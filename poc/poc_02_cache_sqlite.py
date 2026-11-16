"""POC-02: Bounded In-Process Hot Cache & Concurrent SQLite WAL Benchmark."""

from __future__ import annotations

import asyncio
import json
import sqlite3
import time
import tracemalloc
from collections import deque
from pathlib import Path
from typing import Any

import psutil

TMP_DIR = Path(__file__).resolve().parent / ".tmp"
RESULTS_DIR = Path(__file__).resolve().parent / "results"


class BoundedHotCache:
    """Ephemeral in-process hot state bounded strictly by symbol count and deque depth."""

    def __init__(self, max_ticks_per_symbol: int = 1000, max_book_levels: int = 100) -> None:
        self.max_ticks = max_ticks_per_symbol
        self.max_levels = max_book_levels
        self.ticks: dict[str, deque[tuple[int, float, float]]] = {}
        self.books: dict[str, tuple[dict[float, float], dict[float, float]]] = {}

    def apply_tick(self, sym: str, ts_ms: int, price: float, qty: float) -> None:
        buf = self.ticks.get(sym)
        if buf is None:
            buf = deque(maxlen=self.max_ticks)
            self.ticks[sym] = buf
        buf.append((ts_ms, price, qty))

    def apply_book_snapshot(self, sym: str, bids: dict[float, float], asks: dict[float, float]) -> None:
        top_b = dict(sorted(bids.items(), reverse=True)[: self.max_levels])
        top_a = dict(sorted(asks.items())[: self.max_levels])
        self.books[sym] = (top_b, top_a)


def _pct(vals: list[float], q: float) -> float:
    if not vals:
        return 0.0
    s = sorted(vals)
    return round(s[min(len(s) - 1, max(0, int((len(s) - 1) * q)))], 3)


def benchmark_hot_cache() -> dict[str, Any]:
    tracemalloc.start()
    proc = psutil.Process()
    rss_before = proc.memory_info().rss
    cache = BoundedHotCache(max_ticks_per_symbol=1000, max_book_levels=100)
    symbols = [f"venue:perp:ASSET{i}/USDT" for i in range(20)]

    t0 = time.perf_counter()
    for step in range(50_000):
        sym = symbols[step % len(symbols)]
        px = 100.0 + (step % 500) * 0.01
        cache.apply_tick(sym, 1_700_000_000_000 + step, px, 0.5)
        if step % 25 == 0:
            bids = {px - lvl * 0.1: float(lvl + 1) for lvl in range(120)}
            asks = {px + 0.1 + lvl * 0.1: float(lvl + 1) for lvl in range(120)}
            cache.apply_book_snapshot(sym, bids, asks)
    elapsed = time.perf_counter() - t0
    curr_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    rss_after = proc.memory_info().rss

    assert all(len(v) <= 1000 for v in cache.ticks.values())
    assert all(len(b[0]) <= 100 and len(b[1]) <= 100 for b in cache.books.values())
    return {
        "updates": 50_000,
        "symbols": len(symbols),
        "elapsed_sec": round(elapsed, 3),
        "updates_per_sec": round(50_000 / elapsed, 1),
        "tracemalloc_current_mb": round(curr_mem / (1024 * 1024), 2),
        "tracemalloc_peak_mb": round(peak_mem / (1024 * 1024), 2),
        "rss_delta_mb": round((rss_after - rss_before) / (1024 * 1024), 2),
    }


async def benchmark_sqlite_wal() -> dict[str, Any]:
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    db_path = TMP_DIR / "poc_metadata_wal.db"
    for ext in ("", "-wal", "-shm"):
        p = Path(str(db_path) + ext)
        if p.exists():
            p.unlink()

    wconn = sqlite3.connect(db_path, isolation_level=None, check_same_thread=False)
    wconn.execute("PRAGMA journal_mode=WAL;")
    wconn.execute("PRAGMA synchronous=NORMAL;")
    wconn.execute("PRAGMA busy_timeout=5000;")
    wconn.execute(
        """
        CREATE TABLE IF NOT EXISTS watermarks (
            instrument_id TEXT PRIMARY KEY,
            last_event_ms INTEGER NOT NULL,
            status TEXT NOT NULL,
            updated_at_ms INTEGER NOT NULL
        );
        """
    )

    write_lat_ms: list[float] = []
    read_lat_ms: list[float] = []
    lock_errors = 0
    writes_target = 1000
    done_writing = asyncio.Event()

    async def single_writer() -> None:
        nonlocal lock_errors
        for i in range(writes_target):
            sym = f"binance:spot:PAIR{i % 25}/USDT"
            t0 = time.perf_counter()
            try:
                wconn.execute("BEGIN")
                wconn.execute(
                    """
                    INSERT INTO watermarks (instrument_id, last_event_ms, status, updated_at_ms)
                    VALUES (?, ?, 'SYNCED', ?)
                    ON CONFLICT(instrument_id) DO UPDATE SET
                        last_event_ms=excluded.last_event_ms,
                        updated_at_ms=excluded.updated_at_ms
                    """,
                    (sym, 1_700_000_000_000 + i, time.time_ns() // 1_000_000),
                )
                wconn.execute("COMMIT")
            except sqlite3.OperationalError:
                lock_errors += 1
                wconn.execute("ROLLBACK")
            write_lat_ms.append((time.perf_counter() - t0) * 1000.0)
            if i % 20 == 0:
                await asyncio.sleep(0)
        done_writing.set()

    async def reader_worker(reader_id: int) -> int:
        nonlocal lock_errors
        rconn = sqlite3.connect(db_path, check_same_thread=False)
        rconn.execute("PRAGMA busy_timeout=5000;")
        reads = 0
        while not done_writing.is_set():
            t0 = time.perf_counter()
            try:
                rconn.execute("SELECT COUNT(*), MAX(last_event_ms) FROM watermarks").fetchone()
                reads += 1
            except sqlite3.OperationalError:
                lock_errors += 1
            read_lat_ms.append((time.perf_counter() - t0) * 1000.0)
            await asyncio.sleep(0.001)
        rconn.close()
        return reads

    t0 = time.perf_counter()
    results = await asyncio.gather(single_writer(), *(reader_worker(r) for r in range(5)))
    elapsed = time.perf_counter() - t0
    wconn.close()

    return {
        "sqlite_version": sqlite3.sqlite_version,
        "writes": writes_target,
        "concurrent_readers": 5,
        "total_reads": sum(results[1:]),
        "lock_errors": lock_errors,
        "elapsed_sec": round(elapsed, 3),
        "write_latency_ms": {
            "p50": _pct(write_lat_ms, 0.50),
            "p95": _pct(write_lat_ms, 0.95),
            "p99": _pct(write_lat_ms, 0.99),
        },
        "read_latency_ms": {
            "p50": _pct(read_lat_ms, 0.50),
            "p95": _pct(read_lat_ms, 0.95),
            "p99": _pct(read_lat_ms, 0.99),
        },
        "db_wal_size_kb": round(db_path.stat().st_size / 1024.0, 2),
    }


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "probe": "POC-02",
        "hot_cache": benchmark_hot_cache(),
        "sqlite_wal": asyncio.run(benchmark_sqlite_wal()),
    }
    (RESULTS_DIR / "poc_02_cache_sqlite.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

