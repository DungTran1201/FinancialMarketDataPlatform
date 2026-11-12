"""Hot State Projector Consumer (Kafka -> Redis with Monotonic Timestamp Guard)."""

from __future__ import annotations

import logging

from src.shared.config import PlatformConfig

logger = logging.getLogger(__name__)

# Atomic Lua script ensuring out-of-order Kafka retries never overwrite newer prices in Redis
REDIS_MONOTONIC_UPSERT_LUA = """
local current_ts = redis.call('HGET', KEYS[1], 'exchange_event_time_ms')
local incoming_ts = tonumber(ARGV[1])
if (not current_ts) or (incoming_ts >= tonumber(current_ts)) then
    redis.call('HSET', KEYS[1],
        'exchange_event_time_ms', ARGV[1],
        'ingested_at_ms', ARGV[2],
        'last_price', ARGV[3],
        'payload_json', ARGV[4]
    )
    redis.call('EXPIRE', KEYS[1], tonumber(ARGV[5]))
    return 1
end
return 0
"""


def build_hot_price_key(provider: str, symbol: str) -> str:
    """Return canonical Redis key for hot price lookups."""
    return f"market:v1:price:{provider.lower()}:{symbol.upper()}"


def build_hot_snapshot_key(provider: str, symbol: str) -> str:
    """Return canonical Redis key for 24h market snapshot lookups."""
    return f"market:v1:snapshot:{provider.lower()}:{symbol.upper()}"


def main() -> None:
    config = PlatformConfig()
    logging.basicConfig(level=config.log_level)
    logger.info("Initialized consumer-hot-redis worker targeting %s:%d", config.redis_host, config.redis_port)


if __name__ == "__main__":
    main()

