"""Hot State Streaming Consumer & Monotonic Projector (Kafka -> Redis 7)."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from src.shared.config.settings import PlatformConfig
from src.shared.contracts.events.market_events import EventEnvelopeV1, EventType

logger = logging.getLogger(__name__)

# Atomic Lua script enforcing monotonic exchange_event_time_ms updates (ADR-005 / Section 5.1).
# Prevents out-of-order Kafka retries or replays from overwriting newer hot prices in Redis.
REDIS_MONOTONIC_UPSERT_LUA = """
local current_ts = redis.call('HGET', KEYS[1], 'exchange_event_time_ms')
local incoming_ts = tonumber(ARGV[1])
if (not current_ts) or (incoming_ts >= tonumber(current_ts)) then
    for i = 2, #ARGV, 2 do
        redis.call('HSET', KEYS[1], ARGV[i], ARGV[i + 1])
    end
    redis.call('EXPIRE', KEYS[1], tonumber(ARGV[2]))
    return 1
end
return 0
"""


def build_hot_price_key(provider: str, symbol: str) -> str:
    """Return canonical Redis key for latest instrument price."""
    return f"market:v1:price:{provider.lower()}:{symbol.upper()}"


def build_hot_snapshot_key(provider: str, symbol: str) -> str:
    """Return canonical Redis key for 24h market snapshot."""
    return f"market:v1:snapshot:{provider.lower()}:{symbol.upper()}"


def build_hot_orderbook_key(provider: str, symbol: str) -> str:
    """Return canonical Redis key for top-20 order book depth."""
    return f"market:v1:orderbook:{provider.lower()}:{symbol.upper()}"


@dataclass(frozen=True, slots=True)
class HotPriceRecord:
    """Projected hot price record stored in Redis with monotonic timestamp protection."""

    provider: str
    symbol: str
    last_price: Decimal
    exchange_event_time: datetime
    ingested_at: datetime
    ttl_seconds: int = 300


class HotStateProjector:
    """Projects Kafka market events into Redis hot state enforcing monotonic timestamps (`BR-003`)."""

    CONSUMER_GROUP = "cg.hot.redis.v1"

    def __init__(
        self,
        price_ttl_seconds: int = 300,
        orderbook_ttl_seconds: int = 120,
        state_path: Path | str | None = None,
        redis_client: Any | None = None,
    ) -> None:
        self._price_ttl = price_ttl_seconds
        self._orderbook_ttl = orderbook_ttl_seconds
        self._state_path = Path(state_path) if state_path is not None else None
        self._redis_client = redis_client
        self._price_store: dict[str, HotPriceRecord] = {}
        self._snapshot_store: dict[str, dict[str, Any]] = {}
        self._orderbook_store: dict[str, dict[str, Any]] = {}
        self._dropped_out_of_order: int = 0
        self._applied_updates: int = 0
        self._load_persisted_state()

    def _load_persisted_state(self) -> None:
        if self._state_path is None or not self._state_path.exists():
            return
        try:
            raw = json.loads(self._state_path.read_text(encoding="utf-8"))
            for k, v in raw.get("prices", {}).items():
                self._price_store[k] = HotPriceRecord(
                    provider=str(v["provider"]),
                    symbol=str(v["symbol"]),
                    last_price=Decimal(str(v["last_price"])),
                    exchange_event_time=datetime.fromisoformat(str(v["exchange_event_time"])),
                    ingested_at=datetime.fromisoformat(str(v["ingested_at"])),
                    ttl_seconds=int(v.get("ttl_seconds", self._price_ttl)),
                )
            self._snapshot_store.update(raw.get("snapshots", {}))
            self._orderbook_store.update(raw.get("orderbooks", {}))
        except Exception as exc:
            logger.warning("Failed to load persisted Redis hot state from %s: %s", self._state_path, exc)

    def _persist_state(self) -> None:
        if self._state_path is None:
            return
        self._state_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "prices": {
                k: {
                    "provider": rec.provider,
                    "symbol": rec.symbol,
                    "last_price": str(rec.last_price),
                    "exchange_event_time": rec.exchange_event_time.isoformat(),
                    "ingested_at": rec.ingested_at.isoformat(),
                    "ttl_seconds": rec.ttl_seconds,
                }
                for k, rec in self._price_store.items()
            },
            "snapshots": self._snapshot_store,
            "orderbooks": self._orderbook_store,
        }
        self._state_path.write_text(json.dumps(payload), encoding="utf-8")

    def project_event(self, event: EventEnvelopeV1) -> bool:
        """Apply event if `exchange_event_time >= current.exchange_event_time`; return True if updated."""
        price_key = build_hot_price_key(event.provider, event.symbol)
        existing = self._price_store.get(price_key)
        if existing is not None and event.exchange_event_time < existing.exchange_event_time:
            self._dropped_out_of_order += 1
            return False

        raw_price = event.payload.get("price") or event.payload.get("close_price") or event.payload.get("last_price")
        if raw_price is not None:
            self._price_store[price_key] = HotPriceRecord(
                provider=event.provider,
                symbol=event.symbol,
                last_price=Decimal(str(raw_price)),
                exchange_event_time=event.exchange_event_time,
                ingested_at=event.ingested_at,
                ttl_seconds=self._price_ttl,
            )

        snap_key = build_hot_snapshot_key(event.provider, event.symbol)
        snap = dict(self._snapshot_store.get(snap_key, {}))
        snap.update(
            {
                "provider": event.provider,
                "symbol": event.symbol,
                "last_price": str(raw_price or snap.get("last_price", "0")),
                "high_24h": str(
                    event.payload.get("high_24h")
                    or event.payload.get("high_price")
                    or snap.get("high_24h", raw_price or "0")
                ),
                "low_24h": str(
                    event.payload.get("low_24h")
                    or event.payload.get("low_price")
                    or snap.get("low_24h", raw_price or "0")
                ),
                "vwap_24h": str(event.payload.get("vwap_24h") or snap.get("vwap_24h", raw_price or "0")),
                "base_volume_24h": str(
                    event.payload.get("base_volume_24h")
                    or event.payload.get("base_volume")
                    or snap.get("base_volume_24h", "0")
                ),
                "exchange_event_time": event.exchange_event_time.isoformat(),
                "ingested_at": event.ingested_at.isoformat(),
            }
        )
        self._snapshot_store[snap_key] = snap

        if event.event_type == EventType.ORDER_BOOK:
            ob_key = build_hot_orderbook_key(event.provider, event.symbol)
            self._orderbook_store[ob_key] = {
                "provider": event.provider,
                "symbol": event.symbol,
                "bids": event.payload.get("bids", []),
                "asks": event.payload.get("asks", []),
                "exchange_event_time": event.exchange_event_time.isoformat(),
                "ttl_seconds": self._orderbook_ttl,
            }

        self._applied_updates += 1
        self._persist_state()
        if self._redis_client is not None:
            self._sync_record_to_live_redis(price_key, event)
        return True

    def _sync_record_to_live_redis(self, price_key: str, event: EventEnvelopeV1) -> None:
        """Execute atomic Lua monotonic upsert against a live Redis 7 client when connected."""
        try:
            ts_ms = int(event.exchange_event_time.timestamp() * 1000)
            raw_price = (
                event.payload.get("price")
                or event.payload.get("close_price")
                or event.payload.get("last_price")
                or "0"
            )
            self._redis_client.eval(
                REDIS_MONOTONIC_UPSERT_LUA,
                1,
                price_key,
                ts_ms,
                self._price_ttl,
                "exchange_event_time_ms",
                str(ts_ms),
                "last_price",
                str(raw_price),
                "provider",
                event.provider,
                "symbol",
                event.symbol,
            )
        except Exception as exc:
            logger.warning("Live Redis Lua sync warning on %s: %s", price_key, exc)

    def evict_hot_symbol(self, provider: str, symbol: str) -> None:
        """Evict hot price/snapshot/orderbook keys for a symbol (simulating TTL expiry or Redis miss)."""
        self._price_store.pop(build_hot_price_key(provider, symbol), None)
        self._snapshot_store.pop(build_hot_snapshot_key(provider, symbol), None)
        self._orderbook_store.pop(build_hot_orderbook_key(provider, symbol), None)

    def get_hot_price(self, provider: str, symbol: str) -> HotPriceRecord | None:
        return self._price_store.get(build_hot_price_key(provider, symbol))

    def get_hot_snapshot(self, provider: str, symbol: str) -> dict[str, Any] | None:
        return self._snapshot_store.get(build_hot_snapshot_key(provider, symbol))

    def get_hot_orderbook(self, provider: str, symbol: str) -> dict[str, Any] | None:
        return self._orderbook_store.get(build_hot_orderbook_key(provider, symbol))

    @property
    def dropped_out_of_order_count(self) -> int:
        return self._dropped_out_of_order

    @property
    def applied_updates_count(self) -> int:
        return self._applied_updates


def main() -> None:
    config = PlatformConfig()
    logging.basicConfig(level=config.log_level)
    logger.info(
        "Initialized consumer-hot-redis worker targeting %s:%d",
        config.redis_host,
        config.redis_port,
    )


if __name__ == "__main__":
    main()
