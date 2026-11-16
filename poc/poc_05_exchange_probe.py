"""POC-05: Read-only Binance & OKX Public API & Schema/Rate-Limit Capability Probe."""

from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import Any

import httpx
import websockets

RESULTS_DIR = Path(__file__).resolve().parent / "results"


async def probe_rest(client: httpx.AsyncClient, name: str, url: str) -> dict[str, Any]:
    t0 = time.perf_counter()
    try:
        resp = await client.get(url, timeout=10.0)
        elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 2)
        out: dict[str, Any] = {
            "name": name,
            "url": url,
            "status_code": resp.status_code,
            "latency_ms": elapsed_ms,
            "rate_headers": {
                k: v
                for k, v in resp.headers.items()
                if "weight" in k.lower() or "limit" in k.lower() or "ratelimit" in k.lower()
            },
        }
        if resp.status_code == 200:
            data = resp.json()
            if name in ("binance_spot_info", "binance_fapi_info", "binance_dapi_info"):
                syms = data.get("symbols", [])
                contracts = {s.get("contractType", "SPOT") for s in syms}
                btc = [s for s in syms if str(s.get("symbol", "")).startswith("BTCUSD")][:3]
                out["sample"] = {
                    "total_symbols": len(syms),
                    "contract_types_present": sorted(contracts),
                    "btc_samples": [
                        {
                            "symbol": s.get("symbol"),
                            "contractType": s.get("contractType"),
                            "status": s.get("status") or s.get("contractStatus"),
                        }
                        for s in btc
                    ],
                    "rate_limits": data.get("rateLimits", [])[:3],
                }
            elif name == "binance_fapi_oi":
                out["sample"] = data
            elif name.startswith("okx_") and "funding" not in name:
                items = data.get("data", [])
                out["sample"] = {
                    "total_instruments": len(items),
                    "samples": [
                        {
                            "instId": x.get("instId"),
                            "instType": x.get("instType"),
                            "ctVal": x.get("ctVal"),
                            "ctValCcy": x.get("ctValCcy"),
                            "expTime": x.get("expTime"),
                            "tickSz": x.get("tickSz"),
                            "lotSz": x.get("lotSz"),
                        }
                        for x in items[:3]
                    ],
                }
            else:
                out["sample"] = data.get("data", data)[:2] if isinstance(data, dict) else data[:2]
        return out
    except (httpx.HTTPError, ValueError) as exc:
        return {"name": name, "url": url, "error": f"{type(exc).__name__}: {exc}"}


async def probe_ws(name: str, uri: str, sub_msg: str | None) -> dict[str, Any]:
    t0 = time.perf_counter()
    try:
        async with websockets.connect(uri, open_timeout=8.0, close_timeout=2.0) as ws:
            if sub_msg:
                await ws.send(sub_msg)
            frames: list[dict[str, Any]] = []
            notices: list[dict[str, Any]] = []
            for _ in range(8):
                raw = await asyncio.wait_for(ws.recv(), timeout=6.0)
                obj = json.loads(raw)
                if obj.get("event") in ("subscribe", "notice"):
                    notices.append(obj)
                    continue
                frames.append(obj)
                if len(frames) >= 2:
                    break
            return {
                "name": name,
                "uri": uri,
                "connected": True,
                "elapsed_ms": round((time.perf_counter() - t0) * 1000.0, 2),
                "notices": notices,
                "data_frame_keys": list(frames[0].keys()) if frames else [],
                "sample_data": frames[0] if frames else None,
            }
    except (OSError, TimeoutError, websockets.WebSocketException, ValueError) as exc:
        return {"name": name, "uri": uri, "connected": False, "error": f"{type(exc).__name__}: {exc}"}


async def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    async with httpx.AsyncClient() as client:
        rest_results = await asyncio.gather(
            probe_rest(client, "binance_spot_info", "https://api.binance.com/api/v3/exchangeInfo?symbol=BTCUSDT"),
            probe_rest(client, "binance_fapi_info", "https://fapi.binance.com/fapi/v1/exchangeInfo"),
            probe_rest(client, "binance_dapi_info", "https://dapi.binance.com/dapi/v1/exchangeInfo"),
            probe_rest(client, "binance_fapi_oi", "https://fapi.binance.com/fapi/v1/openInterest?symbol=BTCUSDT"),
            probe_rest(client, "okx_spot_info", "https://www.okx.com/api/v5/public/instruments?instType=SPOT&instId=BTC-USDT"),
            probe_rest(client, "okx_swap_info", "https://www.okx.com/api/v5/public/instruments?instType=SWAP&instId=BTC-USDT-SWAP"),
            probe_rest(client, "okx_futures_info", "https://www.okx.com/api/v5/public/instruments?instType=FUTURES"),
            probe_rest(client, "okx_option_info", "https://www.okx.com/api/v5/public/instruments?instType=OPTION&uly=BTC-USD"),
            probe_rest(client, "okx_swap_funding", "https://www.okx.com/api/v5/public/funding-rate?instId=BTC-USDT-SWAP"),
        )

    ws_results = await asyncio.gather(
        probe_ws("binance_spot_ws_depth", "wss://stream.binance.com:9443/ws/btcusdt@depth@100ms", None),
        probe_ws("binance_fapi_ws_depth", "wss://fstream.binance.com/ws/btcusdt@depth@100ms", None),
        probe_ws(
            "okx_swap_ws_books_443",
            "wss://ws.okx.com:443/ws/v5/public",
            json.dumps({"op": "subscribe", "args": [{"channel": "books5", "instId": "BTC-USDT-SWAP"}]}),
        ),
    )

    report = {"probe": "POC-05", "rest": rest_results, "ws": ws_results}
    (RESULTS_DIR / "poc_05_exchanges.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
