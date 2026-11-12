"""Declarative Great Expectations suite specifications for Silver & Gold datasets."""

from __future__ import annotations

from dataclasses import dataclass


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

