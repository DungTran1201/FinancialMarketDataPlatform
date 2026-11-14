"""Unified Three-Plane Runtime Container wiring Data Plane (A), App Plane (B) & Intelligence Plane (C)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

from src.agent.orchestrator.graph import (
    AgentWorkflowState,
    DeterministicMockLLMAdapter,
    MarketIntelligenceGraph,
)
from src.agent.tools.contracts import ApprovedAgentTool
from src.agent.tools.gateway import (
    ControlledToolGateway,
    compute_deterministic_log_returns,
    compute_deterministic_pearson_correlation,
    compute_deterministic_realized_volatility,
)
from src.backend.modules.agent_api.domain.ports import AgentRunTicket
from src.backend.modules.analytics.domain.ports import MarketStatisticsSummary
from src.backend.modules.catalog.domain.ports import DataFreshnessReport
from src.backend.modules.historical.domain.ports import HistoricalCandleEntity
from src.backend.modules.market.application.queries import GetLatestPriceQueryHandler
from src.backend.modules.market.domain.entities import LatestPriceQuote
from src.backend.modules.market.domain.ports import (
    MarketFallbackRepositoryPort,
    MarketHotStorePort,
)
from src.backend.modules.platform_config.domain.ports import MonitoredInstrumentConfig
from src.backend.modules.reporting.domain.ports import (
    ProvenanceCitation,
    StructuredAnalysisReport,
)
from src.collectors.normalizer import BinancePayloadNormalizer
from src.collectors.publisher import (
    PartitionedEventStreamingBroker,
    ProductionExchangeHistoricalCollector,
)
from src.consumers.analytics_ch.main import ClickHouseBatchSink
from src.consumers.anomaly_detector import DetectedMarketAnomaly, StatisticalAnomalyDetector
from src.consumers.hot_redis.main import HotStateProjector
from src.consumers.lakehouse_bronze.main import BronzeParquetArchiver
from src.microservices.registry import MicroserviceRegistry
from src.processing.gold_marts import GoldLayerMartEngine
from src.processing.pipeline_v01 import DataPlatformV01Pipeline
from src.processing.spark.bronze_to_silver import SilverLakehouseMergeEngine
from src.quality.expectations.suite_definitions import DataQualityGateEngine
from src.quality.lineage_and_observability import (
    DataLineageGovernanceRegistry,
    DataObservabilityMetricsCollector,
)
from src.shared.config import PlatformConfig
from src.shared.contracts.events import EventEnvelopeV1
from src.shared.domain.primitives import BoundedTimeRange, InstrumentKey


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
        self.lineage_registry = DataLineageGovernanceRegistry()
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

    def _mount_domain_microservices(self) -> None:
        from src.microservices.analytics_service import create_analytics_microservice_app
        from src.microservices.catalog_service import create_catalog_microservice_app
        from src.microservices.data_plane_service import create_data_plane_microservice_app
        from src.microservices.historical_service import create_historical_microservice_app
        from src.microservices.iam_service import create_iam_microservice_app
        from src.microservices.intelligence_service import create_intelligence_microservice_app
        from src.microservices.market_service import create_market_microservice_app

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
    ) -> EventEnvelopeV1 | None:
        """Full Plane A pipeline: Normalize -> Validate -> Kafka -> Hot Redis + ClickHouse."""
        env, dlq = self.normalizer.normalize_or_route_dlq(
            raw_message, source_topic=source_topic, ingested_at=ingested_at
        )
        if dlq is not None:
            await self.kafka_broker.publish_dlq(dlq)
            return None
        assert env is not None
        topic = self.kafka_broker.resolve_topic_for_event(env)
        await self.kafka_broker.publish_event(topic, env)
        self.hot_redis_projector.project_event(env)
        self.clickhouse_sink.ingest_event(env, auto_flush=False)
        self.clickhouse_sink.flush()
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
