"""Bronze Lakehouse Parquet Archiver (Kafka -> MinIO / Apache Iceberg Bronze)."""

from __future__ import annotations

import logging

from src.shared.config import PlatformConfig

logger = logging.getLogger(__name__)


def build_bronze_partition_path(provider: str, event_type: str, ingestion_date: str) -> str:
    """Return canonical Hive/Iceberg-compatible Bronze object storage path."""
    return f"bronze/{event_type}/provider={provider.lower()}/ingestion_date={ingestion_date}"


def main() -> None:
    config = PlatformConfig()
    logging.basicConfig(level=config.log_level)
    logger.info("Initialized consumer-lakehouse-bronze archiver worker")


if __name__ == "__main__":
    main()

