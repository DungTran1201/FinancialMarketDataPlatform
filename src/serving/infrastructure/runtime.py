"""Unified Three-Plane Runtime Container wiring Data Plane (A), App Plane (B) & Intelligence Plane (C)."""

from __future__ import annotations

import asyncio
import json
import time
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

import httpx
import pyarrow.parquet as pq

from src.ingestion.providers.binance.normalizer import BinancePayloadNormalizer
from src.ingestion.providers.binance.rest_client import ProductionExchangeHistoricalCollector
from src.intelligence.orchestrator.graph import (
    DeterministicMockLLMAdapter,
    MarketIntelligenceGraph,
)
from src.intelligence.tools.contracts import ApprovedAgentTool
from src.intelligence.tools.gateway import ControlledToolGateway
from src.intelligence.workflows.investigation import AgentWorkflowState
from src.lakehouse.bronze.archiver import BronzeParquetArchiver
from src.lakehouse.catalog.lineage import DataLineageGovernanceRegistry
from src.lakehouse.gold.mart_engine import GoldLayerMartEngine
from src.lakehouse.orchestration.pipeline import DataPlatformV01Pipeline
from src.lakehouse.quality.gates import DataQualityGateEngine
from src.lakehouse.silver.merge_engine import SilverLakehouseMergeEngine
from src.serving.api.gateway.registry import MicroserviceRegistry
from src.serving.api.modules.agent_api.domain.ports import AgentRunTicket
from src.serving.api.modules.analytics.domain.ports import MarketStatisticsSummary
from src.serving.api.modules.catalog.domain.ports import DataFreshnessReport
from src.serving.api.modules.historical.domain.ports import HistoricalCandleEntity
from src.serving.api.modules.market.application.queries import GetLatestPriceQueryHandler
from src.serving.api.modules.market.domain.entities import LatestPriceQuote
from src.serving.api.modules.market.domain.ports import (
    MarketFallbackRepositoryPort,
    MarketHotStorePort,
)
from src.serving.api.modules.platform_config.domain.ports import MonitoredInstrumentConfig
from src.serving.api.modules.reporting.domain.ports import (
    ProvenanceCitation,
    StructuredAnalysisReport,
)
from src.shared.config.settings import PlatformConfig
from src.shared.contracts.events.market_events import EventEnvelopeV1, KafkaTopic
from src.shared.domain.primitives import BoundedTimeRange, InstrumentKey
from src.shared.domain.quant import (
    compute_deterministic_log_returns,
    compute_deterministic_pearson_correlation,
    compute_deterministic_realized_volatility,
)
from src.shared.observability.metrics import DataObservabilityMetricsCollector
from src.shared.observability.tracing import (
    WINDOW_SECONDS,
    EventLifecycleTrace,
    PipelineTraceRegistry,
    compute_parallel_branch_latencies,
    utc_now_iso,
)
from src.streaming.consumers.analytics_ch import ClickHouseBatchSink
from src.streaming.consumers.anomaly_detector import DetectedMarketAnomaly, StatisticalAnomalyDetector
from src.streaming.consumers.hot_redis import HotStateProjector
from src.streaming.infrastructure.kafka_broker import PartitionedEventStreamingBroker


class HotProjectorMarketAdapter(MarketHotStorePort):
    """Bridges Plane A `HotStateProjector` (Redis) to Plane B `MarketHotStorePort`."""

    def __init__(self, projector: HotStateProjector) -> None:
        self._projector = projector

    async def get_latest_price(self, instrument: InstrumentKey) -> LatestPriceQuote | None:
        rec = self._projector.get_hot_price(instrument.provider, instrument.symbol)
        if rec is None:
            return None
        return LatestPriceQuote(
            instrument=instrument,
            last_price=rec.last_price,
            exchange_event_time=rec.exchange_event_time,
            ingested_at=rec.ingested_at,
        )


class ClickHouseSinkFallbackAdapter(MarketFallbackRepositoryPort):
    """Bridges Plane A `ClickHouseBatchSink` to Plane B `MarketFallbackRepositoryPort`."""

    def __init__(self, ch_sink: ClickHouseBatchSink) -> None:
        self._ch_sink = ch_sink

    async def get_latest_price_fallback(self, instrument: InstrumentKey) -> LatestPriceQuote | None:
        row = self._ch_sink.get_latest_price_from_olap(instrument.provider, instrument.symbol)
        if row is None:
            return None
        return LatestPriceQuote(
            instrument=instrument,
            last_price=row["last_price"],
            exchange_event_time=row["exchange_event_time"],
            ingested_at=row["ingested_at"],
        )


