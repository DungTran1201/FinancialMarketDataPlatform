"""Declarative Great Expectations Suite Specifications & Deterministic Quality Gate Engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


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
        expression="high_price >= open_price AND high_price >= close_price",
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
)


@dataclass(frozen=True, slots=True)
class QualityGateValidationResult:
    """Result of evaluating a dataset against `MANDATORY_KLINE_QUALITY_RULES`."""

    dataset: str
    total_rows: int
    passed: bool
    can_promote_to_gold: bool
    failed_rule_ids: tuple[str, ...]
    violations_detail: tuple[str, ...]


class DataQualityGateEngine:
    """Executes `MANDATORY_KLINE_QUALITY_RULES` (`DQ-KLINE-001..004`) before Gold promotion."""

    def validate_kline_dataset(
        self,
        rows: list[dict[str, Any]],
        dataset_name: str = "silver.market_klines",
    ) -> QualityGateValidationResult:
        failed_rules: set[str] = set()
        details: list[str] = []
        seen_keys: set[tuple[str, str, str, str]] = set()

        for idx, row in enumerate(rows):
            open_p = float(row["open_price"])
            high_p = float(row["high_price"])
            low_p = float(row["low_price"])
            close_p = float(row["close_price"])
            base_v = float(row["base_volume"])
            quote_v = float(row["quote_volume"])

            if high_p < low_p:
                failed_rules.add("DQ-KLINE-001")
                details.append(f"Row {idx}: high_price ({high_p}) < low_price ({low_p})")

            if high_p < open_p or high_p < close_p or low_p > open_p or low_p > close_p:
                failed_rules.add("DQ-KLINE-002")
                details.append(f"Row {idx}: OHLC envelope violated")

            if base_v < 0 or quote_v < 0:
                failed_rules.add("DQ-KLINE-003")
                details.append(f"Row {idx}: negative volume detected")

            nat_key = (
                str(row["provider"]).lower(),
                str(row["symbol"]).upper(),
                str(row.get("interval", "1m")),
                str(row["open_time"]),
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
