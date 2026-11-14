"""WebSocket Live Market Stream Collector CLI Entrypoint (`collector-ws`)."""

from __future__ import annotations

import logging

from src.shared.config.settings import PlatformConfig

logger = logging.getLogger(__name__)


def main() -> None:
    config = PlatformConfig()
    logging.basicConfig(level=config.log_level)
    logger.info(
        "Initialized collector-ws service for provider=%s targeting Kafka=%s",
        config.default_provider,
        config.kafka_bootstrap_servers,
    )


if __name__ == "__main__":
    main()
