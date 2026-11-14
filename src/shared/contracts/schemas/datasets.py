"""Shared canonical dataset schema contracts across Streaming and Lakehouse layers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class DatasetLayer(StrEnum):
    """Medallion & serving dataset storage tier."""

    RAW = "raw"
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    HOT = "hot"
    CONTROL = "control"


class StorageEngine(StrEnum):
    """Polyglot storage engines enforced by ADR-003."""

    KAFKA = "Kafka"
    MINIO_ICEBERG = "MinIO_Iceberg"
    CLICKHOUSE = "ClickHouse"
    REDIS = "Redis"
    POSTGRESQL = "PostgreSQL"


@dataclass(frozen=True, slots=True)
class CanonicalDatasetContract:
    """Immutable descriptor of a canonical platform dataset."""

    dataset_name: str
    layer: DatasetLayer
    storage_engine: StorageEngine
    natural_key: tuple[str, ...]
    partition_by: tuple[str, ...]


CANONICAL_DATASET_CONTRACTS: dict[str, CanonicalDatasetContract] = {
    "silver.market_klines": CanonicalDatasetContract(
        dataset_name="silver.market_klines",
        layer=DatasetLayer.SILVER,
        storage_engine=StorageEngine.MINIO_ICEBERG,
        natural_key=("provider", "symbol", "interval", "open_time"),
        partition_by=("provider", "symbol", "interval"),
    ),
    "silver.market_trades": CanonicalDatasetContract(
        dataset_name="silver.market_trades",
        layer=DatasetLayer.SILVER,
        storage_engine=StorageEngine.MINIO_ICEBERG,
        natural_key=("provider", "symbol", "trade_id"),
        partition_by=("provider", "symbol"),
    ),
    "silver.order_book_snapshots": CanonicalDatasetContract(
        dataset_name="silver.order_book_snapshots",
        layer=DatasetLayer.SILVER,
        storage_engine=StorageEngine.MINIO_ICEBERG,
        natural_key=("provider", "symbol", "last_update_id"),
        partition_by=("provider", "symbol"),
    ),
    "gold.fct_daily_market_summary": CanonicalDatasetContract(
        dataset_name="gold.fct_daily_market_summary",
        layer=DatasetLayer.GOLD,
        storage_engine=StorageEngine.CLICKHOUSE,
        natural_key=("provider", "symbol", "trading_date"),
        partition_by=("trading_date",),
    ),
    "gold.fct_realized_volatility": CanonicalDatasetContract(
        dataset_name="gold.fct_realized_volatility",
        layer=DatasetLayer.GOLD,
        storage_engine=StorageEngine.CLICKHOUSE,
        natural_key=("provider", "symbol", "window"),
        partition_by=("window",),
    ),
    "gold.fct_orderbook_liquidity": CanonicalDatasetContract(
        dataset_name="gold.fct_orderbook_liquidity",
        layer=DatasetLayer.GOLD,
        storage_engine=StorageEngine.CLICKHOUSE,
        natural_key=("provider", "symbol", "last_update_id"),
        partition_by=("provider",),
    ),
}
