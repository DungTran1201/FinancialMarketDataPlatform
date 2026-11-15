"""Zero-Hallucination Intelligence Report Provenance Validator (`CTRL-002`)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.intelligence.tools.contracts import ToolExecutionEnvelope


class ReportProvenanceError(ValueError):
    """Raised when a synthesized report cites an invocation_id not present in evidence_trail."""


class ReportValidator:
    """Deterministic verifier ensuring every cited tool invocation exists in the run's evidence trail."""

    @staticmethod
    def validate_report(
        report: dict[str, Any],
        evidence_trail: list[ToolExecutionEnvelope],
    ) -> bool:
        valid_ids = {env.provenance.invocation_id for env in evidence_trail}
        citations = report.get("provenance_citations", [])
        if not citations:
            raise ReportProvenanceError("Report must contain at least one provenance citation.")
        for cit in citations:
            inv_id = cit.get("invocation_id") if isinstance(cit, dict) else getattr(cit, "invocation_id", None)
            if inv_id not in valid_ids:
                raise ReportProvenanceError(f"Fabricated or unknown tool invocation_id '{inv_id}' cited in report.")
        return True
