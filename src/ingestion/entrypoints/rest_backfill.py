"""Historical REST Backfill Worker CLI Entrypoint (`collector-rest`)."""

from __future__ import annotations

import logging

from src.shared.config.settings import PlatformConfig

logger = logging.getLogger(__name__)


def main() -> None:
    config = PlatformConfig()
    logging.basicConfig(level=config.log_level)
    logger.info(
        "Initialized collector-rest backfill worker for provider=%s",
        config.default_provider,
    )


if __name__ == "__main__":
    main()
