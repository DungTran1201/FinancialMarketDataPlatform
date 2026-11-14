"""Gold Layer Analytical Mart Materialization Engine (Silver -> Gold Lakehouse & OLAP Marts).

Implements Stage 7 of the 12-Stage Data Lifecycle (`docs/architecture/04-data-platform-architecture.md`)
enforcing `BR-001` (Financial Precision Invariant): all prices, volumes, VWAPs, spreads, and notional
depths are computed and stored using exact fixed-point `Decimal` arithmetic (`0.00000001`).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

DEC_8 = Decimal("0.00000001")
DEC_6 = Decimal("0.000001")
DEC_4 = Decimal("0.0001")
ZERO = Decimal("0")


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
        """Execute `fct_daily_market_summary` grouped by `(provider, symbol, trading_date)` with exact Decimal math."""
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
            total_base = sum((Decimal(str(c["base_volume"])) for c in candles), ZERO)
            total_quote = sum((Decimal(str(c["quote_volume"])) for c in candles), ZERO)
            total_trades = sum(int(c.get("trade_count", 0)) for c in candles)
            daily_vwap = (total_quote / total_base) if total_base > ZERO else daily_close
            daily_ret_pct = (
                ((daily_close - daily_open) / daily_open * Decimal("100"))
                if daily_open > ZERO
                else ZERO
            )
            hl_spread_pct = (
                ((daily_high - daily_low) / daily_low * Decimal("100"))
                if daily_low > ZERO
                else ZERO
            )
            mart_rows.append(
                {
                    "provider": provider,
                    "symbol": symbol,
                    "trading_date": trading_date,
                    "daily_open": str(daily_open.quantize(DEC_8)),
                    "daily_high": str(daily_high.quantize(DEC_8)),
                    "daily_low": str(daily_low.quantize(DEC_8)),
                    "daily_close": str(daily_close.quantize(DEC_8)),
                    "total_base_volume": str(total_base.quantize(DEC_8)),
                    "total_quote_volume": str(total_quote.quantize(DEC_8)),
                    "total_trades": total_trades,
                    "daily_vwap": str(daily_vwap.quantize(DEC_8)),
                    "daily_return_pct": str(daily_ret_pct.quantize(DEC_4)),
                    "intraday_range_pct": str(hl_spread_pct.quantize(DEC_4)),
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
        """Materialize `gold.fct_realized_volatility` computing log-return volatility & Decimal drawdown."""
        grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
        for row in silver_klines:
            provider = str(row["provider"]).lower()
            symbol = str(row["symbol"]).upper()
            interval = str(row.get("interval", "1m"))
            grouped.setdefault((provider, symbol, interval), []).append(row)

        mart_rows: list[dict[str, Any]] = []
        for (provider, symbol, interval), candles in sorted(grouped.items()):
            candles.sort(key=lambda c: str(c["open_time"]))
            dec_closes = [
                Decimal(str(c["close_price"]))
                for c in candles
                if Decimal(str(c["close_price"])) > ZERO
            ]
            log_returns: list[Decimal] = []
            for i in range(1, len(dec_closes)):
                ratio = float(dec_closes[i] / dec_closes[i - 1])
                log_returns.append(Decimal(str(math.log(ratio))))

            if log_returns:
                n_ret = Decimal(str(len(log_returns)))
                mean_ret = sum(log_returns, ZERO) / n_ret
                variance = sum(((r - mean_ret) ** 2 for r in log_returns), ZERO) / n_ret
                std_ret = variance.sqrt()
                ann_vol = std_ret * Decimal(str(math.sqrt(annualization_factor)))
            else:
                mean_ret = ZERO
                std_ret = ZERO
                ann_vol = ZERO

            peak = dec_closes[0] if dec_closes else ZERO
            max_dd_pct = ZERO
            for p in dec_closes:
                if p > peak:
                    peak = p
                if peak > ZERO:
                    dd = ((peak - p) / peak) * Decimal("100")
                    if dd > max_dd_pct:
                        max_dd_pct = dd

            mart_rows.append(
                {
                    "provider": provider,
                    "symbol": symbol,
                    "interval": interval,
                    "sample_size": len(dec_closes),
                    "mean_log_return": str(mean_ret.quantize(DEC_8)),
                    "period_volatility": str(std_ret.quantize(DEC_8)),
                    "realized_volatility_annualized": str(ann_vol.quantize(DEC_6)),
                    "max_drawdown_pct": str(max_dd_pct.quantize(DEC_4)),
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
        """Materialize `gold.fct_orderbook_liquidity` using exact `Decimal` math for spread & depth."""
        mart_rows: list[dict[str, Any]] = []
        for snap in orderbook_snapshots:
            provider = str(snap.get("provider", "binance")).lower()
            symbol = str(snap.get("symbol", "BTCUSDT")).upper()
            bids = snap.get("bids", [])
            asks = snap.get("asks", [])
            if not bids or not asks:
                continue
            best_bid = Decimal(str(bids[0][0]))
            best_ask = Decimal(str(asks[0][0]))
            mid_price = (best_bid + best_ask) / Decimal("2")
            spread_bps = (
                ((best_ask - best_bid) / mid_price * Decimal("10000"))
                if mid_price > ZERO
                else ZERO
            )
            bid_depth_notional = sum(
                (Decimal(str(b[0])) * Decimal(str(b[1])) for b in bids[:20]),
                ZERO,
            )
            ask_depth_notional = sum(
                (Decimal(str(a[0])) * Decimal(str(a[1])) for a in asks[:20]),
                ZERO,
            )
            total_depth = bid_depth_notional + ask_depth_notional
            imbalance = (
                (bid_depth_notional - ask_depth_notional) / total_depth
                if total_depth > ZERO
                else ZERO
            )
            mart_rows.append(
                {
                    "provider": provider,
                    "symbol": symbol,
                    "best_bid": str(best_bid.quantize(DEC_8)),
                    "best_ask": str(best_ask.quantize(DEC_8)),
                    "mid_price": str(mid_price.quantize(DEC_8)),
                    "spread_bps": str(spread_bps.quantize(DEC_4)),
                    "bid_depth_notional_top20": str(bid_depth_notional.quantize(DEC_4)),
                    "ask_depth_notional_top20": str(ask_depth_notional.quantize(DEC_4)),
                    "orderbook_imbalance": str(imbalance.quantize(DEC_6)),
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
