"""Binance & Multi-Provider Canonical Payload Normalizer & Contract Validator (Plane A)."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from src.collectors.ports import PayloadNormalizerPort
from src.shared.contracts.events import (
    SCHEMA_VERSION_V1,
    DeadLetterEnvelopeV1,
    EventEnvelopeV1,
    EventType,
    MarketKlinePayloadV1,
    MarketTradePayloadV1,
    compute_deterministic_event_id,
)


class NormalizationError(ValueError):
    """Raised when a raw provider payload cannot be normalized into EventEnvelopeV1."""


class BinancePayloadNormalizer(PayloadNormalizerPort):
    """Translates raw Binance WS/REST payloads into validated canonical EventEnvelopeV1 objects."""

    @property
    def provider_name(self) -> str:
        return "binance"

    def normalize_ws_message(
        self,
        raw_message: dict[str, Any],
        ingested_at: datetime | None = None,
    ) -> EventEnvelopeV1:
        now_utc = ingested_at or datetime.now(UTC)
        if now_utc.tzinfo is None:
            raise NormalizationError("ingested_at must be timezone-aware UTC.")

        event_kind = str(raw_message.get("e", "")).lower()
        symbol = str(raw_message.get("s", "")).upper().strip()
        if not symbol:
            raise NormalizationError("Missing symbol ('s') in provider message.")

        event_ts_ms = int(raw_message.get("E") or int(now_utc.timestamp() * 1000))
        exchange_event_time = datetime.fromtimestamp(event_ts_ms / 1000.0, tz=UTC)

        if event_kind == "trade":
            try:
                trade_id = int(raw_message["t"])
                price = Decimal(str(raw_message["p"]))
                qty = Decimal(str(raw_message["q"]))
                quote_vol = Decimal(str(raw_message.get("Q") or (price * qty)))
                trade_ts_ms = int(raw_message.get("T") or event_ts_ms)
                trade_time = datetime.fromtimestamp(trade_ts_ms / 1000.0, tz=UTC)
                is_buyer_maker = bool(raw_message.get("m", False))
                validated = MarketTradePayloadV1(
                    trade_id=trade_id,
                    price=price,
                    quantity=qty,
                    quote_volume=quote_vol,
                    trade_time=trade_time,
                    is_buyer_maker=is_buyer_maker,
                    buyer_order_id=int(raw_message.get("b", 0)),
                    seller_order_id=int(raw_message.get("a", 0)),
                )
            except Exception as exc:
                raise NormalizationError(f"Invalid trade payload: {exc}") from exc

            event_id = compute_deterministic_event_id(
                self.provider_name, EventType.TRADE, symbol, str(validated.trade_id)
            )
            return EventEnvelopeV1(
                event_id=event_id,
                schema_version=SCHEMA_VERSION_V1,
                provider=self.provider_name,
                symbol=symbol,
                event_type=EventType.TRADE,
                exchange_event_time=exchange_event_time,
                ingested_at=now_utc,
                payload={
                    "trade_id": validated.trade_id,
                    "price": str(validated.price),
                    "quantity": str(validated.quantity),
                    "quote_volume": str(validated.quote_volume),
                    "trade_time": validated.trade_time.isoformat(),
                    "is_buyer_maker": validated.is_buyer_maker,
                    "buyer_order_id": validated.buyer_order_id,
                    "seller_order_id": validated.seller_order_id,
                },
            )

        if event_kind == "kline":
            k = raw_message.get("k")
            if not isinstance(k, dict):
                raise NormalizationError("Missing kline object ('k') in kline message.")
            try:
                interval = str(k.get("i", "1m"))
                open_time = datetime.fromtimestamp(int(k["t"]) / 1000.0, tz=UTC)
                close_time = datetime.fromtimestamp(int(k["T"]) / 1000.0, tz=UTC)
                validated_k = MarketKlinePayloadV1(
                    interval=interval,
                    open_time=open_time,
                    close_time=close_time,
                    open_price=Decimal(str(k["o"])),
                    high_price=Decimal(str(k["h"])),
                    low_price=Decimal(str(k["l"])),
                    close_price=Decimal(str(k["c"])),
                    base_volume=Decimal(str(k["v"])),
                    quote_volume=Decimal(str(k["q"])),
                    trade_count=int(k.get("n", 0)),
                    taker_buy_base_volume=Decimal(str(k.get("V", "0"))),
                    taker_buy_quote_volume=Decimal(str(k.get("Q", "0"))),
                    is_closed=bool(k.get("x", False)),
                )
            except Exception as exc:
                raise NormalizationError(f"Invalid kline payload: {exc}") from exc

            natural_key = f"{validated_k.interval}:{int(validated_k.open_time.timestamp() * 1000)}"
            event_id = compute_deterministic_event_id(self.provider_name, EventType.KLINE, symbol, natural_key)
            return EventEnvelopeV1(
                event_id=event_id,
                schema_version=SCHEMA_VERSION_V1,
                provider=self.provider_name,
                symbol=symbol,
                event_type=EventType.KLINE,
                exchange_event_time=exchange_event_time,
                ingested_at=now_utc,
                payload={
                    "interval": validated_k.interval,
                    "open_time": validated_k.open_time.isoformat(),
                    "close_time": validated_k.close_time.isoformat(),
                    "open_price": str(validated_k.open_price),
                    "high_price": str(validated_k.high_price),
                    "low_price": str(validated_k.low_price),
                    "close_price": str(validated_k.close_price),
                    "base_volume": str(validated_k.base_volume),
                    "quote_volume": str(validated_k.quote_volume),
                    "trade_count": validated_k.trade_count,
                    "taker_buy_base_volume": str(validated_k.taker_buy_base_volume),
                    "taker_buy_quote_volume": str(validated_k.taker_buy_quote_volume),
                    "is_closed": validated_k.is_closed,
                },
            )

        if event_kind in ("24hrticker", "ticker"):
            last_price = Decimal(str(raw_message.get("c", "0")))
            if last_price <= Decimal("0"):
                raise NormalizationError("Ticker last_price must be > 0.")
            event_id = compute_deterministic_event_id(self.provider_name, EventType.TICKER, symbol, str(event_ts_ms))
            return EventEnvelopeV1(
                event_id=event_id,
                schema_version=SCHEMA_VERSION_V1,
                provider=self.provider_name,
                symbol=symbol,
                event_type=EventType.TICKER,
                exchange_event_time=exchange_event_time,
                ingested_at=now_utc,
                payload={
                    "last_price": str(last_price),
                    "best_bid_price": str(Decimal(str(raw_message.get("b", last_price)))),
                    "best_ask_price": str(Decimal(str(raw_message.get("a", last_price)))),
                    "high_24h": str(Decimal(str(raw_message.get("h", last_price)))),
                    "low_24h": str(Decimal(str(raw_message.get("l", last_price)))),
                    "vwap_24h": str(Decimal(str(raw_message.get("w", last_price)))),
                    "price_change_pct_24h": str(Decimal(str(raw_message.get("P", "0")))),
                    "base_volume_24h": str(Decimal(str(raw_message.get("v", "0")))),
                    "quote_volume_24h": str(Decimal(str(raw_message.get("q", "0")))),
                },
            )

        raise NormalizationError(f"Unsupported Binance event kind: '{event_kind}'")

    def normalize_or_route_dlq(
        self,
        raw_message: dict[str, Any],
        source_topic: str,
        ingested_at: datetime | None = None,
    ) -> tuple[EventEnvelopeV1 | None, DeadLetterEnvelopeV1 | None]:
        """Validate and normalize raw message, or wrap failure in a DeadLetterEnvelopeV1."""
        now_utc = ingested_at or datetime.now(UTC)
        try:
            envelope = self.normalize_ws_message(raw_message, ingested_at=now_utc)
            return envelope, None
        except Exception as exc:
            dlq = DeadLetterEnvelopeV1(
                dlq_id=str(compute_deterministic_event_id(self.provider_name, "dlq", source_topic, str(raw_message))),
                source_provider=self.provider_name,
                source_stream=source_topic,
                error_type=type(exc).__name__,
                error_message=str(exc),
                raw_payload=str(raw_message),
                failed_at=now_utc,
            )
            return None, dlq
