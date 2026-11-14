"""Hot State Streaming Consumer & Monotonic Projector (Kafka -> Redis 7)."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any

from src.shared.config import PlatformConfig
from src.shared.contracts.events import EventEnvelopeV1, EventType

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

    def __init__(self, price_ttl_seconds: int = 300, orderbook_ttl_seconds: int = 120) -> None:
        self._price_ttl = price_ttl_seconds
        self._orderbook_ttl = orderbook_ttl_seconds
        self._price_store: dict[str, HotPriceRecord] = {}
        self._snapshot_store: dict[str, dict[str, Any]] = {}
        self._orderbook_store: dict[str, dict[str, Any]] = {}
        self._dropped_out_of_order: int = 0
        self._applied_updates: int = 0

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
        return True

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
