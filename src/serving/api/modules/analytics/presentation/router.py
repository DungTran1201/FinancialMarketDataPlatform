"""Analytics Presentation Layer (`API-007` — Statistics, Correlations & Anomalies)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from src.shared.domain.quant import compute_deterministic_pearson_correlation

try:
    from fastapi import APIRouter, Body, HTTPException, Query
except ModuleNotFoundError:  # pragma: no cover
    APIRouter = Any  # type: ignore[misc,assignment]
    Body = None  # type: ignore[assignment]
    HTTPException = Exception  # type: ignore[misc,assignment]
    Query = None  # type: ignore[assignment]

if TYPE_CHECKING:
    from src.serving.infrastructure.runtime import PlatformRuntimeContainer


def build_analytics_router(runtime: PlatformRuntimeContainer) -> Any:
    """Build the FastAPI APIRouter for the Analytics domain (`API-007`)."""
    router = APIRouter()

    @router.get("/statistics/{symbol}")
    async def get_symbol_statistics(
        symbol: str,
        provider: str = "binance",
        window: str = "24h",
    ) -> dict[str, Any]:
        summary = runtime.get_market_statistics_summary(provider=provider.lower(), symbol=symbol.upper(), window=window)
        if summary is None:
            raise HTTPException(
                status_code=404,
                detail={"code": "ERR_ANALYTICS_NOT_FOUND", "message": f"No analytics for {symbol}"},
            )
        return {
            "data": {
                "provider": summary.instrument.provider,
                "symbol": summary.instrument.symbol,
                "window": summary.window,
                "vwap": str(summary.vwap),
                "realized_volatility": str(summary.realized_volatility),
                "total_base_volume": str(summary.total_base_volume),
                "total_quote_volume": str(summary.total_quote_volume),
                "trade_count": summary.trade_count,
            },
            "meta": {"source": "clickhouse_mv_rollup"},
        }

    @router.get("/correlations")
    async def get_symbol_correlations(
        symbols: str = Query(default="BTCUSDT,ETHUSDT,SOLUSDT"),
        provider: str = "binance",
    ) -> dict[str, Any]:
        sym_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
        series_map: dict[str, list[float]] = {}
        for sym in sym_list:
            st = runtime.clickhouse_sink.compute_aggregated_statistics(provider.lower(), sym)
            series_map[sym] = list(st.get("close_prices", [])) if st else []

        matrix: dict[str, dict[str, float]] = {}
        for s1 in sym_list:
            matrix[s1] = {}
            for s2 in sym_list:
                if s1 == s2:
                    matrix[s1][s2] = 1.0
                else:
                    matrix[s1][s2] = compute_deterministic_pearson_correlation(
                        series_map.get(s1, []), series_map.get(s2, [])
                    )
        return {
            "data": {"symbols": sym_list, "matrix": matrix},
            "meta": {"source": "clickhouse_olap_deterministic_math"},
        }

    @router.get("/anomalies")
    async def get_detected_anomalies(symbol: str | None = None) -> dict[str, Any]:
        items = [
            {
                "provider": a.provider,
                "symbol": a.symbol,
                "detector": a.detector_name,
                "z_score": a.z_score,
                "threshold": a.threshold,
                "latest_value": a.latest_value,
                "mean_value": a.mean_value,
                "std_dev": a.std_dev,
                "detected_at": a.detected_at.isoformat(),
            }
            for a in runtime.detected_anomalies
            if symbol is None or a.symbol == symbol.upper()
        ]
        return {"data": items, "meta": {"count": len(items)}}

    @router.post("/anomalies/evaluate")
    async def evaluate_series_for_anomalies(
        payload: dict[str, Any] = Body(...),
    ) -> dict[str, Any]:
        provider = str(payload.get("provider", "binance")).lower()
        symbol = str(payload.get("symbol", "BTCUSDT")).upper()
        values = [float(v) for v in payload.get("values", [])]
        detector_name = str(payload.get("detector_name", "return_zscore"))
        ts_str = payload.get("timestamp")
        now_utc = datetime.fromisoformat(str(ts_str)) if ts_str else datetime.now(UTC)

        env, anom = runtime.anomaly_detector.evaluate_series(
            provider=provider,
            symbol=symbol,
            values=values,
            detector_name=detector_name,
            now_utc=now_utc,
        )
        if env is not None and anom is not None:
            runtime.detected_anomalies.append(anom)
            await runtime.kafka_broker.publish_event("market.anomalies.v1", env)
        return {
            "data": {
                "provider": provider,
                "symbol": symbol,
                "anomaly_emitted": anom is not None,
                "z_score": anom.z_score if anom else 0.0,
                "suppressed_alerts_total": runtime.anomaly_detector.suppressed_alerts_count,
            }
        }

    return router
