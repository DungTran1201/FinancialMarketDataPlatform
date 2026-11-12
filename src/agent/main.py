"""Entrypoint for the Isolated LangGraph Agent Worker (agent-worker — Plane C)."""

from __future__ import annotations

import logging

from src.shared.config import PlatformConfig

logger = logging.getLogger(__name__)


def main() -> None:
    """Initialize the isolated Agent Worker process."""
    config = PlatformConfig()
    logging.basicConfig(level=config.log_level)
    logger.info(
        "Initialized agent-worker (max_iterations=%d, tool_timeout=%.1fs, max_tokens=%d)",
        config.agent_max_iterations,
        config.agent_tool_timeout_seconds,
        config.agent_max_tokens_per_run,
    )


if __name__ == "__main__":
    main()

