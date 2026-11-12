"""Environment-driven platform configuration without hardcoded secrets."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class PlatformConfig:
    """Immutable platform configuration loaded from environment variables."""

    app_env: str = field(default_factory=lambda: os.getenv("APP_ENV", "local"))
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    default_provider: str = field(default_factory=lambda: os.getenv("DEFAULT_PROVIDER", "binance"))
    monitored_symbols: tuple[str, ...] = field(
        default_factory=lambda: tuple(
            s.strip().upper()
            for s in os.getenv("MONITORED_SYMBOLS", "BTCUSDT,ETHUSDT,SOLUSDT").split(",")
            if s.strip()
        )
    )
    market_staleness_threshold_ms: int = field(
        default_factory=lambda: int(os.getenv("MARKET_STALENESS_THRESHOLD_MS", "15000"))
    )
    kafka_bootstrap_servers: str = field(
        default_factory=lambda: os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    )
    redis_host: str = field(default_factory=lambda: os.getenv("REDIS_HOST", "localhost"))
    redis_port: int = field(default_factory=lambda: int(os.getenv("REDIS_PORT", "6379")))
    clickhouse_host: str = field(default_factory=lambda: os.getenv("CLICKHOUSE_HOST", "localhost"))
    clickhouse_http_port: int = field(
        default_factory=lambda: int(os.getenv("CLICKHOUSE_HTTP_PORT", "8123"))
    )
    postgres_host: str = field(default_factory=lambda: os.getenv("POSTGRES_HOST", "localhost"))
    postgres_port: int = field(default_factory=lambda: int(os.getenv("POSTGRES_PORT", "5432")))
    agent_max_iterations: int = field(
        default_factory=lambda: int(os.getenv("AGENT_MAX_ITERATIONS", "6"))
    )
    agent_tool_timeout_seconds: float = field(
        default_factory=lambda: float(os.getenv("AGENT_TOOL_TIMEOUT_SECONDS", "5.0"))
    )
    agent_max_tokens_per_run: int = field(
        default_factory=lambda: int(os.getenv("AGENT_MAX_TOKENS_PER_RUN", "8000"))
    )