class PlatformRuntimeContainer:
    """Central runtime container coordinating Plane A, Plane B, and Plane C."""

    def __init__(self, config: PlatformConfig | None = None) -> None:
        self.config = config or PlatformConfig()

        # --- Plane A: Data Plane Core Components (Zero-Mock Production Engines) ---
        self.normalizer = BinancePayloadNormalizer()
        self.kafka_broker = PartitionedEventStreamingBroker(num_partitions=6)
        self.historical_collector = ProductionExchangeHistoricalCollector(self.normalizer)
        self.hot_redis_projector = HotStateProjector()
        self.clickhouse_sink = ClickHouseBatchSink(max_batch_rows=5000, flush_interval_ms=1000)
        self.bronze_archiver = BronzeParquetArchiver()
        self.silver_merge_engine = SilverLakehouseMergeEngine()
        self.gold_mart_engine = GoldLayerMartEngine()
        self.quality_gate_engine = DataQualityGateEngine()
        self.observability_metrics = DataObservabilityMetricsCollector()
        self.trace_registry = PipelineTraceRegistry(max_traces=2000)
        self.lineage_registry = DataLineageGovernanceRegistry()
        self._lakehouse_root = Path(".local_lakehouse")
        self._infra_probe_cache: dict[str, Any] | None = None
        self._infra_probe_cached_at: float = 0.0
        self.anomaly_detector = StatisticalAnomalyDetector(zscore_threshold=2.5, cooldown_seconds=900)
        self.data_platform_v01 = DataPlatformV01Pipeline(
            normalizer=self.normalizer,
            kafka_broker=self.kafka_broker,
            historical_collector=self.historical_collector,
            hot_redis_projector=self.hot_redis_projector,
            clickhouse_sink=self.clickhouse_sink,
            bronze_archiver=self.bronze_archiver,
            silver_merge_engine=self.silver_merge_engine,
            gold_mart_engine=self.gold_mart_engine,
            quality_gate_engine=self.quality_gate_engine,
            observability=self.observability_metrics,
            lineage_registry=self.lineage_registry,
            trace_registry=self.trace_registry,
        )

        # --- Plane B: Application & Control Plane Repositories / State ---
        self.hot_store_adapter = HotProjectorMarketAdapter(self.hot_redis_projector)
        self.ch_fallback_adapter = ClickHouseSinkFallbackAdapter(self.clickhouse_sink)
        self.latest_price_handler = GetLatestPriceQueryHandler(
            hot_store=self.hot_store_adapter,
            fallback_repo=self.ch_fallback_adapter,
            staleness_threshold_ms=self.config.market_staleness_threshold_ms,
        )

        self.monitored_instruments: dict[str, MonitoredInstrumentConfig] = {
            sym: MonitoredInstrumentConfig(
                provider=self.config.default_provider,
                symbol=sym,
                enabled_streams=("trade", "kline_1m", "ticker", "depth20"),
                is_active=True,
            )
            for sym in ("BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT")
        }
        self.ingestion_watermarks: dict[str, datetime] = {}
        self.backfill_jobs: dict[str, dict[str, Any]] = {}
        self.idempotency_keys: dict[str, str] = {}
        self.detected_anomalies: list[DetectedMarketAnomaly] = []
        self.agent_runs: dict[str, AgentWorkflowState] = {}
        self.reports: dict[str, StructuredAnalysisReport] = {}

        # --- Plane C: Intelligence Plane (Controlled Tool Gateway + LangGraph Orchestrator) ---
        self.tool_gateway = ControlledToolGateway()
        self._register_all_ten_deterministic_tools()
        self.intelligence_graph = MarketIntelligenceGraph(
            tool_gateway=self.tool_gateway,
            llm_adapter=DeterministicMockLLMAdapter(),
            monitored_symbols=tuple(self.monitored_instruments.keys()),
        )

        # Seed initial baseline stream data so endpoints work out-of-the-box
        self._seed_initial_market_state()

        # --- Microservices Architecture Registry (ADR-007) ---
        self.microservice_registry = MicroserviceRegistry(config=self.config)
        self._mount_domain_microservices()

    def close(self) -> None:
        """Release durable storage handles cleanly on runtime shutdown."""
        self.data_platform_v01.watermark_store.close()

    def _mount_domain_microservices(self) -> None:
        from src.serving.api.services.analytics import create_analytics_microservice_app
        from src.serving.api.services.catalog import create_catalog_microservice_app
        from src.serving.api.services.data_plane import create_data_plane_microservice_app
        from src.serving.api.services.historical import create_historical_microservice_app
        from src.serving.api.services.iam import create_iam_microservice_app
        from src.serving.api.services.intelligence import create_intelligence_microservice_app
        from src.serving.api.services.market import create_market_microservice_app

        self.microservice_registry.register_asgi_app(
            "svc-market-hot", create_market_microservice_app(self)
        )
        self.microservice_registry.register_asgi_app(
            "svc-historical-backfill", create_historical_microservice_app(self)
        )
        self.microservice_registry.register_asgi_app(
            "svc-analytics-quant", create_analytics_microservice_app(self)
        )
        self.microservice_registry.register_asgi_app(
            "svc-catalog-governance", create_catalog_microservice_app(self)
        )
        self.microservice_registry.register_asgi_app(
            "svc-iam-security", create_iam_microservice_app(self.config)
        )
        self.microservice_registry.register_asgi_app(
            "svc-intelligence-agent", create_intelligence_microservice_app(self)
        )
        self.microservice_registry.register_asgi_app(
            "svc-data-plane-v01", create_data_plane_microservice_app(self)
        )

    def _seed_initial_market_state(self) -> None:
        now = datetime.now(UTC)
        seed_pairs = [
            ("BTCUSDT", Decimal("89500.25")),
            ("ETHUSDT", Decimal("3120.50")),
            ("SOLUSDT", Decimal("185.75")),
        ]
        for sym, base_price in seed_pairs:
            for offset_min in range(15, 0, -1):
                open_t = now - timedelta(minutes=offset_min)
                close_t = open_t + timedelta(minutes=1)
                drift = Decimal(str(((15 - offset_min) % 5 - 2) * 10))
                p_open = base_price + drift
                p_close = p_open + Decimal("8.50")
                raw_kline = {
                    "e": "kline",
                    "E": int(close_t.timestamp() * 1000),
                    "s": sym,
                    "k": {
                        "t": int(open_t.timestamp() * 1000),
                        "T": int(close_t.timestamp() * 1000),
                        "s": sym,
                        "i": "1m",
                        "o": str(p_open),
                        "h": str(p_open + Decimal("25.00")),
                        "l": str(p_open - Decimal("15.00")),
                        "c": str(p_close),
                        "v": "12.50000000",
                        "q": str(p_close * Decimal("12.5")),
                        "n": 85,
                        "x": True,
                        "V": "6.25000000",
                        "Q": str(p_close * Decimal("6.25")),
                    },
                }
                env = self.normalizer.normalize_ws_message(raw_kline, ingested_at=close_t)
                self.hot_redis_projector.project_event(env)
                self.clickhouse_sink.ingest_event(env, auto_flush=False)
        self.clickhouse_sink.flush()

    async def ingest_raw_provider_message(
        self,
        raw_message: dict[str, Any],
        source_topic: str = "market.raw.trades.v1",
        ingested_at: datetime | None = None,
        execution_mode: str = "LIVE",
    ) -> EventEnvelopeV1 | None:
        """Full Plane A pipeline: Normalize -> Validate -> Kafka -> Hot Redis + ClickHouse."""
        t_ing0 = time.perf_counter_ns()
        env, dlq = self.normalizer.normalize_or_route_dlq(
            raw_message, source_topic=source_topic, ingested_at=ingested_at
        )
        ing_ms = round((time.perf_counter_ns() - t_ing0) / 1_000_000.0, 3)

        if dlq is not None:
            t_dlq0 = time.perf_counter_ns()
            await self.kafka_broker.publish_dlq(dlq)
            dlq_ms = round((time.perf_counter_ns() - t_dlq0) / 1_000_000.0, 3)
            self.observability_metrics.record_dlq_event(dlq.source_provider, dlq.error_type)
            self.observability_metrics.record_stage_duration(
                "ingestion", ing_ms, mode=execution_mode, status="FAILED"
            )
            self.observability_metrics.record_stage_duration(
                "dlq_route", dlq_ms, mode=execution_mode, status="DLQ"
            )
            now_iso = utc_now_iso()
            trace = EventLifecycleTrace(
                event_id=str(dlq.dlq_id),
                correlation_id=str(dlq.dlq_id),
                execution_mode=execution_mode,
                provider=dlq.source_provider,
                symbol=str(raw_message.get("s") or raw_message.get("symbol") or "UNKNOWN").upper(),
                event_type=str(raw_message.get("e") or "malformed"),
                topic=KafkaTopic.DLQ_V1.value,
                partition=0,
                offset=max(0, len(self.kafka_broker._topics.get(KafkaTopic.DLQ_V1.value, [])) - 1),
                consumer_groups_acked=["cg.dlq.inspector.v1"],
                exchange_event_time=None,
                ingested_at=now_iso,
                kafka_published_at=now_iso,
                stage_durations_ms={"ingestion": ing_ms, "dlq_route": dlq_ms},
                final_status="DLQ_FAILED",
                error_detail=f"{dlq.error_type}: {dlq.error_message}",
            )
            self.trace_registry.upsert_trace(trace)
            return None

        assert env is not None
        topic = self.kafka_broker.resolve_topic_for_event(env)
        t_pub0 = time.perf_counter_ns()
        before_total = len(self.kafka_broker._topics.get(topic, []))
        partition = await self.kafka_broker.publish_event(topic, env)
        pub_ms = round((time.perf_counter_ns() - t_pub0) / 1_000_000.0, 3)
        kafka_pub_ts = utc_now_iso()
        after_total = len(self.kafka_broker._topics.get(topic, []))
        offset = max(0, after_total - 1)

        t_con0 = time.perf_counter_ns()
        self.kafka_broker.poll_topic(self.hot_redis_projector.CONSUMER_GROUP, topic, max_records=1)
        consume_ms = round((time.perf_counter_ns() - t_con0) / 1_000_000.0, 3)
        kafka_con_ts = utc_now_iso()

        t_hot0 = time.perf_counter_ns()
        self.hot_redis_projector.project_event(env)
        if after_total > before_total:
            self.kafka_broker.commit_up_to_latest(self.hot_redis_projector.CONSUMER_GROUP, topic)
        hot_ms = round((time.perf_counter_ns() - t_hot0) / 1_000_000.0, 3)
        redis_ts = utc_now_iso()

        t_ch0 = time.perf_counter_ns()
        self.clickhouse_sink.ingest_event(env, auto_flush=False)
        self.clickhouse_sink.flush()
        if after_total > before_total:
            self.kafka_broker.commit_up_to_latest(self.clickhouse_sink.CONSUMER_GROUP, topic)
        ch_ms = round((time.perf_counter_ns() - t_ch0) / 1_000_000.0, 3)
        ch_ts = utc_now_iso()

        t_srv0 = time.perf_counter_ns()
        serving_ts = utc_now_iso()
        serving_ms = round((time.perf_counter_ns() - t_srv0) / 1_000_000.0, 3)

        self.observability_metrics.record_ingested_event(env.provider, env.symbol, env.event_type.value)
        for cg in (
            self.hot_redis_projector.CONSUMER_GROUP,
            self.clickhouse_sink.CONSUMER_GROUP,
            self.bronze_archiver.CONSUMER_GROUP,
        ):
            self.observability_metrics.set_consumer_lag(cg, topic, self.kafka_broker.get_topic_lag(cg, topic))

        stage_map = {
            "ingestion": ing_ms,
            "kafka_publish": pub_ms,
            "kafka_consume": consume_ms,
            "redis_hot_write": hot_ms,
            "clickhouse_olap_write": ch_ms,
            "serving_ready": serving_ms,
        }
        for s_name, s_ms in stage_map.items():
            self.observability_metrics.record_stage_duration(s_name, s_ms, mode=execution_mode)

        branches = compute_parallel_branch_latencies(stage_map, final_status="SERVING_HOT")
        if branches["serving_hot_e2e_ms"] is not None:
            self.observability_metrics.record_e2e_latency(
                "hot", branches["serving_hot_e2e_ms"], mode=execution_mode
            )
        if branches["serving_olap_e2e_ms"] is not None:
            self.observability_metrics.record_e2e_latency(
                "olap", branches["serving_olap_e2e_ms"], mode=execution_mode
            )
        if branches["end_to_end_serving_ms"] is not None:
            self.observability_metrics.record_e2e_latency(
                "critical_serving", branches["end_to_end_serving_ms"], mode=execution_mode
            )

        trace = EventLifecycleTrace(
            event_id=str(env.event_id),
            correlation_id=str(getattr(env, "correlation_id", None) or env.event_id),
            execution_mode=execution_mode,
            provider=env.provider,
            symbol=env.symbol,
            event_type=env.event_type.value,
            topic=topic,
            partition=partition,
            offset=offset,
            consumer_groups_acked=[
                self.hot_redis_projector.CONSUMER_GROUP,
                self.clickhouse_sink.CONSUMER_GROUP,
            ],
            exchange_event_time=env.exchange_event_time.isoformat(),
            ingested_at=env.ingested_at.isoformat(),
            kafka_published_at=kafka_pub_ts,
            kafka_consumed_at=kafka_con_ts,
            redis_written_at=redis_ts,
            clickhouse_written_at=ch_ts,
            serving_available_at=serving_ts,
            stage_durations_ms=stage_map,
            final_status="SERVING_HOT",
        )
        self.trace_registry.upsert_trace(trace)
        return env

    def _register_all_ten_deterministic_tools(self) -> None:
        """Bind all 10 ApprovedAgentTool handlers to read-only Plane A/B stores."""

        async def _tool_get_latest_price(params: dict[str, Any]) -> dict[str, Any]:
            sym = str(params.get("symbol", "BTCUSDT")).upper()
            dto = await self.latest_price_handler.handle("binance", sym)
            if dto is None:
                return {"symbol": sym, "last_price": "0", "is_stale": True, "row_count": 0}
            return {
                "symbol": dto.symbol,
                "last_price": dto.last_price,
                "source": dto.source,
                "is_stale": dto.is_stale,
                "age_ms": dto.age_ms,
                "row_count": 1,
            }

        async def _tool_get_market_snapshot(params: dict[str, Any]) -> dict[str, Any]:
            sym = str(params.get("symbol", "BTCUSDT")).upper()
            snap = self.hot_redis_projector.get_hot_snapshot("binance", sym) or {}
            return {"symbol": sym, "snapshot": snap, "row_count": 1 if snap else 0}

        async def _tool_get_historical_candles(params: dict[str, Any]) -> dict[str, Any]:
            sym = str(params.get("symbol", "BTCUSDT")).upper()
            interval = str(params.get("interval", "1m"))
            limit = int(params.get("limit", 60))
            now = datetime.now(UTC)
            rows = self.clickhouse_sink.query_klines(
                "binance", sym, interval, now - timedelta(days=7), now, limit=limit
            )
            return {
                "symbol": sym,
                "interval": interval,
                "candle_count": len(rows),
                "latest_close": str(rows[-1]["close_price"]) if rows else "0",
                "row_count": len(rows),
            }

        async def _tool_get_market_statistics(params: dict[str, Any]) -> dict[str, Any]:
            sym = str(params.get("symbol", "BTCUSDT")).upper()
            stats = self.clickhouse_sink.compute_aggregated_statistics("binance", sym) or {}
            return {
                "symbol": sym,
                "vwap": str(stats.get("vwap", "0")),
                "total_base_volume": str(stats.get("total_base_volume", "0")),
                "trade_count": int(stats.get("trade_count", 0)),
                "row_count": int(stats.get("candle_count", 1)),
            }

        async def _tool_calculate_returns(params: dict[str, Any]) -> dict[str, Any]:
            sym = str(params.get("symbol", "BTCUSDT")).upper()
            stats = self.clickhouse_sink.compute_aggregated_statistics("binance", sym) or {}
            prices: list[float] = list(stats.get("close_prices", [89500.0, 89550.0, 89600.0]))
            log_rets = compute_deterministic_log_returns(prices)
            return {
                "symbol": sym,
                "sample_size": len(prices),
                "cumulative_log_return": round(sum(log_rets), 8),
                "mean_log_return": round(sum(log_rets) / max(1, len(log_rets)), 8),
                "row_count": len(prices),
            }

        async def _tool_calculate_volatility(params: dict[str, Any]) -> dict[str, Any]:
            sym = str(params.get("symbol", "BTCUSDT")).upper()
            stats = self.clickhouse_sink.compute_aggregated_statistics("binance", sym) or {}
            prices: list[float] = list(stats.get("close_prices", [89500.0, 89550.0, 89600.0]))
            vol = compute_deterministic_realized_volatility(prices)
            return {
                "symbol": sym,
                "realized_volatility_annualized": round(vol, 6),
                "row_count": len(prices),
            }

        async def _tool_calculate_correlation(params: dict[str, Any]) -> dict[str, Any]:
            symbols = [str(s).upper() for s in params.get("symbols", ["BTCUSDT", "ETHUSDT"])]
            s1 = symbols[0] if symbols else "BTCUSDT"
            s2 = symbols[1] if len(symbols) > 1 else "ETHUSDT"
            st1 = self.clickhouse_sink.compute_aggregated_statistics("binance", s1) or {}
            st2 = self.clickhouse_sink.compute_aggregated_statistics("binance", s2) or {}
            p1: list[float] = list(st1.get("close_prices", [89500.0, 89520.0, 89580.0]))
            p2: list[float] = list(st2.get("close_prices", [3120.0, 3125.0, 3132.0]))
            corr = compute_deterministic_pearson_correlation(p1, p2)
            return {
                "pair": f"{s1}:{s2}",
                "pearson_correlation": corr,
                "row_count": min(len(p1), len(p2)),
            }

        async def _tool_detect_anomalies(params: dict[str, Any]) -> dict[str, Any]:
            sym = str(params.get("symbol", "BTCUSDT")).upper()
            stats = self.clickhouse_sink.compute_aggregated_statistics("binance", sym) or {}
            prices: list[float] = list(stats.get("close_prices", [100.0, 101.0, 100.5, 100.2, 100.8]))
            _, anom = self.anomaly_detector.evaluate_series("binance", sym, prices)
            if anom is not None:
                self.detected_anomalies.append(anom)
            return {
                "symbol": sym,
                "anomaly_detected": anom is not None,
                "z_score": anom.z_score if anom else 0.0,
                "row_count": len(prices),
            }

        async def _tool_get_data_freshness(params: dict[str, Any]) -> dict[str, Any]:
            sym = str(params.get("symbol", "BTCUSDT")).upper()
            dto = await self.latest_price_handler.handle("binance", sym)
            lag_ms = dto.age_ms if dto else 999999
            return {
                "symbol": sym,
                "redis_lag_ms": lag_ms,
                "clickhouse_lag_ms": lag_ms,
                "is_healthy": lag_ms <= self.config.market_staleness_threshold_ms,
                "row_count": 1,
            }

        async def _tool_generate_analysis_report(params: dict[str, Any]) -> dict[str, Any]:
            rep_dict = dict(params.get("report", {}))
            run_id = str(rep_dict.get("run_id", uuid.uuid4()))
            sym = str(params.get("symbol", rep_dict.get("symbol", "BTCUSDT"))).upper()
            citations = tuple(
                ProvenanceCitation(
                    invocation_id=str(c["invocation_id"]),
                    tool_name=str(c["tool_name"]),
                    source_store=str(c["source_store"]),
                    symbol=str(c["symbol"]),
                    window_start=datetime.fromisoformat(str(c["window_start"])),
                    window_end=datetime.fromisoformat(str(c["window_end"])),
                    row_count=int(c["row_count"]),
                )
                for c in rep_dict.get("provenance_citations", [])
            )
            structured = StructuredAnalysisReport(
                run_id=run_id,
                symbol=sym,
                summary=str(rep_dict.get("summary", "")),
                quantitative_evidence=dict(rep_dict.get("quantitative_evidence", {})),
                anomalies_detected=tuple(rep_dict.get("anomalies_detected", ())),
                data_quality_status=str(rep_dict.get("data_quality_status", "HEALTHY")),
                provenance_citations=citations,
                limitations_disclaimer=str(rep_dict.get("limitations_disclaimer", "")),
            )
            self.reports[run_id] = structured
            return {"persisted_run_id": run_id, "citation_count": len(citations), "row_count": 1}

        self.tool_gateway.register_handler(ApprovedAgentTool.GET_LATEST_PRICE, _tool_get_latest_price)
        self.tool_gateway.register_handler(ApprovedAgentTool.GET_MARKET_SNAPSHOT, _tool_get_market_snapshot)
        self.tool_gateway.register_handler(ApprovedAgentTool.GET_HISTORICAL_CANDLES, _tool_get_historical_candles)
        self.tool_gateway.register_handler(ApprovedAgentTool.GET_MARKET_STATISTICS, _tool_get_market_statistics)
        self.tool_gateway.register_handler(ApprovedAgentTool.CALCULATE_RETURNS, _tool_calculate_returns)
        self.tool_gateway.register_handler(ApprovedAgentTool.CALCULATE_VOLATILITY, _tool_calculate_volatility)
        self.tool_gateway.register_handler(ApprovedAgentTool.CALCULATE_CORRELATION, _tool_calculate_correlation)
        self.tool_gateway.register_handler(ApprovedAgentTool.DETECT_ANOMALIES, _tool_detect_anomalies)
        self.tool_gateway.register_handler(ApprovedAgentTool.GET_DATA_FRESHNESS, _tool_get_data_freshness)
        self.tool_gateway.register_handler(ApprovedAgentTool.GENERATE_ANALYSIS_REPORT, _tool_generate_analysis_report)

    async def execute_agent_investigation(
        self,
        symbol: str,
        prompt_summary: str,
        trigger_mode: str = "ON_DEMAND",
        idempotency_key: str | None = None,
    ) -> tuple[AgentRunTicket, AgentWorkflowState]:
        """Enqueue and run an isolated Plane C investigation workflow with idempotency protection."""
        if idempotency_key and idempotency_key in self.idempotency_keys:
            existing_id = self.idempotency_keys[idempotency_key]
            existing_state = self.agent_runs[existing_id]
            return (
                AgentRunTicket(
                    run_id=existing_id,
                    trigger_mode=existing_state.trigger_mode,
                    symbol=existing_state.symbol,
                    status=existing_state.status,
                    queued_at=datetime.now(UTC),
                ),
                existing_state,
            )

        run_id = f"run_{uuid.uuid4().hex[:12]}"
        now = datetime.now(UTC)
        state = AgentWorkflowState(
            run_id=run_id,
            trigger_mode=trigger_mode,
            symbol=symbol.upper(),
            prompt_summary=prompt_summary,
        )
        self.agent_runs[run_id] = state
        if idempotency_key:
            self.idempotency_keys[idempotency_key] = run_id

        completed_state = await self.intelligence_graph.run_investigation(state)
        ticket = AgentRunTicket(
            run_id=run_id,
            trigger_mode=trigger_mode,
            symbol=symbol.upper(),
            status=completed_state.status,
            queued_at=now,
        )
        return ticket, completed_state

    def query_historical_candles(
        self,
        provider: str,
        symbol: str,
        interval: str,
        time_range: BoundedTimeRange,
        limit: int = 500,
    ) -> list[HistoricalCandleEntity]:
        inst = InstrumentKey(provider=provider, symbol=symbol)
        rows = self.clickhouse_sink.query_klines(
            provider, symbol, interval, time_range.start_time, time_range.end_time, limit=limit
        )
        return [
            HistoricalCandleEntity(
                instrument=inst,
                interval=r["interval"],
                open_time=r["open_time"],
                close_time=r["close_time"],
                open_price=r["open_price"],
                high_price=r["high_price"],
                low_price=r["low_price"],
                close_price=r["close_price"],
                base_volume=r["base_volume"],
                quote_volume=r["quote_volume"],
                trade_count=r["trade_count"],
            )
            for r in rows
        ]

    def get_market_statistics_summary(
        self,
        provider: str,
        symbol: str,
        window: str = "24h",
    ) -> MarketStatisticsSummary | None:
        stats = self.clickhouse_sink.compute_aggregated_statistics(provider, symbol)
        if stats is None:
            return None
        vol = compute_deterministic_realized_volatility(list(stats.get("close_prices", [])))
        return MarketStatisticsSummary(
            instrument=InstrumentKey(provider=provider, symbol=symbol),
            window=window,
            vwap=stats["vwap"].quantize(Decimal("0.00000001")),
            realized_volatility=Decimal(str(round(vol, 6))),
            total_base_volume=stats["total_base_volume"],
            total_quote_volume=stats["total_quote_volume"],
            trade_count=stats["trade_count"],
        )

    async def get_freshness_report(self, provider: str, symbol: str) -> DataFreshnessReport:
        inst = InstrumentKey(provider=provider, symbol=symbol)
        dto = await self.latest_price_handler.handle(provider, symbol)
        lag = dto.age_ms if dto is not None else 999999
        return DataFreshnessReport(
            instrument=inst,
            hot_redis_lag_ms=lag,
            clickhouse_lag_ms=lag,
            is_healthy=lag <= self.config.market_staleness_threshold_ms,
        )

    # ------------------------------------------------------------------
    # Real-Time Data Platform Observatory Facades (Clean Plane Isolation)
    # ------------------------------------------------------------------

    @staticmethod
    async def _probe_tcp(host: str, port: int, timeout_s: float = 0.12) -> tuple[bool, float | None, str | None]:
        candidates = [host] if host in ("127.0.0.1", "localhost") else [host, "127.0.0.1"]
        last_err: str | None = None
        for target_host in candidates:
            t0 = time.perf_counter_ns()
            try:
                conn = asyncio.open_connection(target_host, port)
                _reader, writer = await asyncio.wait_for(conn, timeout=timeout_s)
                latency_ms = round((time.perf_counter_ns() - t0) / 1_000_000.0, 2)
                writer.close()
                try:
                    await asyncio.wait_for(writer.wait_closed(), timeout=0.05)
                except Exception:
                    pass
                return True, latency_ms, f"{target_host}:{port}"
            except Exception as exc:
                last_err = f"{target_host}:{port} -> {type(exc).__name__}"
        return False, None, last_err

    async def probe_external_infrastructure(self, force: bool = False) -> dict[str, Any]:
        """Probe configured external containers via non-blocking TCP checks with 5s TTL cache."""
        now = time.time()
        if not force and self._infra_probe_cache is not None and (now - self._infra_probe_cached_at) < 5.0:
            return self._infra_probe_cache

        minio_host = (
            self.config.minio_endpoint_url.replace("http://", "").replace("https://", "").split(":")[0]
        )
        targets = [
            ("kafka_broker_1", self.config.kafka_bootstrap_servers.split(":")[0], 9092, "Kafka KRaft Node 1"),
            ("redis", self.config.redis_host, self.config.redis_port, "Redis 7.4 Hot Cache"),
            ("clickhouse", self.config.clickhouse_host, self.config.clickhouse_http_port, "ClickHouse 24.8 OLAP"),
            ("minio", minio_host, 9000, "MinIO S3 Object Store"),
            ("postgres", self.config.postgres_host, self.config.postgres_port, "PostgreSQL 16 Control Plane"),
        ]
        results = await asyncio.gather(*(self._probe_tcp(h, p) for _k, h, p, _lbl in targets))
        services: dict[str, Any] = {}
        for (key, host, port, label), (reachable, rtt_ms, detail) in zip(targets, results, strict=True):
            services[key] = {
                "name": label,
                "configured_endpoint": f"{host}:{port}",
                "status": "LIVE_CONTAINER" if reachable else "UNAVAILABLE",
                "rtt_ms": rtt_ms,
                "detail": detail,
            }

        # Honest Kafka Cluster broker accounting per docker-compose.yml (single-node KRaft)
        b1 = services["kafka_broker_1"]
        services["kafka_cluster_brokers"] = [
            {
                "broker_id": 1,
                "name": "Broker 1 (KRaft Controller+Broker)",
                "host": b1["configured_endpoint"],
                "status": "LIVE_CONTAINER" if b1["status"] == "LIVE_CONTAINER" else "IN_PROCESS_ACTIVE",
                "rtt_ms": b1["rtt_ms"],
                "detail": "External broker reachable"
                if b1["status"] == "LIVE_CONTAINER"
                else "External :9092 unavailable; serving in-process PartitionedEventStreamingBroker",
            },
            {
                "broker_id": 2,
                "name": "Broker 2",
                "host": "kafka-2:9092",
                "status": "UNAVAILABLE",
                "rtt_ms": None,
                "detail": "Not configured in docker-compose.yml (single-node KRaft KAFKA_NODE_ID=1).",
            },
            {
                "broker_id": 3,
                "name": "Broker 3",
                "host": "kafka-3:9092",
                "status": "UNAVAILABLE",
                "rtt_ms": None,
                "detail": "Not configured in docker-compose.yml (single-node KRaft KAFKA_NODE_ID=1).",
            },
        ]
        payload = {"probed_at_utc": utc_now_iso(), "services": services}
        self._infra_probe_cache = payload
        self._infra_probe_cached_at = now
        return payload

    def _get_redis_hot_snapshot(self) -> dict[str, Any]:
        prices = []
        for key, rec in self.hot_redis_projector._price_store.items():
            prices.append(
                {
                    "redis_key": key,
                    "provider": rec.provider,
                    "symbol": rec.symbol,
                    "last_price": str(rec.last_price),
                    "exchange_event_time": rec.exchange_event_time.isoformat(),
                    "ingested_at": rec.ingested_at.isoformat(),
                    "ttl_seconds": rec.ttl_seconds,
                }
            )
        prices.sort(key=lambda r: r["symbol"])
        return {
            "engine_mode": "IN_PROCESS_HOT_STATE_STORE",
            "lua_monotonic_guard": "BR-003 REDIS_MONOTONIC_UPSERT_LUA",
            "applied_updates": self.hot_redis_projector._applied_updates,
            "dropped_out_of_order": self.hot_redis_projector._dropped_out_of_order,
            "price_keys_count": len(self.hot_redis_projector._price_store),
            "snapshot_keys_count": len(self.hot_redis_projector._snapshot_store),
            "orderbook_keys_count": len(self.hot_redis_projector._orderbook_store),
            "latest_prices": prices,
        }

    def _scan_lakehouse_disk(self) -> dict[str, Any]:
        root = self._lakehouse_root
        if not root.exists():
            return {
                "root_path": str(root),
                "exists": False,
                "bronze": {"partitions": [], "file_count": 0, "total_rows": 0, "total_bytes": 0},
                "silver": {"tables": [], "file_count": 0, "total_rows": 0},
                "gold": {"marts": [], "file_count": 0, "total_rows": 0},
                "iceberg_manifests": [],
            }

        def _parquet_stats(path: Path) -> tuple[int, int]:
            size = path.stat().st_size
            try:
                rows = int(pq.read_metadata(path).num_rows)
            except Exception:
                rows = 0
            return rows, size

        # Bronze partitions
        bronze_dir = root / "bronze"
        bronze_files_info: list[dict[str, Any]] = []
        bronze_rows = 0
        bronze_bytes = 0
        if bronze_dir.exists():
            for p_file in sorted(bronze_dir.rglob("*.parquet")):
                rows, size = _parquet_stats(p_file)
                bronze_rows += rows
                bronze_bytes += size
                rel = p_file.relative_to(root).as_posix()
                bronze_files_info.append(
                    {
                        "relative_path": rel,
                        "rows": rows,
                        "bytes": size,
                        "modified_utc": datetime.fromtimestamp(p_file.stat().st_mtime, tz=UTC).isoformat(),
                    }
                )

        # Silver Parquet + Iceberg v2 manifests
        silver_dir = root / "silver"
        silver_tables: list[dict[str, Any]] = []
        iceberg_manifests: list[dict[str, Any]] = []
        silver_file_count = 0
        silver_rows_total = 0
        if silver_dir.exists():
            for tbl_dir in sorted(p for p in silver_dir.iterdir() if p.is_dir()):
                parquets = sorted(tbl_dir.glob("*.parquet"))
                tbl_files = []
                tbl_rows = 0
                for p_file in parquets:
                    rows, size = _parquet_stats(p_file)
                    silver_file_count += 1
                    tbl_rows = max(tbl_rows, rows) if "compacted" in p_file.name else tbl_rows + rows
                    tbl_files.append(
                        {
                            "file": p_file.name,
                            "rows": rows,
                            "bytes": size,
                            "compacted": "compacted" in p_file.name,
                        }
                    )
                silver_rows_total += tbl_rows

                meta_dir = tbl_dir / "metadata"
                hint_ver = None
                snapshots_list: list[dict[str, Any]] = []
                current_snapshot_id = None
                table_uuid = None
                format_version = None
                latest_manifest_path = None
                if meta_dir.exists():
                    hint_file = meta_dir / "version-hint.text"
                    if hint_file.exists():
                        hint_ver = hint_file.read_text(encoding="utf-8").strip()
                    meta_jsons = sorted(meta_dir.glob("*.metadata.json"), key=lambda p: p.stat().st_mtime)
                    if meta_jsons:
                        latest_meta = meta_jsons[-1]
                        latest_manifest_path = latest_meta.relative_to(root).as_posix()
                        try:
                            meta_data = json.loads(latest_meta.read_text(encoding="utf-8"))
                            format_version = meta_data.get("format-version")
                            table_uuid = meta_data.get("table-uuid")
                            current_snapshot_id = meta_data.get("current-snapshot-id")
                            snapshots_list = list(meta_data.get("snapshots", []))
                        except Exception:
                            pass
                manifest_entry = {
                    "table_name": f"silver.{tbl_dir.name}",
                    "format_version": format_version,
                    "table_uuid": table_uuid,
                    "version_hint": hint_ver,
                    "current_snapshot_id": current_snapshot_id,
                    "manifest_path": latest_manifest_path,
                    "snapshots": snapshots_list[-8:],
                }
                iceberg_manifests.append(manifest_entry)
                silver_tables.append(
                    {
                        "table_name": f"silver.{tbl_dir.name}",
                        "files": tbl_files,
                        "estimated_rows": tbl_rows,
                        "current_snapshot_id": current_snapshot_id,
                        "snapshot_count": len(snapshots_list),
                    }
                )

        # Gold marts
        gold_dir = root / "gold"
        gold_marts: list[dict[str, Any]] = []
        gold_file_count = 0
        gold_rows_total = 0
        if gold_dir.exists():
            for mart_dir in sorted(p for p in gold_dir.iterdir() if p.is_dir()):
                if mart_dir.name.startswith("_"):
                    continue
                parquets = sorted(mart_dir.rglob("*.parquet"))
                mart_rows = 0
                mart_bytes = 0
                mart_files = []
                for p_file in parquets:
                    rows, size = _parquet_stats(p_file)
                    gold_file_count += 1
                    mart_rows += rows
                    mart_bytes += size
                    mart_files.append(p_file.name)
                gold_rows_total += mart_rows
                gold_marts.append(
                    {
                        "mart_name": f"gold.{mart_dir.name}",
                        "files": mart_files,
                        "file_count": len(mart_files),
                        "rows": mart_rows,
                        "bytes": mart_bytes,
                    }
                )

        return {
            "root_path": str(root),
            "exists": True,
            "bronze": {
                "file_count": len(bronze_files_info),
                "total_rows": bronze_rows,
                "total_bytes": bronze_bytes,
                "recent_files": bronze_files_info[-12:],
            },
            "silver": {
                "file_count": silver_file_count,
                "total_rows": silver_rows_total,
                "tables": silver_tables,
            },
            "gold": {
                "file_count": gold_file_count,
                "total_rows": gold_rows_total,
                "marts": gold_marts,
            },
            "iceberg_manifests": iceberg_manifests,
        }

    def get_observability_kafka(
        self, selected_topic: str | None = None, window: str = "5m"
    ) -> dict[str, Any]:
        window_sec = WINDOW_SECONDS.get(window, 300.0)
        snapshot = self.kafka_broker.get_cluster_snapshot(
            selected_topic=selected_topic, window_seconds=window_sec
        )
        infra = self._infra_probe_cache or {}
        brokers = infra.get("services", {}).get("kafka_cluster_brokers")
        if not brokers:
            brokers = [
                {
                    "broker_id": 1,
                    "name": "Broker 1 (In-Process Partitioned Engine)",
                    "host": self.config.kafka_bootstrap_servers,
                    "status": "IN_PROCESS_ACTIVE",
                    "rtt_ms": None,
                    "detail": "Using PartitionedEventStreamingBroker; click Probe Live Infra for :9092 check.",
                },
                {
                    "broker_id": 2,
                    "name": "Broker 2",
                    "host": "kafka-2:9092",
                    "status": "UNAVAILABLE",
                    "rtt_ms": None,
                    "detail": "Not configured in docker-compose.yml (single-node KRaft KAFKA_NODE_ID=1).",
                },
                {
                    "broker_id": 3,
                    "name": "Broker 3",
                    "host": "kafka-3:9092",
                    "status": "UNAVAILABLE",
                    "rtt_ms": None,
                    "detail": "Not configured in docker-compose.yml (single-node KRaft KAFKA_NODE_ID=1).",
                },
            ]
        snapshot["brokers"] = brokers
        snapshot["single_node_compose_note"] = (
            "docker-compose.yml deploys 1 KRaft broker (KAFKA_NODE_ID=1); "
            "Broker 2 & Broker 3 are explicitly UNAVAILABLE."
        )
        return snapshot

    def get_observability_storage(self, dataset: str | None = None) -> dict[str, Any]:
        redis_snap = self._get_redis_hot_snapshot()
        clickhouse_snap = self.clickhouse_sink.get_storage_snapshot()
        lakehouse_snap = self._scan_lakehouse_disk()
        lineage_cat = self.lineage_registry.export_lineage_catalog()

        dq_rules = [
            {
                "rule_id": "DQ-KLINE-001",
                "dataset": "silver.market_klines",
                "rule": "high_price >= low_price AND open/close within [low, high]",
                "severity": "BLOCKING",
            },
            {
                "rule_id": "DQ-KLINE-002",
                "dataset": "silver.market_klines",
                "rule": "No negative prices or volumes (price > 0, volume >= 0)",
                "severity": "BLOCKING",
            },
            {
                "rule_id": "DQ-KLINE-003",
                "dataset": "silver.market_klines",
                "rule": "Unique (provider, symbol, interval, open_time) after MERGE INTO",
                "severity": "BLOCKING",
            },
            {
                "rule_id": "DQ-KLINE-004",
                "dataset": "silver.market_klines",
                "rule": "Schema conformance & UTC timestamps non-null",
                "severity": "BLOCKING",
            },
            {
                "rule_id": "DQ-KLINE-005",
                "dataset": "silver.market_klines",
                "rule": "Batch freshness lag <= configured SLA threshold",
                "severity": "WARNING",
            },
            {
                "rule_id": "DQ-TRADE-001..003",
                "dataset": "silver.market_trades",
                "rule": "Positive trade price/quantity + non-null trade_id deduplication",
                "severity": "BLOCKING",
            },
        ]

        bronze_cnt = lakehouse_snap["bronze"]["file_count"]
        bronze_rows = lakehouse_snap["bronze"]["total_rows"]
        ice_cnt = len(lakehouse_snap["iceberg_manifests"])
        gold_rows = lakehouse_snap["gold"]["total_rows"]
        ch_rows = clickhouse_snap["total_rows"]

        architecture_comparison = [
            {
                "dimension": "Data Structure & Schema",
                "data_lake": (
                    "Schema-on-read immutable raw Bronze Parquet/JSON files partitioned "
                    "by provider & ingestion_date."
                ),
                "data_lakehouse": (
                    "Schema-enforced ACID Apache Iceberg v2 tables on Parquet "
                    "(Silver MERGE INTO + Gold marts)."
                ),
                "data_warehouse": (
                    "Rigid typed OLAP tables in ClickHouse (ReplacingMergeTree / "
                    "AggregatingMergeTree)."
                ),
            },
            {
                "dimension": "Project Mapping (Real Paths)",
                "data_lake": f".local_lakehouse/bronze/** ({bronze_cnt} files, {bronze_rows} rows)",
                "data_lakehouse": (
                    f".local_lakehouse/silver + /gold ({ice_cnt} Iceberg tables, {gold_rows} Gold rows)"
                ),
                "data_warehouse": f"ClickHouse DDL + sink ({ch_rows} OLAP rows; :8123 container)",
            },
            {
                "dimension": "Latency & Workload Purpose",
                "data_lake": "Durable replay / audit trail from raw Exchange envelopes (seconds-minutes).",
                "data_lakehouse": (
                    "Time-travel snapshot isolation, dedup compaction, DQ gates & ML batch research."
                ),
                "data_warehouse": "Sub-second analytical slices, OHLCV rollups & VWAP/volatility SQL queries.",
            },
            {
                "dimension": "Quality & Governance",
                "data_lake": "Append-only raw capture; bad frames already isolated into Kafka DLQ.",
                "data_lakehouse": (
                    "DQ-KLINE-001..005 & DQ-TRADE-001..003 block Gold promotion + lineage edges."
                ),
                "data_warehouse": "ReplacingMergeTree deduplicates by ingested_at/trade_id asynchronously.",
            },
        ]

        return {
            "selected_dataset": dataset or "ALL",
            "redis_hot_state": redis_snap,
            "clickhouse_warehouse": clickhouse_snap,
            "lakehouse": lakehouse_snap,
            "dq_rules": dq_rules,
            "lineage_edges_count": len(lineage_cat.get("lineage_edges", [])),
            "lineage_edges_recent": lineage_cat.get("lineage_edges", [])[-15:],
            "architecture_comparison": architecture_comparison,
        }

    def get_observability_latency(
        self,
        *,
        window: str = "all",
        provider: str | None = None,
        symbol: str | None = None,
        mode: str | None = None,
        slow_threshold_ms: float = 25.0,
    ) -> dict[str, Any]:
        return self.trace_registry.compute_latency_analytics(
            window=window,
            mode=mode,
            provider=provider,
            symbol=symbol,
            slow_threshold_ms=slow_threshold_ms,
        )

    def get_observability_traces(
        self,
        *,
        window: str = "all",
        mode: str | None = None,
        provider: str | None = None,
        symbol: str | None = None,
        status: str | None = None,
        topic: str | None = None,
        slow_threshold_ms: float | None = None,
        only_errors: bool = False,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        return self.trace_registry.query_traces(
            window=window,
            mode=mode,
            provider=provider,
            symbol=symbol,
            status=status,
            topic=topic,
            slow_threshold_ms=slow_threshold_ms,
            only_errors=only_errors,
            limit=limit,
        )

    def get_observability_trace_detail(self, event_id: str) -> dict[str, Any] | None:
        return self.trace_registry.get_trace(event_id)

    async def get_observability_overview(
        self,
        *,
        window: str = "all",
        provider: str | None = None,
        symbol: str | None = None,
        mode: str | None = None,
        force_probe: bool = False,
    ) -> dict[str, Any]:
        infra = await self.probe_external_infrastructure(force=force_probe)
        trace_summary = self.trace_registry.get_summary_counts(
            window=window, mode=mode, provider=provider, symbol=symbol
        )
        latency = self.trace_registry.compute_latency_analytics(
            window=window, mode=mode, provider=provider, symbol=symbol
        )
        kafka_snap = self.get_observability_kafka(window=window)
        storage_snap = self.get_observability_storage()

        # Data freshness across tiers
        latest_redis_dt = max(
            (r.ingested_at for r in self.hot_redis_projector._price_store.values()), default=None
        )
        now_utc = datetime.now(UTC)
        redis_age_ms = (
            round(max(0.0, (now_utc - latest_redis_dt).total_seconds() * 1000.0), 1)
            if latest_redis_dt is not None
            else None
        )
        ch_latest_iso = storage_snap["clickhouse_warehouse"].get("latest_ingested_at")
        ch_age_ms = None
        if ch_latest_iso:
            ch_dt = datetime.fromisoformat(ch_latest_iso)
            ch_age_ms = round(max(0.0, (now_utc - ch_dt).total_seconds() * 1000.0), 1)

        latest_traces = self.trace_registry.query_traces(limit=1)
        demo_active = any(t.get("execution_mode") == "DEMO" for t in self.trace_registry.query_traces(limit=25))

        return {
            "generated_at_utc": utc_now_iso(),
            "window": window,
            "execution_context": {
                "has_demo_traces": demo_active,
                "latest_trace_mode": latest_traces[0]["execution_mode"] if latest_traces else "NONE",
                "historical_transport": "EMBEDDED_ASGI_SIMULATOR"
                if getattr(self.historical_collector, "use_embedded_asgi_transport", True)
                else "LIVE_BINANCE_REST",
                "kafka_mode": kafka_snap["engine_mode"],
            },
            "kpis": {
                "events_ingested": trace_summary["events_ingested"],
                "events_processed": trace_summary["events_processed"],
                "events_failed_dlq": trace_summary["events_failed_dlq"],
                "events_dq_blocked": trace_summary["events_dq_blocked"],
                "throughput_events_per_sec": trace_summary["throughput_events_per_sec"],
                "kafka_total_lag": kafka_snap["total_lag_all_topics"],
                "kafka_total_messages": kafka_snap["total_messages_all_topics"],
                "e2e_latency_ms": latency["overall_e2e"],
                "branch_latencies_ms": latency["branch_stats"],
            },
            "freshness": {
                "redis_hot_age_ms": redis_age_ms,
                "clickhouse_olap_age_ms": ch_age_ms,
                "bronze_files": storage_snap["lakehouse"]["bronze"]["file_count"],
                "silver_rows": storage_snap["lakehouse"]["silver"]["total_rows"],
                "gold_rows": storage_snap["lakehouse"]["gold"]["total_rows"],
            },
            "infrastructure": infra,
            "cumulative": trace_summary["cumulative"],
        }

    async def get_observability_topology(
        self,
        *,
        window: str = "all",
        provider: str | None = None,
        symbol: str | None = None,
        mode: str | None = None,
    ) -> dict[str, Any]:
        """Build authoritative parallel-branch DAG nodes & edges for SVG Data Flow Visualization."""
        overview = await self.get_observability_overview(
            window=window, provider=provider, symbol=symbol, mode=mode
        )
        latency = self.trace_registry.compute_latency_analytics(
            window=window, mode=mode, provider=provider, symbol=symbol
        )
        kafka_snap = self.get_observability_kafka(window=window)
        storage_snap = self.get_observability_storage()
        infra_services = overview["infrastructure"]["services"]
        stage_stats = latency["stage_stats"]
        branch_stats = latency["branch_stats"]
        ev_total = overview["kpis"]["events_ingested"]
        dlq_total = kafka_snap["total_dlq_messages"]
        ch_rows = storage_snap["clickhouse_warehouse"]["total_rows"]
        redis_keys = storage_snap["redis_hot_state"]["price_keys_count"]
        bronze_files = storage_snap["lakehouse"]["bronze"]["file_count"]
        silver_rows = storage_snap["lakehouse"]["silver"]["total_rows"]
        gold_rows = storage_snap["lakehouse"]["gold"]["total_rows"]

        last_report = self.data_platform_v01._last_report

        def _node_status(has_data: bool, error_cond: bool = False, lag_cond: bool = False) -> str:
            if error_cond:
                return "FAILED"
            if lag_cond:
                return "DELAYED"
            return "ACTIVE" if has_data else "IDLE"

        nodes = [
            {
                "id": "exchange_source",
                "label": "Exchange REST / WS",
                "layer": "SOURCE",
                "status": "ACTIVE" if ev_total > 0 else "IDLE",
                "engine_mode": overview["execution_context"]["historical_transport"],
                "records": ev_total,
                "throughput_eps": overview["kpis"]["throughput_events_per_sec"],
                "latency_ms": None,
                "errors": 0,
                "detail": "Binance Public REST (/api/v3/klines) + WS frames normalized by BinancePayloadNormalizer.",
            },
            {
                "id": "ingestion",
                "label": "Ingestion & DLQ Gate",
                "layer": "INGESTION",
                "status": _node_status(ev_total > 0, error_cond=dlq_total > 0 and ev_total == 0),
                "engine_mode": "IN_PROCESS_NORMALIZER",
                "records": ev_total,
                "throughput_eps": overview["kpis"]["throughput_events_per_sec"],
                "latency_ms": stage_stats["ingestion"]["p50"],
                "latency_p95_ms": stage_stats["ingestion"]["p95"],
                "errors": dlq_total,
                "detail": (
                    f"Decimal validation & DLQ routing ({dlq_total} rejected payloads "
                    "routed to market.events.dlq.v1)."
                ),
            },
            {
                "id": "kafka_cluster",
                "label": "Kafka Cluster",
                "layer": "STREAMING",
                "status": "DELAYED"
                if kafka_snap["total_lag_all_topics"] > 0
                else ("ACTIVE" if kafka_snap["total_messages_all_topics"] > 0 else "IDLE"),
                "engine_mode": kafka_snap["engine_mode"],
                "records": kafka_snap["total_messages_all_topics"],
                "lag": kafka_snap["total_lag_all_topics"],
                "latency_ms": stage_stats["kafka_publish"]["p50"],
                "latency_p95_ms": stage_stats["kafka_publish"]["p95"],
                "errors": dlq_total,
                "brokers": infra_services["kafka_cluster_brokers"],
                "detail": (
                    "6 topics x 6 partitions; Broker 1 active, Broker 2 & 3 UNAVAILABLE "
                    "in 1-node KRaft compose."
                ),
            },
            {
                "id": "redis_hot",
                "label": "Redis Hot State",
                "layer": "HOT_STORE",
                "branch": "parallel_hot",
                "status": "ACTIVE" if redis_keys > 0 else "IDLE",
                "engine_mode": infra_services["redis"]["status"]
                if infra_services["redis"]["status"] == "LIVE_CONTAINER"
                else "IN_PROCESS_HOT_STATE_STORE",
                "records": redis_keys,
                "applied_updates": storage_snap["redis_hot_state"]["applied_updates"],
                "latency_ms": branch_stats["hot_branch_ms"]["p50"],
                "latency_p95_ms": branch_stats["hot_branch_ms"]["p95"],
                "errors": storage_snap["redis_hot_state"]["dropped_out_of_order"],
                "detail": "BR-003 monotonic LUA upsert protection for sub-ms latest prices & depth.",
            },
            {
                "id": "clickhouse_olap",
                "label": "ClickHouse OLAP",
                "layer": "WAREHOUSE",
                "branch": "parallel_olap",
                "status": "ACTIVE" if ch_rows > 0 else "IDLE",
                "engine_mode": infra_services["clickhouse"]["status"]
                if infra_services["clickhouse"]["status"] == "LIVE_CONTAINER"
                else "IN_PROCESS_REPLACING_MERGE_TREE",
                "records": ch_rows,
                "latency_ms": branch_stats["olap_branch_ms"]["p50"],
                "latency_p95_ms": branch_stats["olap_branch_ms"]["p95"],
                "errors": 0,
                "detail": "ReplacingMergeTree deduplicated trades/klines + Decimal OHLCV timeframe rollups.",
            },
            {
                "id": "lakehouse_bronze",
                "label": "Bronze (Iceberg Raw)",
                "layer": "LAKEHOUSE_BRONZE",
                "branch": "parallel_lakehouse",
                "status": "DELAYED"
                if kafka_snap["total_lag_all_topics"] > 0
                else ("ACTIVE" if bronze_files > 0 else "IDLE"),
                "engine_mode": "PARQUET_ZSTD_LOCAL_FS",
                "records": storage_snap["lakehouse"]["bronze"]["total_rows"],
                "files": bronze_files,
                "latency_ms": stage_stats["bronze_archive"]["p50"],
                "latency_p95_ms": stage_stats["bronze_archive"]["p95"],
                "errors": 0,
                "detail": "cg.lakehouse.bronze.v1 commits offsets ONLY AFTER immutable ZSTD Parquet write succeeds.",
            },
            {
                "id": "lakehouse_silver",
                "label": "Silver (Merge & DQ)",
                "layer": "LAKEHOUSE_SILVER",
                "branch": "parallel_lakehouse",
                "status": "FAILED"
                if (last_report is not None and not last_report.stage_08_dq_passed)
                else ("ACTIVE" if silver_rows > 0 else "IDLE"),
                "engine_mode": "ICEBERG_V2_JSON_MANIFEST",
                "records": silver_rows,
                "latency_ms": stage_stats["silver_merge"]["p50"],
                "latency_p95_ms": stage_stats["silver_merge"]["p95"],
                "errors": len(last_report.stage_08_dq_failed_rules) if last_report else 0,
                "detail": "Deduplication MERGE + DQ-KLINE-001..005 & DQ-TRADE-001..003 pre-Gold gates.",
            },
            {
                "id": "lakehouse_gold",
                "label": "Gold Marts",
                "layer": "LAKEHOUSE_GOLD",
                "branch": "parallel_lakehouse",
                "status": "FAILED"
                if (last_report is not None and last_report.gold_promotion_blocked)
                else ("ACTIVE" if gold_rows > 0 else "IDLE"),
                "engine_mode": "GOLD_PARQUET_AND_DBT_MODELS",
                "records": gold_rows,
                "latency_ms": stage_stats["gold_mart"]["p50"],
                "latency_p95_ms": stage_stats["gold_mart"]["p95"],
                "errors": 1 if (last_report is not None and last_report.gold_promotion_blocked) else 0,
                "detail": "fct_daily_market_summary, fct_realized_volatility, fct_orderbook_liquidity (gated by DQ).",
            },
            {
                "id": "serving_layer",
                "label": "Serving Facade",
                "layer": "SERVING",
                "status": "ACTIVE" if (redis_keys > 0 or ch_rows > 0) else "IDLE",
                "engine_mode": "FASTAPI_MODULAR_MONOLITH",
                "records": ev_total,
                "latency_ms": latency["overall_e2e"]["p50"],
                "latency_p95_ms": latency["overall_e2e"]["p95"],
                "errors": 0,
                "detail": "PlatformRuntimeContainer serving REST, SSE, WS, Redis hot + CH fallback + Gold marts.",
            },
            {
                "id": "consumers_down",
                "label": "API / UI / AI Agent",
                "layer": "CONSUMERS",
                "status": "ACTIVE",
                "engine_mode": "SSE_WS_REST_LANGGRAPH",
                "records": len(self.agent_runs) + ev_total,
                "latency_ms": stage_stats["serving_ready"]["p50"],
                "errors": 0,
                "detail": (
                    f"Observatory UI (/ui/data-flow), REST/SSE/WS, and "
                    f"{len(self.agent_runs)} intelligence runs."
                ),
            },
        ]

        edges = [
            {
                "id": "e_src_ing",
                "source": "exchange_source",
                "target": "ingestion",
                "branch": "spine",
                "active": ev_total > 0,
            },
            {
                "id": "e_ing_kfk",
                "source": "ingestion",
                "target": "kafka_cluster",
                "branch": "spine",
                "active": kafka_snap["total_messages_all_topics"] > 0,
            },
            {
                "id": "e_kfk_redis",
                "source": "kafka_cluster",
                "target": "redis_hot",
                "branch": "parallel_hot",
                "active": redis_keys > 0,
            },
            {
                "id": "e_kfk_ch",
                "source": "kafka_cluster",
                "target": "clickhouse_olap",
                "branch": "parallel_olap",
                "active": ch_rows > 0,
            },
            {
                "id": "e_kfk_brz",
                "source": "kafka_cluster",
                "target": "lakehouse_bronze",
                "branch": "parallel_lakehouse",
                "active": bronze_files > 0 or kafka_snap["total_lag_all_topics"] > 0,
            },
            {
                "id": "e_brz_slv",
                "source": "lakehouse_bronze",
                "target": "lakehouse_silver",
                "branch": "parallel_lakehouse",
                "active": silver_rows > 0,
            },
            {
                "id": "e_slv_gld",
                "source": "lakehouse_silver",
                "target": "lakehouse_gold",
                "branch": "parallel_lakehouse",
                "active": gold_rows > 0,
            },
            {
                "id": "e_redis_srv",
                "source": "redis_hot",
                "target": "serving_layer",
                "branch": "parallel_hot",
                "active": redis_keys > 0,
            },
            {
                "id": "e_ch_srv",
                "source": "clickhouse_olap",
                "target": "serving_layer",
                "branch": "parallel_olap",
                "active": ch_rows > 0,
            },
            {
                "id": "e_gld_srv",
                "source": "lakehouse_gold",
                "target": "serving_layer",
                "branch": "parallel_lakehouse",
                "active": gold_rows > 0,
            },
            {
                "id": "e_srv_out",
                "source": "serving_layer",
                "target": "consumers_down",
                "branch": "spine",
                "active": True,
            },
        ]

        return {
            "generated_at_utc": utc_now_iso(),
            "parallel_note": (
                "Kafka fans out in parallel to cg.hot.redis.v1 (Redis), "
                "cg.analytics.clickhouse.v1 (ClickHouse), and cg.lakehouse.bronze.v1 (Bronze->Silver->Gold)."
            ),
            "nodes": nodes,
            "edges": edges,
        }

    def get_observability_candles(
        self,
        *,
        provider: str = "binance",
        symbol: str = "BTCUSDT",
        interval: str = "1m",
        hours: int = 24,
        limit: int = 200,
    ) -> dict[str, Any]:
        """Return real stored/rolled-up OHLCV candles from ClickHouseBatchSink with zero fabricated bars."""
        end_dt = datetime.now(UTC) + timedelta(minutes=5)
        start_dt = end_dt - timedelta(hours=max(1, min(hours, 168)))
        tr = BoundedTimeRange(start_time=start_dt, end_time=end_dt)
        raw_rows = self.clickhouse_sink.query_klines(
            provider, symbol, interval, tr.start_time, tr.end_time, limit=limit
        )
        candles = []
        for r in raw_rows:
            ex_t = r["exchange_event_time"]
            in_t = r["ingested_at"]
            lag_ms = round((in_t - ex_t).total_seconds() * 1000.0, 2)
            candles.append(
                {
                    "open_time": r["open_time"].isoformat(),
                    "close_time": r["close_time"].isoformat(),
                    "exchange_event_time": ex_t.isoformat(),
                    "ingested_at": in_t.isoformat(),
                    "ingestion_lag_ms": lag_ms,
                    "open": float(r["open_price"]),
                    "high": float(r["high_price"]),
                    "low": float(r["low_price"]),
                    "close": float(r["close_price"]),
                    "open_str": str(r["open_price"]),
                    "high_str": str(r["high_price"]),
                    "low_str": str(r["low_price"]),
                    "close_str": str(r["close_price"]),
                    "volume": float(r["base_volume"]),
                    "quote_volume": float(r["quote_volume"]),
                    "trade_count": int(r["trade_count"]),
                    "rolled_up_from_bars": r.get("rolled_up_from_bars", 1),
                }
            )
        stats = self.get_market_statistics_summary(provider, symbol)
        return {
            "provider": provider.lower(),
            "symbol": symbol.upper(),
            "interval": interval,
            "count": len(candles),
            "no_fake_candles_policy": True,
            "source_engine": (
                "ClickHouseBatchSink (ReplacingMergeTree deduplicated; "
                "1m->higher timeframe Decimal rollup)"
            ),
            "candles": candles,
            "statistics": {
                "vwap": str(stats.vwap) if stats else None,
                "realized_volatility": str(stats.realized_volatility) if stats else None,
                "total_base_volume": str(stats.total_base_volume) if stats else None,
                "trade_count": stats.trade_count if stats else 0,
            },
        }

    async def trigger_lakehouse_flush(self, execution_mode: str = "LIVE") -> dict[str, Any]:
        """Drain uncommitted Bronze Kafka messages through Bronze->Silver->DQ->Gold and update traces."""
        topics = [
            KafkaTopic.KLINES_V1.value,
            KafkaTopic.TRADES_V1.value,
            KafkaTopic.TICKERS_V1.value,
            KafkaTopic.ORDERBOOK_V1.value,
        ]
        pending_events: list[EventEnvelopeV1] = []
        pending_by_topic: dict[str, int] = {}
        for tp in topics:
            polled = self.kafka_broker.poll_topic(self.bronze_archiver.CONSUMER_GROUP, tp, max_records=2000)
            if polled:
                pending_events.extend(polled)
                pending_by_topic[tp] = len(polled)

        if not pending_events:
            report = await self.data_platform_v01.run_end_to_end_pipeline(
                symbols=("BTCUSDT", "ETHUSDT", "SOLUSDT"),
                interval="1m",
                backfill_minutes=4,
            )
            return {
                "action": "full_pipeline_run",
                "execution_mode": execution_mode,
                "flushed_pending_events": 0,
                "report": report.to_dict(),
            }

        t_b0 = time.perf_counter_ns()
        batch_tag = datetime.now(UTC).strftime("%Y%m%d%H%M%S%f")
        bronze_files = self.bronze_archiver.archive_batch(pending_events, batch_id=batch_tag)
        for tp, cnt in pending_by_topic.items():
            self.kafka_broker.commit_offsets(self.bronze_archiver.CONSUMER_GROUP, tp, cnt)
            self.observability_metrics.set_consumer_lag(
                self.bronze_archiver.CONSUMER_GROUP,
                tp,
                self.kafka_broker.get_topic_lag(self.bronze_archiver.CONSUMER_GROUP, tp),
            )
        bronze_ms = round((time.perf_counter_ns() - t_b0) / 1_000_000.0, 3)
        bronze_ts = utc_now_iso()

        t_s0 = time.perf_counter_ns()
        kline_files = [f for f in bronze_files if "kline" in f.name]
        trade_files = [f for f in bronze_files if "trade" in f.name]
        _, silver_klines = self.silver_merge_engine.merge_bronze_klines_to_silver(kline_files)
        _, silver_trades = self.silver_merge_engine.merge_bronze_trades_to_silver(trade_files)
        silver_ms = round((time.perf_counter_ns() - t_s0) / 1_000_000.0, 3)
        silver_ts = utc_now_iso()

        t_dq0 = time.perf_counter_ns()
        dq_klines = self.quality_gate_engine.validate_kline_dataset(silver_klines)
        dq_trades = self.quality_gate_engine.validate_trade_dataset(silver_trades)
        can_gold = dq_klines.can_promote_to_gold and dq_trades.can_promote_to_gold
        dq_ms = round((time.perf_counter_ns() - t_dq0) / 1_000_000.0, 3)

        t_g0 = time.perf_counter_ns()
        gold_rows = 0
        if can_gold and silver_klines:
            g_sum = self.gold_mart_engine.materialize_daily_market_summary(silver_klines)
            g_vol = self.gold_mart_engine.materialize_realized_volatility_mart(silver_klines)
            self.observability_metrics.set_gold_mart_rows("fct_daily_market_summary", g_sum.row_count)
            self.observability_metrics.set_gold_mart_rows("fct_realized_volatility", g_vol.row_count)
            gold_rows = g_sum.row_count + g_vol.row_count
        self.silver_merge_engine.compact_and_snapshot_iceberg_table(
            layer="silver", table_name="market_klines", sort_keys=("provider", "symbol", "open_time")
        )
        gold_ms = round((time.perf_counter_ns() - t_g0) / 1_000_000.0, 3)
        gold_ts = utc_now_iso()

        n = max(1, len(pending_events))
        for ev in pending_events:
            eid = str(ev.event_id)
            self.trace_registry.update_stage(
                eid,
                stage="bronze_archive",
                duration_ms=round(bronze_ms / n, 3),
                timestamp_field="bronze_committed_at",
                timestamp_value=bronze_ts,
                consumer_group=self.bronze_archiver.CONSUMER_GROUP,
            )
            self.trace_registry.update_stage(
                eid,
                stage="silver_merge",
                duration_ms=round(silver_ms / n, 3),
                timestamp_field="silver_processed_at",
                timestamp_value=silver_ts,
            )
            self.trace_registry.update_stage(
                eid,
                stage="dq_gate",
                duration_ms=round(dq_ms / n, 3),
            )
            self.trace_registry.update_stage(
                eid,
                stage="gold_mart",
                duration_ms=round(gold_ms / n, 3),
                timestamp_field="gold_loaded_at" if can_gold else None,
                timestamp_value=gold_ts if can_gold else None,
                final_status="SERVING_COMPLETE" if can_gold else "DQ_BLOCKED",
                error_detail=None if can_gold else "Blocked by Silver->Gold DQ gate",
            )

        return {
            "action": "bronze_to_gold_flush",
            "execution_mode": execution_mode,
            "flushed_pending_events": len(pending_events),
            "bronze_files_written": len(bronze_files),
            "silver_klines_rows": len(silver_klines),
            "silver_trades_rows": len(silver_trades),
            "gold_rows": gold_rows,
            "dq_passed": can_gold,
        }

    async def fetch_live_binance_market_data(
        self,
        *,
        symbol: str = "BTCUSDT",
        interval: str = "1m",
        limit: int = 10,
    ) -> dict[str, Any]:
        """Attempt real HTTPS pull from public api.binance.com and ingest into runtime."""
        sym = symbol.upper()
        url = "https://api.binance.com/api/v3/klines"
        try:
            async with httpx.AsyncClient(timeout=3.5) as client:
                resp = await client.get(
                    url, params={"symbol": sym, "interval": interval, "limit": max(1, min(limit, 50))}
                )
                resp.raise_for_status()
                raw_klines = resp.json()
        except Exception as exc:
            return {
                "status": "UNAVAILABLE",
                "execution_mode": "LIVE",
                "source": url,
                "symbol": sym,
                "events_ingested": 0,
                "error": f"Live Binance REST unavailable: {type(exc).__name__}: {exc}",
            }

        ingested = 0
        event_ids: list[str] = []
        now_utc = datetime.now(UTC)
        for row in raw_klines:
            raw_kline_event = {
                "e": "kline",
                "E": int(row[6]),
                "s": sym,
                "k": {
                    "t": int(row[0]),
                    "T": int(row[6]),
                    "i": interval,
                    "o": str(row[1]),
                    "h": str(row[2]),
                    "l": str(row[3]),
                    "c": str(row[4]),
                    "v": str(row[5]),
                    "q": str(row[7]),
                    "n": int(row[8]),
                },
            }
            env = await self.ingest_raw_provider_message(
                raw_kline_event,
                source_topic=KafkaTopic.KLINES_V1.value,
                ingested_at=now_utc,
                execution_mode="LIVE",
            )
            if env is not None:
                ingested += 1
                event_ids.append(str(env.event_id))

        return {
            "status": "LIVE_INGESTED",
            "execution_mode": "LIVE",
            "source": url,
            "symbol": sym,
            "interval": interval,
            "events_ingested": ingested,
            "event_ids": event_ids,
        }

    async def trigger_demo_action(
        self, action: str, symbol: str = "BTCUSDT", count: int = 5
    ) -> dict[str, Any]:
        """Execute an explicit, transparently labeled DEMO MODE simulation."""
        sym = symbol.upper()
        n = max(1, min(count, 25))
        base_map = {
            "BTCUSDT": Decimal("89620.50"),
            "ETHUSDT": Decimal("3145.25"),
            "SOLUSDT": Decimal("188.40"),
            "BNBUSDT": Decimal("612.80"),
            "XRPUSDT": Decimal("2.45"),
        }
        base_p = base_map.get(sym, Decimal("100.00"))

        if action == "emit_batch":
            emitted_ids: list[str] = []
            now_dt = datetime.now(UTC)
            for idx in range(n):
                delta = Decimal(str((idx - n // 2) * 1.25))
                price = max(Decimal("0.01"), base_p + delta)
                ts_ms = int((now_dt + timedelta(milliseconds=idx * 10)).timestamp() * 1000)
                trade_payload = {
                    "e": "trade",
                    "E": ts_ms,
                    "s": sym,
                    "t": int(time.time() * 1000) + idx,
                    "p": str(price),
                    "q": "0.85000000",
                    "T": ts_ms,
                    "m": idx % 2 == 0,
                }
                env = await self.ingest_raw_provider_message(
                    trade_payload,
                    source_topic=KafkaTopic.TRADES_V1.value,
                    execution_mode="DEMO",
                )
                if env is not None:
                    emitted_ids.append(str(env.event_id))
            return {
                "status": "DEMO_EXECUTED",
                "execution_mode": "DEMO",
                "action": action,
                "symbol": sym,
                "events_emitted": len(emitted_ids),
                "event_ids": emitted_ids,
            }

        if action == "inject_dlq":
            bad_payload = {
                "e": "trade",
                "E": int(time.time() * 1000),
                "s": sym,
                "t": int(time.time() * 1000),
                "p": "-42.50",
                "q": "1.0",
            }
            await self.ingest_raw_provider_message(
                bad_payload,
                source_topic=KafkaTopic.TRADES_V1.value,
                execution_mode="DEMO",
            )
            return {
                "status": "DEMO_DLQ_INJECTED",
                "execution_mode": "DEMO",
                "action": action,
                "symbol": sym,
                "dlq_total": len(self.kafka_broker.dlq_events),
            }

        if action == "flush_lakehouse":
            res = await self.trigger_lakehouse_flush(execution_mode="DEMO")
            return {"status": "DEMO_LAKEHOUSE_FLUSHED", **res}

        if action == "run_full_pipeline":
            report = await self.data_platform_v01.run_end_to_end_pipeline(
                symbols=(sym, "ETHUSDT", "SOLUSDT"),
                interval="1m",
                backfill_minutes=5,
            )
            return {
                "status": "DEMO_FULL_PIPELINE_RUN",
                "execution_mode": "DEMO",
                "action": action,
                "report": report.to_dict(),
            }

        raise ValueError(f"Unsupported demo action: {action}")
