"""Reporting domain ports (Pure Domain Layer)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class ProvenanceCitation:
    """Verifiable link to a deterministic tool invocation and underlying data window."""

    invocation_id: str
    tool_name: str
    source_store: str
    symbol: str
    window_start: datetime
    window_end: datetime
    row_count: int


@dataclass(frozen=True, slots=True)
class StructuredAnalysisReport:
    """Canonical structured intelligence report backed by deterministic tool citations."""

    run_id: str
    symbol: str
    summary: str
    quantitative_evidence: dict[str, Any]
    anomalies_detected: tuple[str, ...]
    data_quality_status: str
    provenance_citations: tuple[ProvenanceCitation, ...]
    limitations_disclaimer: str


class ReportRepositoryPort(Protocol):
    """Port for reading completed structured reports from PostgreSQL."""

    async def get_report_by_run_id(self, run_id: str) -> StructuredAnalysisReport | None: ...

