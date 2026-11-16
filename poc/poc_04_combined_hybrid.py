"""POC-04: Combined multi-process Hybrid benchmark (Realtime Core + Isolated Worker + SIGKILL recovery)."""

from __future__ import annotations

import asyncio
import json
import os
import sqlite3
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any

import duckdb
import nats
import psutil
import pyarrow as pa
import pyarrow.parquet as pq
from nats.js.api import ConsumerConfig, RetentionPolicy, StorageType, StreamConfig
from nats.js.errors import NotFoundError

POC_DIR = Path(__file__).resolve().parent
TMP_DIR = POC_DIR / ".tmp" / "poc04_combined"
RESULTS_DIR = POC_DIR / "results"
NATS_URL = os.environ.get("FMDP_POC_NATS_URL", "nats://127.0.0.1:4222")


async def _worker_loop() -> None:
    """Isolated Process 2: JetStream pull -> Atomic ZSTD Parquet writer + SQLite WAL + DuckDB checks."""
    parquet_dir = TMP_DIR / "parquet"
    parquet_dir.mkdir(parents=True, exist_ok=True)
    db_path = TMP_DIR / "state.db"

    wconn = sqlite3.connect(db_path, isolation_level=None)
    wconn.execute("PRAGMA journal_mode=WAL;")
    wconn.execute("PRAGMA synchronous=NORMAL;")
    wconn.execute("PRAGMA busy_timeout=5000;")
    wconn.execute("CREATE TABLE IF NOT EXISTS offsets (batch_id TEXT PRIMARY KEY, row_count INTEGER, ts INTEGER);")

    nc = await nats.connect(NATS_URL, max_reconnect_attempts=20)
    js = nc.jetstream()
    sub = await js.pull_subscribe(
        "mkt.poc4.events",
        durable="poc4_writer",
        config=ConsumerConfig(durable_name="poc4_writer", ack_wait=3.0, max_ack_pending=500),
    )

    stop_file = TMP_DIR / "stop.flag"
    batch_idx = 0
    while not stop_file.exists():
        try:
            msgs = await sub.fetch(250, timeout=0.5)
        except TimeoutError:
            # Periodic DuckDB analytical read probe in isolated worker while idle
            pqs = list(parquet_dir.glob("*.parquet"))
            if pqs and batch_idx % 3 == 0:
                con = duckdb.connect(":memory:")
                con.execute("SET memory_limit='512MB'; SET threads=2;")
                con.execute(f"SELECT COUNT(*) FROM read_parquet('{(parquet_dir / '*.parquet').as_posix()}')").fetchone()
                con.close()
            continue

        rows = [json.loads(m.data.decode()) for m in msgs]
        if not rows:
            continue
        batch_idx += 1
        bid = f"{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"
        tbl = pa.Table.from_pylist(rows)
        tmp_path = parquet_dir / f"part_{bid}.parquet.tmp"
        final_path = parquet_dir / f"part_{bid}.parquet"
        pq.write_table(tbl, tmp_path, compression="zstd")
        os.replace(tmp_path, final_path)

        wconn.execute("BEGIN")
        wconn.execute(
            "INSERT OR IGNORE INTO offsets (batch_id, row_count, ts) VALUES (?, ?, ?)",
            (bid, len(rows), time.time_ns()),
        )
        wconn.execute("COMMIT")

        for m in msgs:
            await m.ack()

    wconn.close()
    await nc.drain()


