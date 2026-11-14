"""Gold Layer Analytical Mart Materialization Engine (Silver -> Gold Lakehouse & OLAP Marts).

Implements Stage 7 of the 12-Stage Data Lifecycle (`docs/architecture/04-data-platform-architecture.md`):
1. `gold.fct_daily_market_summary` (mirrors `src/transformation/dbt/models/marts/fct_daily_market_summary.sql`)
2. `gold.fct_realized_volatility` (rolling & annualized realized volatility from log returns)
3. `gold.fct_orderbook_liquidity` (bid-ask spread bps, depth notional & orderbook imbalance)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq


@dataclass(frozen=True, slots=True)
class GoldMartMaterializationResult:
    """Summary of a materialized Gold layer analytical mart."""

    mart_name: str
    row_count: int
    parquet_path: str
    rows: tuple[dict[str, Any], ...]


class GoldLayerMartEngine:
    """Materializes curated Gold analytical marts (`fct_daily_market_summary`, `fct_realized_volatility`,
    `fct_orderbook_liquidity`) from validated Silver datasets into ZSTD Parquet tables.
    """

    def __init__(self, lakehouse_root: Path | str = ".local_lakehouse") -> None:
        self._root = Path(lakehouse_root)
        self._marts_store: dict[str, list[dict[str, Any]]] = {
            "fct_daily_market_summary": [],
            "fct_realized_volatility": [],
            "fct_orderbook_liquidity": [],
        }

    def materialize_daily_market_summary(
        self,
        silver_klines: list[dict[str, Any]],
    ) -> GoldMartMaterializationResult:
        """Execute the `fct_daily_market_summary` Gold transformation grouped by `(provider, symbol, trading_date)`."""
        grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
        for row in silver_klines:
            if not row.get("is_closed", True):
                continue
            provider = str(row["provider"]).lower()
            symbol = str(row["symbol"]).upper()
            trading_date = str(row["open_time"])[:10]
            grouped.setdefault((provider, symbol, trading_date), []).append(row)

        mart_rows: list[dict[str, Any]] = []
        for (provider, symbol, trading_date), candles in sorted(grouped.items()):
            candles.sort(key=lambda c: str(c["open_time"]))
            daily_open = Decimal(str(candles[0]["open_price"]))
            daily_close = Decimal(str(candles[-1]["close_price"]))
            daily_high = max(Decimal(str(c["high_price"])) for c in candles)
            daily_low = min(Decimal(str(c["low_price"])) for c in candles)
            total_base = sum((Decimal(str(c["base_volume"])) for c in candles), Decimal("0"))
            total_quote = sum((Decimal(str(c["quote_volume"])) for c in candles), Decimal("0"))
            total_trades = sum(int(c.get("trade_count", 0)) for c in candles)
            daily_vwap = (total_quote / total_base) if total_base > Decimal("0") else daily_close
            daily_ret_pct = (
                ((daily_close - daily_open) / daily_open * Decimal("100"))
                if daily_open > Decimal("0")
                else Decimal("0")
            )
            hl_spread_pct = (
                ((daily_high - daily_low) / daily_low * Decimal("100"))
                if daily_low > Decimal("0")
                else Decimal("0")
            )
            mart_rows.append(
                {
                    "provider": provider,
                    "symbol": symbol,
                    "trading_date": trading_date,
                    "daily_open": float(daily_open.quantize(Decimal("0.00000001"))),
                    "daily_high": float(daily_high.quantize(Decimal("0.00000001"))),
                    "daily_low": float(daily_low.quantize(Decimal("0.00000001"))),
                    "daily_close": float(daily_close.quantize(Decimal("0.00000001"))),
                    "total_base_volume": float(total_base.quantize(Decimal("0.00000001"))),
                    "total_quote_volume": float(total_quote.quantize(Decimal("0.00000001"))),
                    "total_trades": total_trades,
                    "daily_vwap": float(daily_vwap.quantize(Decimal("0.00000001"))),
                    "daily_return_pct": float(daily_ret_pct.quantize(Decimal("0.0001"))),
                    "intraday_range_pct": float(hl_spread_pct.quantize(Decimal("0.0001"))),
                    "candle_count": len(candles),
                }
            )

        out_path = self._write_gold_parquet("fct_daily_market_summary", mart_rows)
        self._marts_store["fct_daily_market_summary"] = mart_rows
        return GoldMartMaterializationResult(
            mart_name="gold.fct_daily_market_summary",
            row_count=len(mart_rows),
            parquet_path=out_path.as_posix(),
            rows=tuple(mart_rows),
        )

    def materialize_realized_volatility_mart(
        self,
        silver_klines: list[dict[str, Any]],
        annualization_factor: float = 365.0 * 24.0 * 60.0,
    ) -> GoldMartMaterializationResult:
        """Materialize `gold.fct_realized_volatility` computing log-return standard deviation & drawdown."""
        grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
        for row in silver_klines:
            provider = str(row["provider"]).lower()
            symbol = str(row["symbol"]).upper()
            interval = str(row.get("interval", "1m"))
            grouped.setdefault((provider, symbol, interval), []).append(row)

        mart_rows: list[dict[str, Any]] = []
        for (provider, symbol, interval), candles in sorted(grouped.items()):
            candles.sort(key=lambda c: str(c["open_time"]))
            closes = [float(c["close_price"]) for c in candles if float(c["close_price"]) > 0]
            log_returns: list[float] = []
            for i in range(1, len(closes)):
                log_returns.append(math.log(closes[i] / closes[i - 1]))

            if log_returns:
                mean_ret = sum(log_returns) / len(log_returns)
                variance = sum((r - mean_ret) ** 2 for r in log_returns) / max(1, len(log_returns))
                std_ret = math.sqrt(variance)
                ann_vol = std_ret * math.sqrt(annualization_factor)
            else:
                mean_ret = 0.0
                std_ret = 0.0
                ann_vol = 0.0

            peak = closes[0] if closes else 0.0
            max_dd_pct = 0.0
            for p in closes:
                if p > peak:
                    peak = p
                if peak > 0:
                    dd = ((peak - p) / peak) * 100.0
                    if dd > max_dd_pct:
                        max_dd_pct = dd

            mart_rows.append(
                {
                    "provider": provider,
                    "symbol": symbol,
                    "interval": interval,
                    "sample_size": len(closes),
                    "mean_log_return": round(mean_ret, 8),
                    "period_volatility": round(std_ret, 8),
                    "realized_volatility_annualized": round(ann_vol, 6),
                    "max_drawdown_pct": round(max_dd_pct, 4),
                    "window_start": str(candles[0]["open_time"]) if candles else "",
                    "window_end": str(candles[-1]["close_time"]) if candles else "",
                }
            )

        out_path = self._write_gold_parquet("fct_realized_volatility", mart_rows)
        self._marts_store["fct_realized_volatility"] = mart_rows
        return GoldMartMaterializationResult(
            mart_name="gold.fct_realized_volatility",
            row_count=len(mart_rows),
            parquet_path=out_path.as_posix(),
            rows=tuple(mart_rows),
        )

    def materialize_orderbook_liquidity_mart(
        self,
        orderbook_snapshots: list[dict[str, Any]],
    ) -> GoldMartMaterializationResult:
        """Materialize `gold.fct_orderbook_liquidity` measuring spread bps, depth notional & imbalance."""
        mart_rows: list[dict[str, Any]] = []
        for snap in orderbook_snapshots:
            provider = str(snap.get("provider", "binance")).lower()
            symbol = str(snap.get("symbol", "BTCUSDT")).upper()
            bids = snap.get("bids", [])
            asks = snap.get("asks", [])
            if not bids or not asks:
                continue
            best_bid = float(bids[0][0])
            best_ask = float(asks[0][0])
            mid_price = (best_bid + best_ask) / 2.0
            spread_bps = ((best_ask - best_bid) / mid_price * 10000.0) if mid_price > 0 else 0.0
            bid_depth_notional = sum(float(b[0]) * float(b[1]) for b in bids[:20])
            ask_depth_notional = sum(float(a[0]) * float(a[1]) for a in asks[:20])
            total_depth = bid_depth_notional + ask_depth_notional
            imbalance = (
                (bid_depth_notional - ask_depth_notional) / total_depth if total_depth > 0 else 0.0
            )
            mart_rows.append(
                {
                    "provider": provider,
                    "symbol": symbol,
                    "best_bid": round(best_bid, 8),
                    "best_ask": round(best_ask, 8),
                    "mid_price": round(mid_price, 8),
                    "spread_bps": round(spread_bps, 4),
                    "bid_depth_notional_top20": round(bid_depth_notional, 4),
                    "ask_depth_notional_top20": round(ask_depth_notional, 4),
                    "orderbook_imbalance": round(imbalance, 6),
                    "exchange_event_time": str(snap.get("exchange_event_time", "")),
                }
            )

        out_path = self._write_gold_parquet("fct_orderbook_liquidity", mart_rows)
        self._marts_store["fct_orderbook_liquidity"] = mart_rows
        return GoldMartMaterializationResult(
            mart_name="gold.fct_orderbook_liquidity",
            row_count=len(mart_rows),
            parquet_path=out_path.as_posix(),
            rows=tuple(mart_rows),
        )

    def query_gold_mart(self, mart_name: str, symbol: str | None = None) -> list[dict[str, Any]]:
        """Query materialized Gold mart records with optional symbol filter."""
        clean_name = mart_name.replace("gold.", "")
        rows = list(self._marts_store.get(clean_name, []))
        if symbol:
            sym = symbol.upper()
            rows = [r for r in rows if str(r.get("symbol", "")).upper() == sym]
        return rows

    def _write_gold_parquet(self, mart_name: str, rows: list[dict[str, Any]]) -> Path:
        out_dir = self._root / "gold" / mart_name
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / f"gold_{mart_name}.parquet"
        if rows:
            pq.write_table(pa.Table.from_pylist(rows), out_file, compression="ZSTD")
        return out_file

