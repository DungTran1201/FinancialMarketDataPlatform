"""Ingestion domain value objects for exchange metadata, stream gaps, and watermarks."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class ExchangeSymbolMetadata:
    """Stage 1 Data Source Discovery metadata for a trading instrument."""

    provider: str
    symbol: str
    status: str
    base_asset: str
    quote_asset: str
    tick_size: Decimal
    lot_size: Decimal
    min_notional: Decimal


@dataclass(frozen=True, slots=True)
class DetectedStreamGap:
    """Represents a detected missing sequence or kline interval gap requiring REST backfill."""

    provider: str
    symbol: str
    interval: str
    gap_start: datetime
    gap_end: datetime
    missing_candles: int


@dataclass(frozen=True, slots=True)
class WatermarkRecord:
    """Durable ingestion watermark checkpoint record (`ingestion_watermarks` control table)."""

    provider: str
    symbol: str
    interval: str
    last_open_time: datetime
    updated_at: datetime
    status: str  # SYNCED | BACKFILLING | GAP_DETECTED
