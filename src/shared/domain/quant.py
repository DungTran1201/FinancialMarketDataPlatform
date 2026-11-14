"""Pure deterministic quantitative finance computations shared across Serving and Intelligence."""

from __future__ import annotations

import math


def compute_deterministic_log_returns(prices: list[float]) -> list[float]:
    """Deterministic Python calculation of log returns (never delegated to LLM math)."""
    if len(prices) < 2:
        return []
    returns: list[float] = []
    for idx in range(1, len(prices)):
        prev_p = prices[idx - 1]
        curr_p = prices[idx]
        if prev_p <= 0 or curr_p <= 0:
            raise ValueError("Prices must be strictly positive for log return calculation")
        returns.append(math.log(curr_p / prev_p))
    return returns


def compute_deterministic_realized_volatility(
    prices: list[float],
    periods_per_year: int = 365 * 24,
) -> float:
    """Deterministic calculation of annualized realized volatility from price series."""
    log_returns = compute_deterministic_log_returns(prices)
    if len(log_returns) < 2:
        return 0.0
    mean_ret = sum(log_returns) / len(log_returns)
    variance = sum((r - mean_ret) ** 2 for r in log_returns) / (len(log_returns) - 1)
    return math.sqrt(variance * periods_per_year)


def compute_deterministic_pearson_correlation(
    prices_a: list[float],
    prices_b: list[float],
) -> float:
    """Deterministic Pearson correlation coefficient between two return series."""
    ret_a = compute_deterministic_log_returns(prices_a)
    ret_b = compute_deterministic_log_returns(prices_b)
    n = min(len(ret_a), len(ret_b))
    if n < 2:
        return 0.0
    ra = ret_a[-n:]
    rb = ret_b[-n:]
    mean_a = sum(ra) / n
    mean_b = sum(rb) / n
    cov = sum((ra[i] - mean_a) * (rb[i] - mean_b) for i in range(n))
    std_a = math.sqrt(sum((x - mean_a) ** 2 for x in ra))
    std_b = math.sqrt(sum((y - mean_b) ** 2 for y in rb))
    if std_a <= 1e-12 or std_b <= 1e-12:
        return 0.0
    return round(cov / (std_a * std_b), 6)
