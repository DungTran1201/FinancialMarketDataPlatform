"""POC-01: NATS JetStream throughput, latency, ACK/NAK, DLQ, restart durability & replay."""

from __future__ import annotations

import asyncio
import json
import os
import statistics
import subprocess
import time
from pathlib import Path
from typing import Any

import nats
import psutil
from nats.errors import Error as NatsError
from nats.js.api import ConsumerConfig, DeliverPolicy, RetentionPolicy, StorageType, StreamConfig
from nats.js.errors import NotFoundError

RESULTS_DIR = Path(__file__).resolve().parent / "results"
NATS_URL = os.environ.get("FMDP_POC_NATS_URL", "nats://127.0.0.1:4222")
CONTAINER_NAME = "fmdp-poc-nats"


def _pct(vals: list[float], q: float) -> float:
    if not vals:
        return 0.0
    s = sorted(vals)
    idx = min(len(s) - 1, max(0, int((len(s) - 1) * q)))
    return round(s[idx], 3)


def _docker_stats(container: str) -> dict[str, Any]:
    proc = subprocess.run(
        ["docker", "stats", container, "--no-stream", "--format", "{{json .}}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0 or not proc.stdout.strip():
        return {"error": proc.stderr.strip() or "docker stats unavailable"}
    return json.loads(proc.stdout.strip().splitlines()[0])


async def run_benchmark() -> dict[str, Any]:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    proc = psutil.Process()
    report: dict[str, Any] = {
        "probe": "POC-01",
        "nats_url": NATS_URL,
        "nats_py_version": nats.__version__,
        "stats_before": _docker_stats(CONTAINER_NAME),
    }

    nc = await nats.connect(NATS_URL, max_reconnect_attempts=30, reconnect_time_wait=0.5)
    js = nc.jetstream()

    # Clean old test streams cleanly
    for sname in ("MKT_POC", "MKT_POC_DLQ"):
        try:
            await js.delete_stream(sname)
        except NotFoundError:
            print(f"Stream {sname} not present; creating fresh.")

    await js.add_stream(
        StreamConfig(
            name="MKT_POC",
            subjects=["mkt.poc.>"],
            retention=RetentionPolicy.LIMITS,
            storage=StorageType.FILE,
            max_bytes=256 * 1024 * 1024,
            duplicate_window=60.0,
        )
    )
    await js.add_stream(
        StreamConfig(
            name="MKT_POC_DLQ",
            subjects=["mkt.dlq.>"],
            retention=RetentionPolicy.LIMITS,
            storage=StorageType.FILE,
            max_bytes=32 * 1024 * 1024,
        )
    )

    # Phase A: Sustained throughput & E2E latency on 20,000 realistic ~420-byte envelopes
    total_msgs = 20_000
    sub_pull = await js.pull_subscribe(
        "mkt.poc.trade",
        durable="poc_bench_pull",
        config=ConsumerConfig(
            durable_name="poc_bench_pull",
            ack_wait=5.0,
            max_deliver=4,
            max_ack_pending=500,
        ),
    )

    latencies_ms: list[float] = []
    seen_ids: set[int] = set()
    t0 = time.perf_counter()

    async def publisher() -> None:
        sem = asyncio.Semaphore(200)

        async def pub_one(seq_i: int) -> None:
            payload = json.dumps(
                {
                    "schema_version": "1.0.0",
                    "seq_id": seq_i,
                    "instrument_id": "binance:perp:BTC/USDT",
                    "exchange": "binance",
                    "contract_type": "PERPETUAL",
                    "price": "89421.50",
                    "qty": "0.02450",
                    "side": "BUY" if seq_i % 2 == 0 else "SELL",
                    "sent_ns": time.time_ns(),
                    "pad": "x" * 160,
                }
            ).encode()
            async with sem:
                await js.publish("mkt.poc.trade", payload, headers={"Nats-Msg-Id": f"id-{seq_i}"})

        batch = 500
        for start in range(0, total_msgs, batch):
            await asyncio.gather(*(pub_one(i) for i in range(start, min(total_msgs, start + batch))))

    async def consumer() -> None:
        while len(seen_ids) < total_msgs:
            try:
                msgs = await sub_pull.fetch(250, timeout=2.0)
            except TimeoutError:
                continue
            now_ns = time.time_ns()
            for msg in msgs:
                obj = json.loads(msg.data.decode())
                seen_ids.add(obj["seq_id"])
                latencies_ms.append((now_ns - obj["sent_ns"]) / 1_000_000.0)
                await msg.ack()

    await asyncio.gather(publisher(), consumer())
    elapsed_a = time.perf_counter() - t0
    report["phase_a_throughput"] = {
        "messages": total_msgs,
        "received_unique": len(seen_ids),
        "elapsed_sec": round(elapsed_a, 3),
        "msgs_per_sec": round(total_msgs / elapsed_a, 1),
        "e2e_latency_ms": {
            "p50": _pct(latencies_ms, 0.50),
            "p95": _pct(latencies_ms, 0.95),
            "p99": _pct(latencies_ms, 0.99),
            "max": round(max(latencies_ms), 3),
            "mean": round(statistics.fmean(latencies_ms), 3),
        },
    }

    # Phase B: NAK redelivery & DLQ quarantine on poison event
    dlq_sub = await js.pull_subscribe(
        "mkt.poc.poison",
        durable="poc_poison_pull",
        config=ConsumerConfig(durable_name="poc_poison_pull", ack_wait=1.0, max_deliver=3),
    )
    await js.publish("mkt.poc.poison", b'{"seq_id": -1, "poison": true}')
    deliveries = 0
    quarantined = False
    for _ in range(5):
        msgs = await dlq_sub.fetch(1, timeout=2.0)
        msg = msgs[0]
        deliveries += 1
        if msg.metadata.num_delivered >= 3:
            await js.publish("mkt.dlq.poison", msg.data, headers={"Reason": "MAX_DELIVER_EXCEEDED"})
            await msg.term()
            quarantined = True
            break
        await msg.nak()
    dlq_info = await js.stream_info("MKT_POC_DLQ")
    report["phase_b_nak_and_dlq"] = {
        "deliveries_observed": deliveries,
        "quarantined_to_dlq": quarantined,
        "dlq_stream_messages": dlq_info.state.messages,
    }

    # Phase C: Broker container restart & auto-reconnect + zero loss of unacked/restarted msgs
    pre_restart = 1000
    post_restart = 1000
    restart_sub = await js.pull_subscribe(
        "mkt.poc.restart",
        durable="poc_restart_pull",
        config=ConsumerConfig(durable_name="poc_restart_pull", ack_wait=3.0, max_ack_pending=500),
    )
    for i in range(pre_restart):
        await js.publish("mkt.poc.restart", json.dumps({"idx": i}).encode())

    # Consume half before restart
    pre_ids: set[int] = set()
    while len(pre_ids) < 400:
        batch_msgs = await restart_sub.fetch(200, timeout=2.0)
        for m in batch_msgs:
            pre_ids.add(json.loads(m.data.decode())["idx"])
            await m.ack()

    t_rst = time.perf_counter()
    rst_proc = await asyncio.to_thread(
        subprocess.run,
        ["docker", "restart", CONTAINER_NAME],
        capture_output=True,
        text=True,
        check=False,
    )
    reconnect_sec = round(time.perf_counter() - t_rst, 3)

    # Wait briefly until NATS Python client reports connected again and publish post_restart messages
    for _ in range(40):
        if nc.is_connected:
            try:
                await js.stream_info("MKT_POC")
                break
            except (NatsError, TimeoutError):
                await asyncio.sleep(0.1)
        await asyncio.sleep(0.25)

    for i in range(pre_restart, pre_restart + post_restart):
        await js.publish("mkt.poc.restart", json.dumps({"idx": i}).encode())

    all_restart_ids = set(pre_ids)
    deadline = time.perf_counter() + 20.0
    while len(all_restart_ids) < (pre_restart + post_restart) and time.perf_counter() < deadline:
        try:
            batch_msgs = await restart_sub.fetch(250, timeout=1.5)
            for m in batch_msgs:
                all_restart_ids.add(json.loads(m.data.decode())["idx"])
                await m.ack()
        except (NatsError, TimeoutError):
            await asyncio.sleep(0.2)

    report["phase_c_container_restart"] = {
        "docker_restart_exit": rst_proc.returncode,
        "restart_elapsed_sec": reconnect_sec,
        "expected_total": pre_restart + post_restart,
        "received_unique_total": len(all_restart_ids),
        "zero_loss": len(all_restart_ids) == (pre_restart + post_restart),
    }

    # Phase D: Full replay verification on MKT_POC from sequence 1
    replay_sub = await js.pull_subscribe(
        "mkt.poc.trade",
        config=ConsumerConfig(deliver_policy=DeliverPolicy.ALL, ack_wait=5.0, max_ack_pending=1000),
    )
    replayed_ids: set[int] = set()
    deadline_rep = time.perf_counter() + 20.0
    while len(replayed_ids) < total_msgs and time.perf_counter() < deadline_rep:
        try:
            msgs = await replay_sub.fetch(500, timeout=1.5)
            for m in msgs:
                replayed_ids.add(json.loads(m.data.decode())["seq_id"])
                await m.ack()
        except TimeoutError:
            break

    report["phase_d_replay"] = {
        "replayed_unique": len(replayed_ids),
        "replay_exact_match": replayed_ids == seen_ids,
    }
    report["stats_after"] = _docker_stats(CONTAINER_NAME)
    report["python_client_rss_mb"] = round(proc.memory_info().rss / (1024 * 1024), 2)

    await nc.drain()
    out_file = RESULTS_DIR / "poc_01_nats.json"
    out_file.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    asyncio.run(run_benchmark())
