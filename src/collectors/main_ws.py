"""Entrypoint for the Real-Time WebSocket Collector Worker (collector-ws)."""

from __future__ import annotations

import logging

from src.shared.config import PlatformConfig

logger = logging.getLogger(__name__)


def main() -> None:
    """Initialize WebSocket collector worker configuration and lifecycle."""
    config = PlatformConfig()
    logging.basicConfig(level=config.log_level)
    logger.info(
        "Initialized collector-ws entrypoint (provider=%s, symbols=%s)",
        config.default_provider,
        config.monitored_symbols,
    )


if __name__ == "__main__":
    main()

