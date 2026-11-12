"""Market Presentation Layer (FastAPI Router & HTTP Response Envelope)."""

from __future__ import annotations

from typing import Any


def build_market_router() -> Any:
    """Build the FastAPI APIRouter for the Market domain."""
    from fastapi import APIRouter

    router = APIRouter()

    @router.get("/prices/{symbol}")
    async def get_symbol_price(symbol: str, provider: str = "binance") -> dict[str, Any]:
        return {
            "data": {
                "provider": provider.lower(),
                "symbol": symbol.upper(),
                "status": "scaffold_initialized",
            },
            "meta": {"source": "redis_hot_cache"},
        }

    return router

