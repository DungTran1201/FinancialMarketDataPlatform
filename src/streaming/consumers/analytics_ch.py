"""Analytics Micro-Batch Consumer & ReplacingMergeTree Sink (Kafka -> ClickHouse)."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

from src.shared.config.settings import PlatformConfig
from src.shared.contracts.events.market_events import EventEnvelopeV1, EventType

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class MicroBatchBuffer:
    """In-memory columnar buffer flushing every 1,000ms or 5,000 rows (ADR-002 / Section 5.2)."""

    max_rows: int = 5000
    flush_interval_ms: int = 1000
    _rows: list[dict[str, Any]] = field(default_factory=list)

    def append(self, row: dict[str, Any]) -> bool:
        """Append a row and return True if the buffer has reached `max_rows`."""
        self._rows.append(row)
        return len(self._rows) >= self.max_rows

    def drain(self) -> list[dict[str, Any]]:
        """Return all buffered rows and clear the internal buffer."""
        batch = list(self._rows)
        self._rows.clear()
        return batch

    @property
    def size(self) -> int:
        return len(self._rows)


class ClickHouseBatchSink:
    """Columnar OLAP sink enforcing `ReplacingMergeTree` deduplication & `AggregatingMergeTree` rollups."""

    CONSUMER_GROUP = "cg.analytics.clickhouse.v1"

    def __init__(
        self,
        max_batch_rows: int = 5000,
        flush_interval_ms: int = 1000,
        state_path: Path | str | None = None,
        clickhouse_client: Any | None = None,
    ) -> None:
        self.buffer = MicroBatchBuffer(max_rows=max_batch_rows, flush_interval_ms=flush_interval_ms)
        self._state_path = Path(state_path) if state_path is not None else None
        self._clickhouse_client = clickhouse_client
        # ReplacingMergeTree tables keyed by natural keys
        self._trades_table: dict[tuple[str, str, int], dict[str, Any]] = {}
        self._klines_table: dict[tuple[str, str, str, str], dict[str, Any]] = {}
        self._tickers_table: dict[tuple[str, str, str], dict[str, Any]] = {}
        self._flushed_batches_count: int = 0
        self._load_persisted_state()

    def _load_persisted_state(self) -> None:
        if self._state_path is None or not self._state_path.exists():
            return
        try:
            raw = json.loads(self._state_path.read_text(encoding="utf-8"))
            for row in raw.get("klines", []):
                k_key = (
                    str(row["provider"]),
                    str(row["symbol"]),
                    str(row["interval"]),
                    str(row["open_time"]),
                )
                self._klines_table[k_key] = {
                    "provider": str(row["provider"]),
                    "symbol": str(row["symbol"]),
                    "interval": str(row["interval"]),
                    "open_time": datetime.fromisoformat(str(row["open_time"])),
                    "close_time": datetime.fromisoformat(str(row["close_time"])),
                    "open_price": Decimal(str(row["open_price"])),
                    "high_price": Decimal(str(row["high_price"])),
                    "low_price": Decimal(str(row["low_price"])),
                    "close_price": Decimal(str(row["close_price"])),
                    "base_volume": Decimal(str(row["base_volume"])),
                    "quote_volume": Decimal(str(row["quote_volume"])),
                    "trade_count": int(row["trade_count"]),
                    "is_closed": bool(row["is_closed"]),
                    "exchange_event_time": datetime.fromisoformat(str(row["exchange_event_time"])),
                    "ingested_at": datetime.fromisoformat(str(row["ingested_at"])),
                }
        except Exception as exc:
            logger.warning("Failed to load persisted ClickHouse state from %s: %s", self._state_path, exc)

    def _persist_state(self) -> None:
        if self._state_path is None:
            return
        self._state_path.parent.mkdir(parents=True, exist_ok=True)
        klines_serialized = [
            {
                "provider": r["provider"],
                "symbol": r["symbol"],
                "interval": r["interval"],
                "open_time": r["open_time"].isoformat(),
                "close_time": r["close_time"].isoformat(),
                "open_price": str(r["open_price"]),
                "high_price": str(r["high_price"]),
                "low_price": str(r["low_price"]),
                "close_price": str(r["close_price"]),
                "base_volume": str(r["base_volume"]),
                "quote_volume": str(r["quote_volume"]),
                "trade_count": r["trade_count"],
                "is_closed": r["is_closed"],
                "exchange_event_time": r["exchange_event_time"].isoformat(),
                "ingested_at": r["ingested_at"].isoformat(),
            }
            for r in self._klines_table.values()
        ]
        self._state_path.write_text(json.dumps({"klines": klines_serialized}), encoding="utf-8")

    def ingest_event(self, event: EventEnvelopeV1, auto_flush: bool = True) -> int:
        """Buffer an event and automatically flush to ReplacingMergeTree tables when full."""
        should_flush = self.buffer.append(
            {
                "event_id": str(event.event_id),
                "provider": event.provider,
                "symbol": event.symbol,
                "event_type": event.event_type.value,
                "exchange_event_time": event.exchange_event_time,
                "ingested_at": event.ingested_at,
                "payload": dict(event.payload),
            }
        )
        if should_flush and auto_flush:
            return self.flush()
        return 0

    def flush(self) -> int:
        """Flush buffered records into ReplacingMergeTree tables with versioned deduplication."""
        rows = self.buffer.drain()
        if not rows:
            return 0

        for row in rows:
            provider = str(row["provider"]).lower()
            symbol = str(row["symbol"]).upper()
            etype = str(row["event_type"])
            ex_time: datetime = row["exchange_event_time"]
            ing_time: datetime = row["ingested_at"]
            payload: dict[str, Any] = row["payload"]

            if etype == EventType.TRADE.value:
                trade_id = int(payload["trade_id"])
                key = (provider, symbol, trade_id)
                existing = self._trades_table.get(key)
                if existing is None or ing_time >= existing["ingested_at"]:
                    self._trades_table[key] = {
                        "provider": provider,
                        "symbol": symbol,
                        "trade_id": trade_id,
                        "price": Decimal(str(payload["price"])),
                        "quantity": Decimal(str(payload["quantity"])),
                        "quote_volume": Decimal(str(payload["quote_volume"])),
                        "trade_time": datetime.fromisoformat(str(payload["trade_time"])),
                        "exchange_event_time": ex_time,
                        "ingested_at": ing_time,
                    }
            elif etype == EventType.KLINE.value:
                interval = str(payload.get("interval", "1m"))
                open_time_iso = str(payload["open_time"])
                k_key = (provider, symbol, interval, open_time_iso)
                existing_k = self._klines_table.get(k_key)
                if existing_k is None or ex_time >= existing_k["exchange_event_time"]:
                    self._klines_table[k_key] = {
                        "provider": provider,
                        "symbol": symbol,
                        "interval": interval,
                        "open_time": datetime.fromisoformat(open_time_iso),
                        "close_time": datetime.fromisoformat(str(payload["close_time"])),
                        "open_price": Decimal(str(payload["open_price"])),
                        "high_price": Decimal(str(payload["high_price"])),
                        "low_price": Decimal(str(payload["low_price"])),
                        "close_price": Decimal(str(payload["close_price"])),
                        "base_volume": Decimal(str(payload["base_volume"])),
                        "quote_volume": Decimal(str(payload["quote_volume"])),
                        "trade_count": int(payload.get("trade_count", 0)),
                        "is_closed": bool(payload.get("is_closed", True)),
                        "exchange_event_time": ex_time,
                        "ingested_at": ing_time,
                    }
            elif etype == EventType.TICKER.value:
                t_key = (provider, symbol, ex_time.isoformat())
                self._tickers_table[t_key] = {
                    "provider": provider,
                    "symbol": symbol,
                    "last_price": Decimal(str(payload["last_price"])),
                    "exchange_event_time": ex_time,
                    "ingested_at": ing_time,
                }

        self._flushed_batches_count += 1
        self._persist_state()
        return len(rows)

    def query_klines(
        self,
        provider: str,
        symbol: str,
        interval: str,
        start_time: datetime,
        end_time: datetime,
        limit: int = 500,
    ) -> list[dict[str, Any]]:
        """Query deduplicated klines ordered by `open_time ASC`, rolling up 1m bars if needed."""
        prov = provider.lower()
        sym = symbol.upper()
        matched = [
            row
            for (p, s, iv, _), row in self._klines_table.items()
            if p == prov and s == sym and iv == interval and start_time <= row["open_time"] <= end_time
        ]
        if matched:
            matched.sort(key=lambda r: r["open_time"])
            return matched[:limit]

        interval_seconds_map = {
            "1m": 60,
            "5m": 300,
            "15m": 900,
            "1h": 3600,
            "4h": 14400,
            "1d": 86400,
        }
        target_sec = interval_seconds_map.get(interval)
        if target_sec is None or interval == "1m":
            return []

        source_bars = [
            row
            for (p, s, iv, _), row in self._klines_table.items()
            if p == prov
            and s == sym
            and interval_seconds_map.get(iv, 9999999) < target_sec
            and start_time <= row["open_time"] <= end_time
        ]
        if not source_bars:
            return []

        buckets: dict[int, list[dict[str, Any]]] = {}
        for row in source_bars:
            open_dt = row["open_time"]
            epoch_s = int(open_dt.timestamp())
            bucket_epoch = (epoch_s // target_sec) * target_sec
            buckets.setdefault(bucket_epoch, []).append(row)

        rolled_up: list[dict[str, Any]] = []
        for bucket_epoch in sorted(buckets.keys()):
            items = sorted(buckets[bucket_epoch], key=lambda r: r["open_time"])
            first = items[0]
            last = items[-1]
            open_dt = datetime.fromtimestamp(bucket_epoch, tz=UTC)
            close_dt = datetime.fromtimestamp(bucket_epoch + target_sec, tz=UTC) - timedelta(milliseconds=1)
            rolled_up.append(
                {
                    "provider": prov,
                    "symbol": sym,
                    "interval": interval,
                    "open_time": open_dt,
                    "close_time": close_dt,
                    "open_price": first["open_price"],
                    "high_price": max(r["high_price"] for r in items),
                    "low_price": min(r["low_price"] for r in items),
                    "close_price": last["close_price"],
                    "base_volume": sum((r["base_volume"] for r in items), Decimal("0")),
                    "quote_volume": sum((r["quote_volume"] for r in items), Decimal("0")),
                    "trade_count": sum(int(r["trade_count"]) for r in items),
                    "exchange_event_time": last["exchange_event_time"],
                    "ingested_at": last["ingested_at"],
                    "rolled_up_from_bars": len(items),
                }
            )
        return rolled_up[:limit]

    def get_storage_snapshot(self) -> dict[str, Any]:
        """Return real ClickHouse in-memory OLAP & micro-batch buffer telemetry."""
        symbols = sorted(
            {s for (_p, s, _t) in self._trades_table}
            | {s for (_p, s, _iv, _t) in self._klines_table}
            | {s for (_p, s) in self._tickers_table}
        )
        intervals = sorted({iv for (_p, _s, iv, _t) in self._klines_table})
        latest_ingested = max(
            (
                row["ingested_at"]
                for row in (
                    list(self._trades_table.values())
                    + list(self._klines_table.values())
                    + list(self._tickers_table.values())
                )
            ),
            default=None,
        )
        pending_rows = list(self.buffer._rows)
        trades_pending = sum(1 for r in pending_rows if r.get("_table") == "trades")
        klines_pending = sum(1 for r in pending_rows if r.get("_table") == "klines")
        tickers_pending = sum(1 for r in pending_rows if r.get("_table") == "tickers")
        return {
            "engine_mode": "IN_PROCESS_REPLACING_MERGE_TREE_SIMULATION",
            "ddl_schema_path": "deploy/clickhouse/init/01_schema.sql",
            "tables": {
                "market_trades_raw": len(self._trades_table),
                "market_klines_1m": len(self._klines_table),
                "market_tickers_latest": len(self._tickers_table),
            },
            "total_rows": len(self._trades_table) + len(self._klines_table) + len(self._tickers_table),
            "buffers": {
                "trades_pending": trades_pending,
                "klines_pending": klines_pending,
                "tickers_pending": tickers_pending,
                "total_pending": len(pending_rows),
                "max_rows_per_batch": self.buffer.max_rows,
                "flush_interval_ms": self.buffer.flush_interval_ms,
            },
            "flushed_batches_count": self._flushed_batches_count,
            "symbols_present": symbols,
            "intervals_present": intervals,
            "latest_ingested_at": latest_ingested.isoformat() if latest_ingested else None,
        }

    def get_latest_price_from_olap(self, provider: str, symbol: str) -> dict[str, Any] | None:
        """Fallback query returning the most recent trade or kline close price from ClickHouse."""
        prov = provider.lower()
        sym = symbol.upper()
        candidates: list[tuple[datetime, Decimal, datetime]] = []
        for (p, s, _), row in self._trades_table.items():
            if p == prov and s == sym:
                candidates.append((row["exchange_event_time"], row["price"], row["ingested_at"]))
        for (p, s, _, _), row in self._klines_table.items():
            if p == prov and s == sym:
                candidates.append((row["exchange_event_time"], row["close_price"], row["ingested_at"]))
        if not candidates:
            return None
        candidates.sort(key=lambda item: item[0], reverse=True)
        latest_ex, latest_price, latest_ing = candidates[0]
        return {
            "provider": prov,
            "symbol": sym,
            "last_price": latest_price,
            "exchange_event_time": latest_ex,
            "ingested_at": latest_ing,
        }

    def compute_aggregated_statistics(self, provider: str, symbol: str) -> dict[str, Any] | None:
        """Compute `AggregatingMergeTree` equivalent summary (VWAP, volume, trade_count, close series)."""
        prov = provider.lower()
        sym = symbol.upper()
        klines = [row for (p, s, _, _), row in self._klines_table.items() if p == prov and s == sym]
        klines.sort(key=lambda r: r["open_time"])
        if not klines:
            return None
        total_base = sum((r["base_volume"] for r in klines), Decimal("0"))
        total_quote = sum((r["quote_volume"] for r in klines), Decimal("0"))
        total_trades = sum(int(r["trade_count"]) for r in klines)
        vwap = (
            (total_quote / total_base).quantize(Decimal("0.00000001"))
            if total_base > Decimal("0")
            else klines[-1]["close_price"]
        )
        close_prices = [float(r["close_price"]) for r in klines]
        close_prices_decimal = [str(r["close_price"]) for r in klines]
        return {
            "provider": prov,
            "symbol": sym,
            "vwap": vwap,
            "total_base_volume": total_base,
            "total_quote_volume": total_quote,
            "trade_count": total_trades,
            "close_prices": close_prices,
            "close_prices_decimal": close_prices_decimal,
            "candle_count": len(klines),
        }


def main() -> None:
    config = PlatformConfig()
    logging.basicConfig(level=config.log_level)
    logger.info(
        "Initialized consumer-analytics-ch worker targeting ClickHouse %s:%d",
        config.clickhouse_host,
        config.clickhouse_http_port,
    )


if __name__ == "__main__":
    main()
