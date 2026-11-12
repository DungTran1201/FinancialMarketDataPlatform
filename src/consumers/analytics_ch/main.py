"""Analytics Micro-Batch Consumer (Kafka -> ClickHouse ReplacingMergeTree)."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from src.shared.config import PlatformConfig

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class MicroBatchBuffer:
    """Buffers streaming events up to max_rows or flush_interval_ms before bulk ClickHouse insert."""

    max_rows: int = 5000
    flush_interval_ms: int = 1000
    _rows: list[dict[str, Any]] = field(default_factory=list)

    def append(self, row: dict[str, Any]) -> bool:
        """Append row and return True if batch size threshold is reached."""
        self._rows.append(row)
        return len(self._rows) >= self.max_rows

    def drain(self) -> list[dict[str, Any]]:
        """Drain and return buffered rows after successful flush."""
        flushed = list(self._rows)
        self._rows.clear()
        return flushed


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