async def _run_coordinator() -> dict[str, Any]:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    if TMP_DIR.exists():
        for p in sorted(TMP_DIR.rglob("*"), reverse=True):
            if p.is_file():
                p.unlink()
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    (TMP_DIR / "parquet").mkdir(exist_ok=True)

    nc = await nats.connect(NATS_URL)
    js = nc.jetstream()
    try:
        await js.delete_stream("MKT_POC4")
    except NotFoundError:
        print("Stream MKT_POC4 not present; creating fresh.")
    await js.add_stream(
        StreamConfig(
            name="MKT_POC4",
            subjects=["mkt.poc4.>"],
            retention=RetentionPolicy.LIMITS,
            storage=StorageType.FILE,
            max_bytes=128 * 1024 * 1024,
        )
    )

    worker_proc = await asyncio.create_subprocess_exec(sys.executable, __file__, "--worker")
    coord_ps = psutil.Process()

    rss_samples: list[dict[str, float]] = []
    pub_lat_before_query_ms: list[float] = []
    pub_lat_during_query_ms: list[float] = []
    total_events = 9_000
    rate_batch = 150  # ~1,500 events/s using 100ms pacing
    killed_once = False

    def sample_rss() -> None:
        w_rss = 0.0
        try:
            if worker_proc.returncode is None:
                w_rss = psutil.Process(worker_proc.pid).memory_info().rss / (1024 * 1024)
        except psutil.Error:
            w_rss = 0.0
        c_rss = coord_ps.memory_info().rss / (1024 * 1024)
        rss_samples.append({"coord_mb": round(c_rss, 2), "worker_mb": round(w_rss, 2)})

    for start in range(0, total_events, rate_batch):
        t0 = time.perf_counter()
        futs = []
        for idx in range(start, min(total_events, start + rate_batch)):
            payload = json.dumps(
                {
                    "event_id": idx,
                    "instrument_id": "okx:swap:BTC/USDT",
                    "price": 89500.0 + (idx % 100) * 0.5,
                    "qty": 1.0,
                    "ts_ns": time.time_ns(),
                }
            ).encode()
            futs.append(js.publish("mkt.poc4.events", payload, headers={"Nats-Msg-Id": f"p4-{idx}"}))
        await asyncio.gather(*futs)
        batch_ms = (time.perf_counter() - t0) * 1000.0
        if start < total_events // 2:
            pub_lat_before_query_ms.append(batch_ms)
        else:
            pub_lat_during_query_ms.append(batch_ms)

        if not killed_once and start >= total_events // 2:
            killed_once = True
            worker_proc.kill()
            await worker_proc.wait()
            await asyncio.sleep(0.3)
            worker_proc = await asyncio.create_subprocess_exec(sys.executable, __file__, "--worker")

        sample_rss()
        elapsed_tick = time.perf_counter() - t0
        if elapsed_tick < 0.1:
            await asyncio.sleep(0.1 - elapsed_tick)

    # Wait for restarted worker to catch up and drain stream
    deadline = time.perf_counter() + 20.0
    while time.perf_counter() < deadline:
        info = await js.consumer_info("MKT_POC4", "poc4_writer")
        sample_rss()
        if info.num_pending == 0 and info.num_ack_pending == 0:
            break
        await asyncio.sleep(0.3)

    (TMP_DIR / "stop.flag").write_text("stop", encoding="utf-8")
    await asyncio.wait_for(worker_proc.wait(), timeout=10.0)
    await nc.drain()

    # Verify recovered Parquet rows & atomic temp hygiene
    pq_glob = (TMP_DIR / "parquet" / "*.parquet").as_posix()
    orphan_tmps = list((TMP_DIR / "parquet").glob("*.tmp"))
    con = duckdb.connect(":memory:")
    distinct_cnt, raw_cnt = con.execute(
        f"SELECT COUNT(DISTINCT event_id), COUNT(*) FROM read_parquet('{pq_glob}')"
    ).fetchone()
    con.close()

    nats_stats = await asyncio.to_thread(
        subprocess.run,
        ["docker", "stats", "fmdp-poc-nats", "--no-stream", "--format", "{{json .}}"],
        capture_output=True,
        text=True,
        check=False,
    )
    nats_mem = nats_stats.stdout.strip().splitlines()[0] if nats_stats.stdout.strip() else "{}"

    max_coord_mb = max(s["coord_mb"] for s in rss_samples)
    max_worker_mb = max(s["worker_mb"] for s in rss_samples)
    report: dict[str, Any] = {
        "probe": "POC-04",
        "published_events": total_events,
        "recovered_distinct_parquet_rows": distinct_cnt,
        "recovered_total_parquet_rows": raw_cnt,
        "zero_loss": distinct_cnt == total_events,
        "orphan_tmp_files": len(orphan_tmps),
        "sigkill_injected_and_recovered": killed_once and (distinct_cnt == total_events),
        "peak_coordinator_rss_mb": max_coord_mb,
        "peak_worker_rss_mb": max_worker_mb,
        "combined_python_rss_peak_mb": round(max_coord_mb + max_worker_mb, 2),
        "nats_container_stats": json.loads(nats_mem),
        "pub_batch_before_ms_max": round(max(pub_lat_before_query_ms), 2),
        "pub_batch_after_ms_max": round(max(pub_lat_during_query_ms), 2),
    }
    (RESULTS_DIR / "poc_04_combined.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    if "--worker" in sys.argv:
        asyncio.run(_worker_loop())
    else:
        asyncio.run(_run_coordinator())
