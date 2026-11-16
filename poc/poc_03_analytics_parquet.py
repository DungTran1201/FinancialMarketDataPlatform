"""POC-03: DuckDB vs Polars ZSTD Parquet 1M-row analytical rollup & Point-in-Time ASOF join."""

from __future__ import annotations

import json
import statistics
import time
from pathlib import Path
from typing import Any

import duckdb
import polars as pl
import psutil

TMP_DIR = Path(__file__).resolve().parent / ".tmp" / "poc03_parquet"
RESULTS_DIR = Path(__file__).resolve().parent / "results"


def _setup_dataset(n_rows: int = 1_000_000) -> tuple[Path, Path, float]:
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    trades_pq = TMP_DIR / "silver_trades.parquet"
    features_pq = TMP_DIR / "gold_features.parquet"

    t0 = time.perf_counter()
    # Deterministic synthetic canonical Spot/Perp trade dataset across 4 symbols
    df = pl.DataFrame(
        {
            "seq": range(n_rows),
        }
    ).with_columns(
        [
            pl.when((pl.col("seq") % 4) == 0)
            .then(pl.lit("binance:spot:BTC/USDT"))
            .when((pl.col("seq") % 4) == 1)
            .then(pl.lit("okx:swap:BTC/USDT"))
            .when((pl.col("seq") % 4) == 2)
            .then(pl.lit("binance:perp:ETH/USDT"))
            .otherwise(pl.lit("okx:expiry:BTC/USDT:20261225"))
            .alias("instrument_id"),
            (1_700_000_000_000 + (pl.col("seq") * 50)).alias("exchange_event_ms"),
            (1_700_000_000_015 + (pl.col("seq") * 50)).alias("available_at_ms"),
            (89_000.0 + ((pl.col("seq") % 500) * 0.25)).alias("price"),
            (0.01 + ((pl.col("seq") % 20) * 0.005)).alias("qty"),
            pl.when((pl.col("seq") % 3) == 0).then(pl.lit("BUY")).otherwise(pl.lit("SELL")).alias("aggressor_side"),
        ]
    )
    df.write_parquet(trades_pq, compression="zstd", row_group_size=100_000)

    # 50,000 point-in-time decision grid timestamps
    dec_df = pl.DataFrame({"dec_seq": range(50_000)}).with_columns(
        [
            pl.when((pl.col("dec_seq") % 2) == 0)
            .then(pl.lit("binance:spot:BTC/USDT"))
            .otherwise(pl.lit("okx:swap:BTC/USDT"))
            .alias("instrument_id"),
            (1_700_000_100_000 + (pl.col("dec_seq") * 900)).alias("decision_time_ms"),
        ]
    )
    dec_df.write_parquet(features_pq, compression="zstd")
    gen_sec = round(time.perf_counter() - t0, 3)
    return trades_pq, features_pq, gen_sec


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    proc = psutil.Process()
    rss_start_mb = round(proc.memory_info().rss / (1024 * 1024), 2)

    trades_pq, dec_pq, gen_sec = _setup_dataset(1_000_000)
    size_mb = round(trades_pq.stat().st_size / (1024 * 1024), 2)

    # 1. DuckDB benchmark (explicit 768MB cap + 4 threads)
    con = duckdb.connect(":memory:")
    con.execute("SET memory_limit='768MB';")
    con.execute("SET threads=4;")

    duck_rollup_ms: list[float] = []
    duck_peak_rss = proc.memory_info().rss
    for _ in range(5):
        t0 = time.perf_counter()
        rows = con.execute(
            f"""
            SELECT
                instrument_id,
                (exchange_event_ms // 60000) * 60000 AS bar_min,
                FIRST(price) AS open_px,
                MAX(price) AS high_px,
                MIN(price) AS low_px,
                LAST(price) AS close_px,
                SUM(qty) AS vol,
                SUM(price * qty) / SUM(qty) AS vwap,
                STDDEV_SAMP(price) AS px_std
            FROM read_parquet('{trades_pq.as_posix()}')
            GROUP BY 1, 2
            """
        ).fetchall()
        duck_rollup_ms.append((time.perf_counter() - t0) * 1000.0)
        duck_peak_rss = max(duck_peak_rss, proc.memory_info().rss)

    # Point-in-time ASOF join in DuckDB (strictly available_at_ms <= decision_time_ms)
    duck_asof_ms: list[float] = []
    for _ in range(3):
        t0 = time.perf_counter()
        asof_cnt = con.execute(
            f"""
            SELECT COUNT(*) FROM (
                SELECT d.instrument_id, d.decision_time_ms, t.price, t.available_at_ms
                FROM read_parquet('{dec_pq.as_posix()}') d
                ASOF JOIN read_parquet('{trades_pq.as_posix()}') t
                    ON d.instrument_id = t.instrument_id
                   AND d.decision_time_ms >= t.available_at_ms
            )
            """
        ).fetchone()
        duck_asof_ms.append((time.perf_counter() - t0) * 1000.0)
        duck_peak_rss = max(duck_peak_rss, proc.memory_info().rss)
    con.close()

    # 2. Polars LazyFrame benchmark
    polars_rollup_ms: list[float] = []
    polars_asof_ms: list[float] = []
    pl_peak_rss = proc.memory_info().rss
    for _ in range(5):
        t0 = time.perf_counter()
        out_pl = (
            pl.scan_parquet(trades_pq)
            .with_columns(((pl.col("exchange_event_ms") // 60_000) * 60_000).alias("bar_min"))
            .group_by(["instrument_id", "bar_min"])
            .agg(
                [
                    pl.col("price").first().alias("open_px"),
                    pl.col("price").max().alias("high_px"),
                    pl.col("price").min().alias("low_px"),
                    pl.col("price").last().alias("close_px"),
                    pl.col("qty").sum().alias("vol"),
                    ((pl.col("price") * pl.col("qty")).sum() / pl.col("qty").sum()).alias("vwap"),
                ]
            )
            .collect(engine="streaming")
        )
        polars_rollup_ms.append((time.perf_counter() - t0) * 1000.0)
        pl_peak_rss = max(pl_peak_rss, proc.memory_info().rss)

    for _ in range(3):
        t0 = time.perf_counter()
        t_sorted = pl.scan_parquet(trades_pq).sort(["instrument_id", "available_at_ms"])
        d_sorted = pl.scan_parquet(dec_pq).sort(["instrument_id", "decision_time_ms"])
        joined = d_sorted.join_asof(
            t_sorted,
            left_on="decision_time_ms",
            right_on="available_at_ms",
            by="instrument_id",
            strategy="backward",
        ).select(pl.len()).collect(engine="streaming")
        polars_asof_ms.append((time.perf_counter() - t0) * 1000.0)
        pl_peak_rss = max(pl_peak_rss, proc.memory_info().rss)

    report: dict[str, Any] = {
        "probe": "POC-03",
        "duckdb_version": duckdb.__version__,
        "polars_version": pl.__version__,
        "rows_trades": 1_000_000,
        "rows_decisions": 50_000,
        "zstd_parquet_size_mb": size_mb,
        "dataset_gen_sec": gen_sec,
        "rss_start_mb": rss_start_mb,
        "duckdb": {
            "rollup_bars": len(rows),
            "rollup_runs_ms": [round(x, 2) for x in duck_rollup_ms],
            "rollup_median_ms": round(statistics.median(duck_rollup_ms), 2),
            "asof_join_rows": asof_cnt[0] if asof_cnt else 0,
            "asof_runs_ms": [round(x, 2) for x in duck_asof_ms],
            "peak_rss_mb": round(duck_peak_rss / (1024 * 1024), 2),
        },
        "polars_streaming": {
            "rollup_bars": len(out_pl),
            "rollup_runs_ms": [round(x, 2) for x in polars_rollup_ms],
            "rollup_median_ms": round(statistics.median(polars_rollup_ms), 2),
            "asof_join_rows": int(joined.item()),
            "asof_runs_ms": [round(x, 2) for x in polars_asof_ms],
            "peak_rss_mb": round(pl_peak_rss / (1024 * 1024), 2),
        },
    }
    (RESULTS_DIR / "poc_03_analytics_parquet.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

