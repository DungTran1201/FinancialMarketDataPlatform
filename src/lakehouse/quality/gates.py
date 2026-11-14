"""Declarative Great Expectations Suite Specifications & Deterministic Decimal Quality Gate Engine."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any


class QualityGateBlockedError(RuntimeError):
    """Raised when critical data quality rules fail and block promotion to the Gold layer."""


@dataclass(frozen=True, slots=True)
class QualityExpectationRule:
    """Represents a mandatory financial data quality invariant."""

    rule_id: str
    dataset: str
    expression: str
    severity: str  # CRITICAL | WARNING


MANDATORY_KLINE_QUALITY_RULES: tuple[QualityExpectationRule, ...] = (
    QualityExpectationRule(
        rule_id="DQ-KLINE-001",
        dataset="silver.market_klines",
        expression="high_price >= low_price",
        severity="CRITICAL",
    ),
    QualityExpectationRule(
        rule_id="DQ-KLINE-002",
        dataset="silver.market_klines",
        expression=(
            "high_price >= open_price AND high_price >= close_price "
            "AND low_price <= open_price AND low_price <= close_price"
        ),
        severity="CRITICAL",
    ),
    QualityExpectationRule(
        rule_id="DQ-KLINE-003",
        dataset="silver.market_klines",
        expression="base_volume >= 0 AND quote_volume >= 0",
        severity="CRITICAL",
    ),
    QualityExpectationRule(
        rule_id="DQ-KLINE-004",
        dataset="silver.market_klines",
        expression="UNIQUE(provider, symbol, interval, open_time)",
        severity="CRITICAL",
    ),
    QualityExpectationRule(
        rule_id="DQ-KLINE-005",
        dataset="silver.market_klines",
        expression="close_time > open_time AND open_price > 0 AND close_price > 0",
        severity="CRITICAL",
    ),
)

MANDATORY_TRADE_QUALITY_RULES: tuple[QualityExpectationRule, ...] = (
    QualityExpectationRule(
        rule_id="DQ-TRADE-001",
        dataset="silver.market_trades",
        expression="price > 0 AND quantity > 0",
        severity="CRITICAL",
    ),
    QualityExpectationRule(
        rule_id="DQ-TRADE-002",
        dataset="silver.market_trades",
        expression="abs(quote_volume - (price * quantity)) <= 0.01",
        severity="CRITICAL",
    ),
    QualityExpectationRule(
        rule_id="DQ-TRADE-003",
        dataset="silver.market_trades",
        expression="UNIQUE(provider, symbol, trade_id)",
        severity="CRITICAL",
    ),
)


@dataclass(frozen=True, slots=True)
class QualityGateValidationResult:
    """Result of evaluating a dataset against mandatory financial quality rules."""

    dataset: str
    total_rows: int
    passed: bool
    can_promote_to_gold: bool
    failed_rule_ids: tuple[str, ...]
    violations_detail: tuple[str, ...]


class DataQualityGateEngine:
    """Executes `MANDATORY_KLINE_QUALITY_RULES` and `MANDATORY_TRADE_QUALITY_RULES` using exact `Decimal` math."""

    def validate_kline_dataset(
        self,
        rows: list[dict[str, Any]],
        dataset_name: str = "silver.market_klines",
    ) -> QualityGateValidationResult:
        failed_rules: set[str] = set()
        details: list[str] = []
        seen_keys: set[tuple[str, str, str, str]] = set()
        zero = Decimal("0")

        for idx, row in enumerate(rows):
            open_p = Decimal(str(row["open_price"]))
            high_p = Decimal(str(row["high_price"]))
            low_p = Decimal(str(row["low_price"]))
            close_p = Decimal(str(row["close_price"]))
            base_v = Decimal(str(row["base_volume"]))
            quote_v = Decimal(str(row["quote_volume"]))
            open_t = str(row.get("open_time", ""))
            close_t = str(row.get("close_time", ""))

            if high_p < low_p:
                failed_rules.add("DQ-KLINE-001")
                details.append(f"Row {idx}: high_price ({high_p}) < low_price ({low_p})")

            if high_p < open_p or high_p < close_p or low_p > open_p or low_p > close_p:
                failed_rules.add("DQ-KLINE-002")
                details.append(f"Row {idx}: OHLC envelope violated")

            if base_v < zero or quote_v < zero:
                failed_rules.add("DQ-KLINE-003")
                details.append(f"Row {idx}: negative volume detected")

            if open_p <= zero or close_p <= zero or (close_t and open_t and close_t <= open_t):
                failed_rules.add("DQ-KLINE-005")
                details.append(f"Row {idx}: non-positive price or invalid candle window ({open_t}..{close_t})")

            nat_key = (
                str(row["provider"]).lower(),
                str(row["symbol"]).upper(),
                str(row.get("interval", "1m")),
                open_t,
            )
            if nat_key in seen_keys:
                failed_rules.add("DQ-KLINE-004")
                details.append(f"Row {idx}: duplicate natural key {nat_key}")
            seen_keys.add(nat_key)

        passed = len(failed_rules) == 0
        return QualityGateValidationResult(
            dataset=dataset_name,
            total_rows=len(rows),
            passed=passed,
            can_promote_to_gold=passed,
            failed_rule_ids=tuple(sorted(failed_rules)),
            violations_detail=tuple(details),
        )

    def validate_trade_dataset(
        self,
        rows: list[dict[str, Any]],
        dataset_name: str = "silver.market_trades",
    ) -> QualityGateValidationResult:
        failed_rules: set[str] = set()
        details: list[str] = []
        seen_keys: set[tuple[str, str, int]] = set()
        zero = Decimal("0")
        tolerance = Decimal("0.01")

        for idx, row in enumerate(rows):
            price = Decimal(str(row["price"]))
            qty = Decimal(str(row["quantity"]))
            quote_vol = Decimal(str(row["quote_volume"]))
            trade_id = int(row["trade_id"])

            if price <= zero or qty <= zero:
                failed_rules.add("DQ-TRADE-001")
                details.append(f"Row {idx}: non-positive price ({price}) or quantity ({qty})")

            if abs(quote_vol - (price * qty)) > tolerance:
                failed_rules.add("DQ-TRADE-002")
                details.append(
                    f"Row {idx}: quote_volume ({quote_vol}) != price * quantity ({price * qty})"
                )

            nat_key = (
                str(row["provider"]).lower(),
                str(row["symbol"]).upper(),
                trade_id,
            )
            if nat_key in seen_keys:
                failed_rules.add("DQ-TRADE-003")
                details.append(f"Row {idx}: duplicate trade key {nat_key}")
            seen_keys.add(nat_key)

        passed = len(failed_rules) == 0
        return QualityGateValidationResult(
            dataset=dataset_name,
            total_rows=len(rows),
            passed=passed,
            can_promote_to_gold=passed,
            failed_rule_ids=tuple(sorted(failed_rules)),
            violations_detail=tuple(details),
        )
