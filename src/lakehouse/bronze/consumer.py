"""Lakehouse Bronze Kafka-to-Parquet Consumer Entrypoint (`consumer-lakehouse-bronze`)."""

from __future__ import annotations

import logging

from src.shared.config.settings import PlatformConfig

logger = logging.getLogger(__name__)


def main() -> None:
    config = PlatformConfig()
    logging.basicConfig(level=config.log_level)
    logger.info("Initialized consumer-lakehouse-bronze archiver worker")


if __name__ == "__main__":
    main()
