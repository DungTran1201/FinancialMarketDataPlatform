"""Unit and integration tests for Documentation V2 validator (scripts/docs/validate_docs.py)."""

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DOCS = REPO_ROOT / "scripts" / "docs"
if str(SCRIPTS_DOCS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DOCS))

from validate_docs import validate_repository  # noqa: E402


def _make_clean_sandbox(tmp_dir: Path) -> Path:
    """Copy Documentation V2 Phase 1 governance baseline into a temp sandbox repo."""
    docs_dir = tmp_dir / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(REPO_ROOT / "docs" / "governance", docs_dir / "governance")
    shutil.copy2(REPO_ROOT / "docs" / "README.md", docs_dir / "README.md")
    shutil.copy2(REPO_ROOT / "docs" / "docs-index.yaml", docs_dir / "docs-index.yaml")
    shutil.copy2(REPO_ROOT / "docker-compose.yml", tmp_dir / "docker-compose.yml")
    shutil.copy2(REPO_ROOT / "pyproject.toml", tmp_dir / "pyproject.toml")

    
    # Minimal stub migration disposition if test runs prior to cleanup or on subset
    mig_disp = docs_dir / "governance" / "migration" / "legacy-disposition.md"
    if not mig_disp.exists():
        mig_disp.write_text(
            "---\n"
            "doc_id: GOV-MIG-DISP-001\n"
            "title: 'Legacy Disposition Stub'\n"
            "doc_type: migration-report\n"
            "plane: governance\n"
            "scope_level: platform\n"
            "status: DRAFT\n"
            "implementation_status: NOT_APPLICABLE\n"
            "version: '0.1.0'\n"
            "owner_role: documentation-architect\n"
            "accountable_role: documentation-architect\n"
            "created_at: '2026-11-16'\n"
            "updated_at: '2026-11-16'\n"
            "source_of_truth:\n"
            "  is_authoritative: true\n"
            "  authoritative_source: ['docs/governance/migration/legacy-disposition.md']\n"
            "related_docs: ['GOV-MIG-INV-001']\n"
            "---\n\n"
            "# Legacy Disposition\n\n"
            "## 1. Scope\n\nStub for isolated sandbox.\n",
            encoding="utf-8",
        )

    # Create stub entrypoints referenced by docs-index.yaml
    (tmp_dir / "AGENTS.md").write_text("# Agents\n\nSee docs.\n", encoding="utf-8")
    (tmp_dir / ".agents").mkdir(exist_ok=True)
    (tmp_dir / ".agents" / "hooks.json").write_text("{}\n", encoding="utf-8")
    (tmp_dir / "scripts" / "docs").mkdir(parents=True, exist_ok=True)
    (tmp_dir / "scripts" / "docs" / "validate_docs.py").write_text("# stub\n", encoding="utf-8")
    (tmp_dir / "src" / "serving").mkdir(parents=True, exist_ok=True)
    (tmp_dir / "src" / "serving" / "ui_widget.py").write_text("# sample source\n", encoding="utf-8")
    (tmp_dir / "tests" / "unit").mkdir(parents=True, exist_ok=True)
    (tmp_dir / "tests" / "unit" / "test_widget.py").write_text("# sample test\n", encoding="utf-8")
    return tmp_dir


def _add_low_risk_ui_capability(sandbox: Path) -> Path:
    cap_rel = "docs/application-plane/domains/market-ui/capabilities/readonly-ticker-banner"
    cap_dir = sandbox / cap_rel
    (cap_dir / "design").mkdir(parents=True, exist_ok=True)
    (cap_dir / "quality").mkdir(parents=True, exist_ok=True)

    (cap_dir / "capability-specification.md").write_text(
        "---\n"
        "doc_id: APP-UI-CAP-001\n"
        "title: 'Read-Only Ticker Banner Capability Spec'\n"
        "doc_type: specification\n"
        "plane: application-plane\n"
        "scope_level: capability\n"
        "domain: market-ui\n"
        "capability_id: CAP-UI-001\n"
        "status: APPROVED\n"
        "implementation_status: IMPLEMENTED\n"
        "version: '1.0.0'\n"
        "owner_role: business-analyst\n"
        "accountable_role: business-analyst\n"
        "created_at: '2026-11-16'\n"
        "updated_at: '2026-11-16'\n"
        "source_of_truth:\n"
        "  is_authoritative: true\n"
        f"  authoritative_source: ['{cap_rel}/capability-specification.md']\n"
        "related_docs: ['APP-UI-COMP-001']\n"
        "requirement_ids: ['FR-UI-001']\n"
        "change_metadata:\n"
        "  approved_by: 'Senior BA'\n"
        "  approved_at: '2026-11-16'\n"
        "  change_summary: 'Approved baseline read-only UI capability.'\n"
        "revision_history:\n"
        "  - version: '1.0.0'\n"
        "    date: '2026-11-16'\n"
        "    author_role: business-analyst\n"
        "    summary: 'Initial release.'\n"
        "---\n\n"
        "# Read-Only Ticker Banner\n\n"
        "## 1. Capability Scope\n\nDisplays read-only market ticker labels.\n\n"
        "## 2. Functional Requirements\n\n"
        "| Req ID | Summary | Acceptance Criteria |\n"
        "|---|---|---|\n"
        "| FR-UI-001 | Display ticker symbol in UI banner. | AC-UI-001 |\n",
        encoding="utf-8",
    )
    (cap_dir / "design" / "component-design.md").write_text(
        "---\n"
        "doc_id: APP-UI-COMP-001\n"
        "title: 'Ticker Banner Component Design'\n"
        "doc_type: specification\n"
        "plane: application-plane\n"
        "scope_level: capability\n"
        "domain: market-ui\n"
        "capability_id: CAP-UI-001\n"
        "status: APPROVED\n"
        "implementation_status: IMPLEMENTED\n"
        "version: '1.0.0'\n"
        "owner_role: fullstack-engineer\n"
        "accountable_role: system-architect\n"
        "created_at: '2026-11-16'\n"
        "updated_at: '2026-11-16'\n"
        "source_of_truth:\n"
        "  is_authoritative: true\n"
        f"  authoritative_source: ['{cap_rel}/design/component-design.md']\n"
        "related_docs: ['APP-UI-CAP-001']\n"
        "change_metadata:\n"
        "  approved_by: 'System Architect'\n"
        "  approved_at: '2026-11-16'\n"
        "  change_summary: 'Approved component design.'\n"
        "revision_history:\n"
        "  - version: '1.0.0'\n"
        "    date: '2026-11-16'\n"
        "    author_role: fullstack-engineer\n"
        "    summary: 'Initial release.'\n"
        "---\n\n"
        "# Ticker Banner Component Design\n\n"
        "## 1. Responsibilities\n\nStateless rendering component.\n\n"
        "## 2. Props & Error Fallback\n\nRenders empty state when feed unavailable.\n",
        encoding="utf-8",
    )
    (cap_dir / "quality" / "test-cases.yaml").write_text(
        "schema_version: '2.0.0'\ncapability_id: 'CAP-UI-001'\ncases:\n"
        "  - test_case_id: 'TC-UI-001'\n    title: 'Render banner'\n",
        encoding="utf-8",
    )
    (cap_dir / "quality" / "traceability.yaml").write_text(
        "schema_version: '2.0.0'\n"
        "capability_id: 'CAP-UI-001'\n"
        "owner_role: 'business-analyst'\n"
        "document_status: 'APPROVED'\n"
        "links:\n"
        "  - business_need_id: 'BR-UI-001'\n"
        "    requirement_id: 'FR-UI-001'\n"
        "    rule_or_use_case_ids: []\n"
        "    design_doc_ids: ['APP-UI-COMP-001']\n"
        "    contract_paths: []\n"
        "    implementation_paths: ['src/serving/ui_widget.py']\n"
        "    test_case_ids: ['TC-UI-001']\n"
        "    test_paths: ['tests/unit/test_widget.py']\n"
        "    verification_evidence: 'pytest unit suite passed'\n",
        encoding="utf-8",
    )
    (cap_dir / "capability.yaml").write_text(
        "schema_version: '2.0.0'\n"
        "capability_id: 'CAP-UI-001'\n"
        "name: 'Read-Only Ticker Banner'\n"
        "plane: 'application-plane'\n"
        "domain: 'market-ui'\n"
        "owner_role: 'business-analyst'\n"
        "accountable_role: 'business-analyst'\n"
        "risk_tier: 'LOW'\n"
        "risk_signals:\n"
        "  handles_auth_or_rbac: false\n"
        "  handles_user_or_financial_data: false\n"
        "  external_exposure: false\n"
        "  schema_or_db_migration: false\n"
        "  realtime_or_event_streaming: false\n"
        "  agent_write_capable_tools: false\n"
        "  cross_plane_dependencies: false\n"
        "scope: 'Displays non-sensitive static banner state.'\n"
        "in_scope: ['Render label']\n"
        "out_of_scope: ['Order submission']\n"
        "authoritative_documents: ['capability-specification.md']\n"
        "required_artifacts:\n"
        "  - artifact_id: 'ART-CAP-MANIFEST'\n"
        "    path: 'capability.yaml'\n"
        "    applicability: 'REQUIRED'\n"
        "    status: 'PRESENT'\n"
        "  - artifact_id: 'ART-CAP-SPEC'\n"
        "    path: 'capability-specification.md'\n"
        "    applicability: 'REQUIRED'\n"
        "    status: 'PRESENT'\n"
        "  - artifact_id: 'ART-COMP-DESIGN'\n"
        "    path: 'design/component-design.md'\n"
        "    applicability: 'REQUIRED'\n"
        "    status: 'PRESENT'\n"
        "  - artifact_id: 'ART-TEST-CASES'\n"
        "    path: 'quality/test-cases.yaml'\n"
        "    applicability: 'REQUIRED'\n"
        "    status: 'PRESENT'\n"
        "  - artifact_id: 'ART-TRACEABILITY'\n"
        "    path: 'quality/traceability.yaml'\n"
        "    applicability: 'REQUIRED'\n"
        "    status: 'PRESENT'\n"
        "  - artifact_id: 'ART-DB-DESIGN'\n"
        "    path: null\n"
        "    applicability: 'NOT_APPLICABLE_WITH_REASON'\n"
        "    status: 'NOT_APPLICABLE'\n"
        "    not_applicable_reason: 'Read-only UI component has zero database tables.'\n"
        "document_status: 'APPROVED'\n"
        "implementation_status: 'IMPLEMENTED'\n"
        "code_paths: ['src/serving/ui_widget.py']\n"
        "test_paths: ['tests/unit/test_widget.py']\n"
        "change_metadata:\n"
        "  approved_by: 'Senior BA'\n"
        "  approved_at: '2026-11-16'\n"
        "  change_summary: 'Approved capability manifest.'\n"
        "updated_at: '2026-11-16'\n",
        encoding="utf-8",
    )
    return cap_dir


class DocumentationValidatorTests(unittest.TestCase):
    def test_valid_real_repository_passes(self) -> None:
        report = validate_repository(REPO_ROOT)
        self.assertEqual(
            report.errors,
            [],
            "Real repository validation failed:\n" + "\n".join(i.format() for i in report.errors),
        )

    def test_valid_low_risk_capability_fixture_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sandbox = _make_clean_sandbox(Path(tmp))
            _add_low_risk_ui_capability(sandbox)
            report = validate_repository(sandbox)
            self.assertEqual(
                report.errors,
                [],
                "\n".join(i.format() for i in report.errors),
            )

    def test_valid_high_risk_auth_capability_fixture_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sandbox = _make_clean_sandbox(Path(tmp))
            cap_dir = _add_low_risk_ui_capability(sandbox)
            sec_dir = cap_dir / "security"
            sec_dir.mkdir(exist_ok=True)
            (cap_dir / "contracts").mkdir(exist_ok=True)
            (cap_dir / "requirements").mkdir(exist_ok=True)
            (cap_dir / "use-cases").mkdir(exist_ok=True)
            (cap_dir / "operations").mkdir(exist_ok=True)

            cap_rel = "docs/application-plane/domains/market-ui/capabilities/readonly-ticker-banner"

            def _mkdoc(rel: str, doc_id: str, dtype: str, title: str, body: str, extra_fm: str = "") -> None:
                is_auth = "false" if dtype == "diagram" else "true"
                src_path = f"{cap_rel}/security/threat-model.md" if dtype == "diagram" else f"{cap_rel}/{rel}"
                (cap_dir / rel).write_text(
                    "---\n"
                    f"doc_id: {doc_id}\n"
                    f"title: '{title}'\n"
                    f"doc_type: {dtype}\n"
                    "plane: application-plane\n"
                    "scope_level: capability\n"
                    "domain: market-ui\n"
                    "capability_id: CAP-UI-001\n"
                    "status: APPROVED\n"
                    "implementation_status: IMPLEMENTED\n"
                    "version: '1.0.0'\n"
                    "owner_role: security-architect\n"
                    "accountable_role: security-architect\n"
                    "created_at: '2026-11-16'\n"
                    "updated_at: '2026-11-16'\n"
                    "source_of_truth:\n"
                    f"  is_authoritative: {is_auth}\n"
                    f"  authoritative_source: ['{src_path}']\n"
                    "related_docs: ['APP-UI-CAP-001']\n"
                    f"{extra_fm}"
                    "change_metadata:\n"
                    "  approved_by: 'Security Architect'\n"
                    "  approved_at: '2026-11-16'\n"
                    "  change_summary: 'Approved high-risk capability artifact.'\n"
                    "revision_history:\n"
                    "  - version: '1.0.0'\n"
                    "    date: '2026-11-16'\n"
                    "    author_role: security-architect\n"
                    "    summary: 'Initial release.'\n"
                    "---\n\n" + body,
                    encoding="utf-8",
                )

            _mkdoc(
                "security/threat-model.md",
                "APP-UI-TM-001",
                "specification",
                "Auth Threat Model",
                "# Auth Threat Model\n\n## 1. Assets & Entry Points\n\nJWT tokens and /login.\n\n"
                "## 2. Trust Boundaries & Threats\n\nDMZ boundary; THR-001 token forge.\n\n"
                "## 3. Mitigations & Residual Risks\n\nSEC-001 HS256 check; residual risk accepted.\n",
            )
            _mkdoc(
                "security/security-requirements.md",
                "APP-UI-SEC-001",
                "specification",
                "Security Requirements",
                "# Security Requirements\n\n## 1. Scope\n\nAuth guards.\n\n"
                "## 2. Controls\n\nSEC-UI-001 enforce role check.\n",
            )
            _mkdoc(
                "security/threat-model-diagram.md",
                "APP-UI-DIAG-TM-001",
                "diagram",
                "Threat Model Diagram",
                "# Threat Model Diagram\n\n## 1. Diagram Metadata\n\n"
                "| Field | Value |\n|---|---|\n| ID | DIAG-UI-001 |\n\n"
                "## 2. Diagram\n\n```mermaid\nflowchart TB\n"
                '  user["Client"] -->|"HTTPS"| api["Auth API"]\n```\n\n'
                "## 3. Legend\n\n- Solid arrow: synchronous HTTPS.\n",
            )
            _mkdoc(
                "use-cases/use-cases.md",
                "APP-UI-UC-001",
                "specification",
                "Auth Use Cases",
                "# Use Cases\n\n## 1. Actors\n\nTrader.\n\n## 2. Flows\n\nUC-UI-001 Login.\n",
            )
            _mkdoc(
                "requirements/nfr.md",
                "APP-UI-NFR-001",
                "specification",
                "Auth NFR",
                "# NFR\n\n## 1. Scope\n\nAuth latency.\n\n## 2. Targets\n\nNFR target verified in test.\n",
            )
            _mkdoc(
                "contracts/error-catalog.md",
                "APP-UI-ERR-001",
                "specification",
                "Error Catalog",
                "# Errors\n\n## 1. Scope\n\n4xx HTTP codes.\n\n## 2. Mapping\n\n401 Unauthorized.\n",
            )
            _mkdoc(
                "design/sequence-diagram.md",
                "APP-UI-DIAG-SEQ-001",
                "diagram",
                "Login Sequence Diagram",
                "# Login Sequence\n\n## 1. Diagram Metadata\n\n| ID | DIAG-UI-002 |\n|---|---|\n\n"
                "## 2. Diagram\n\n```mermaid\nsequenceDiagram\n  Client->>API: POST /login\n```\n\n"
                "## 3. Legend\n\n- Solid arrow: sync call.\n",
            )
            _mkdoc(
                "quality/test-plan.md",
                "APP-UI-TPLAN-001",
                "specification",
                "Test Plan",
                "# Test Plan\n\n## 1. Scope\n\nAuth tests.\n\n## 2. Criteria\n\nZero critical failures.\n",
            )
            _mkdoc(
                "quality/test-scenarios.md",
                "APP-UI-TSCEN-001",
                "specification",
                "Test Scenarios",
                "# Scenarios\n\n## 1. Scope\n\nNegative auth.\n\n## 2. Cases\n\nTS-UI-001 Invalid token.\n",
            )
            _mkdoc(
                "operations/observability.md",
                "APP-UI-OBS-001",
                "specification",
                "Observability",
                "# Observability\n\n## 1. Scope\n\nAuth metrics.\n\n## 2. Alerts\n\nAuth failure spike.\n",
            )
            _mkdoc(
                "operations/runbook.md",
                "APP-UI-RB-001",
                "specification",
                "Runbook",
                "# Runbook\n\n## 1. Scope\n\nKey rotation.\n\n## 2. Procedure\n\nRotate signing secret.\n",
            )
            _mkdoc(
                "operations/recovery.md",
                "APP-UI-REC-001",
                "specification",
                "Incident Recovery",
                "# Recovery\n\n## 1. Scope\n\nToken revocation.\n\n## 2. Drill\n\nEmergency revoke.\n",
            )

            (cap_dir / "security" / "authorization-matrix.yaml").write_text(
                "schema_version: '2.0.0'\nrules:\n  - subject: 'viewer'\n"
                "    resource: '/api/v1/auth/me'\n    action: 'read'\n    expected_decision: 'ALLOW'\n",
                encoding="utf-8",
            )
            (cap_dir / "contracts" / "openapi.yaml").write_text(
                "openapi: '3.1.0'\ninfo:\n  title: 'Auth Contract'\n  version: '1.0.0'\n"
                "paths:\n  /api/v1/auth/me:\n    get:\n      responses:\n        '200':\n          description: 'OK'\n",
                encoding="utf-8",
            )

            high_arts = [
                ("ART-CAP-MANIFEST", "capability.yaml"),
                ("ART-CAP-SPEC", "capability-specification.md"),
                ("ART-COMP-DESIGN", "design/component-design.md"),
                ("ART-TEST-CASES", "quality/test-cases.yaml"),
                ("ART-TRACEABILITY", "quality/traceability.yaml"),
                ("ART-USE-CASE", "use-cases/use-cases.md"),
                ("ART-NFR-SPEC", "requirements/nfr.md"),
                ("ART-ERR-CAT", "contracts/error-catalog.md"),
                ("ART-OPENAPI", "contracts/openapi.yaml"),
                ("ART-THREAT-MODEL", "security/threat-model.md"),
                ("ART-SEC-REQ", "security/security-requirements.md"),
                ("ART-AUTHZ-MATRIX", "security/authorization-matrix.yaml"),
                ("ART-DIAG-TM", "security/threat-model-diagram.md"),
                ("ART-DIAG-SEQ", "design/sequence-diagram.md"),
                ("ART-TEST-PLAN", "quality/test-plan.md"),
                ("ART-TEST-SCEN", "quality/test-scenarios.md"),
                ("ART-OBS-SLO", "operations/observability.md"),
                ("ART-RUNBOOK", "operations/runbook.md"),
                ("ART-INC-REC", "operations/recovery.md"),
            ]
            art_yaml = "".join(
                f"  - artifact_id: '{aid}'\n    path: '{pth}'\n    applicability: 'REQUIRED'\n    status: 'PRESENT'\n"
                for aid, pth in high_arts
            )
            (cap_dir / "capability.yaml").write_text(
                "schema_version: '2.0.0'\n"
                "capability_id: 'CAP-UI-001'\n"
                "name: 'Auth Guard Capability'\n"
                "plane: 'application-plane'\n"
                "domain: 'market-ui'\n"
                "owner_role: 'security-architect'\n"
                "accountable_role: 'security-architect'\n"
                "risk_tier: 'HIGH_CRITICAL'\n"
                "risk_signals:\n"
                "  handles_auth_or_rbac: true\n"
                "  handles_user_or_financial_data: false\n"
                "  external_exposure: true\n"
                "  schema_or_db_migration: false\n"
                "  realtime_or_event_streaming: false\n"
                "  agent_write_capable_tools: false\n"
                "  cross_plane_dependencies: false\n"
                "scope: 'Enforces token auth and RBAC rules.'\n"
                "in_scope: ['Verify JWT']\n"
                "out_of_scope: ['Billing']\n"
                "authoritative_documents: ['capability-specification.md']\n"
                f"required_artifacts:\n{art_yaml}"
                "document_status: 'APPROVED'\n"
                "implementation_status: 'IMPLEMENTED'\n"
                "code_paths: ['src/serving/ui_widget.py']\n"
                "test_paths: ['tests/unit/test_widget.py']\n"
                "change_metadata:\n"
                "  approved_by: 'Security Architect'\n"
                "  approved_at: '2026-11-16'\n"
                "  change_summary: 'Approved high-risk capability manifest.'\n"
                "updated_at: '2026-11-16'\n",
                encoding="utf-8",
            )
            report = validate_repository(sandbox)
            self.assertEqual(
                report.errors,
                [],
                "\n".join(i.format() for i in report.errors),
            )

    def test_rejects_approved_doc_missing_change_metadata_and_unresolved_tbd(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sandbox = _make_clean_sandbox(Path(tmp))
            cap_dir = _add_low_risk_ui_capability(sandbox)
            bad_doc = cap_dir / "capability-specification.md"
            text = bad_doc.read_text(encoding="utf-8")
            # Remove change_metadata and inject raw TBD in prose
            text = text.replace(
                "change_metadata:\n  approved_by: 'Senior BA'\n  approved_at: '2026-11-16'\n"
                "  change_summary: 'Approved baseline read-only UI capability.'\n",
                "",
            )
            text += "\nTarget threshold is TBD by product team.\n"
            bad_doc.write_text(text, encoding="utf-8")

            report = validate_repository(sandbox)
            rule_ids = {e.rule_id for e in report.errors}
            self.assertIn("VAL-FM-001", rule_ids)
            self.assertIn("VAL-TBD-001", rule_ids)

    def test_rejects_duplicate_doc_id_and_requirement_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sandbox = _make_clean_sandbox(Path(tmp))
            cap_dir = _add_low_risk_ui_capability(sandbox)
            dup = cap_dir / "duplicate-spec.md"
            dup.write_text(
                (cap_dir / "capability-specification.md").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            report = validate_repository(sandbox)
            rule_ids = {e.rule_id for e in report.errors}
            self.assertIn("VAL-ID-UNIQUE-001", rule_ids)

    def test_rejects_broken_links_anchors_and_traceability_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sandbox = _make_clean_sandbox(Path(tmp))
            cap_dir = _add_low_risk_ui_capability(sandbox)
            spec = cap_dir / "capability-specification.md"
            spec.write_text(
                spec.read_text(encoding="utf-8")
                + "\nSee [Broken](does-not-exist.md) and [Bad Anchor](design/component-design.md#missing-anchor).\n",
                encoding="utf-8",
            )
            trac = cap_dir / "quality" / "traceability.yaml"
            trac.write_text(
                trac.read_text(encoding="utf-8").replace(
                    "src/serving/ui_widget.py",
                    "src/serving/non_existent_module.py",
                ),
                encoding="utf-8",
            )
            report = validate_repository(sandbox)
            rule_ids = {e.rule_id for e in report.errors}
            self.assertIn("VAL-LINK-001", rule_ids)
            self.assertIn("VAL-LINK-002", rule_ids)
            self.assertIn("VAL-TRAC-001", rule_ids)

    def test_enforces_applicability_matrix_and_na_reason(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sandbox = _make_clean_sandbox(Path(tmp))
            cap_dir = _add_low_risk_ui_capability(sandbox)
            manifest = cap_dir / "capability.yaml"
            content = manifest.read_text(encoding="utf-8")
            # Activate auth signal without elevating tier/artifacts AND blank out NA reason
            content = content.replace("handles_auth_or_rbac: false", "handles_auth_or_rbac: true")
            content = content.replace(
                "not_applicable_reason: 'Read-only UI component has zero database tables.'",
                "not_applicable_reason: ''",
            )
            manifest.write_text(content, encoding="utf-8")

            report = validate_repository(sandbox)
            rule_ids = {e.rule_id for e in report.errors}
            self.assertIn("VAL-CAP-MATRIX-001", rule_ids)
            self.assertIn("VAL-CAP-SCHEMA-001", rule_ids)

    def test_enforces_derived_diagram_and_required_sections_and_no_archive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sandbox = _make_clean_sandbox(Path(tmp))
            cap_dir = _add_low_risk_ui_capability(sandbox)
            (sandbox / "docs" / "archive").mkdir()
            diag = cap_dir / "design" / "bad-diagram.md"
            diag.write_text(
                "---\n"
                "doc_id: APP-UI-DIAG-001\n"
                "title: 'Bad Derived Diagram'\n"
                "doc_type: diagram\n"
                "plane: application-plane\n"
                "scope_level: capability\n"
                "domain: market-ui\n"
                "capability_id: CAP-UI-001\n"
                "status: DRAFT\n"
                "implementation_status: NOT_IMPLEMENTED\n"
                "version: '0.1.0'\n"
                "owner_role: fullstack-engineer\n"
                "accountable_role: system-architect\n"
                "created_at: '2026-11-16'\n"
                "updated_at: '2026-11-16'\n"
                "source_of_truth:\n"
                "  is_authoritative: true\n"
                "  authoritative_source: []\n"
                "related_docs: ['APP-UI-COMP-001']\n"
                "---\n\n"
                "# Bad Derived Diagram\n\n"
                "## 1. Body\n\n"
                "```mermaid\n"
                "invalidDiagramType\n"
                "```\n",
                encoding="utf-8",
            )

            report = validate_repository(sandbox)
            rule_ids = {e.rule_id for e in report.errors}
            self.assertIn("VAL-STRUCT-002", rule_ids)
            self.assertIn("VAL-DIAG-SOT-001", rule_ids)
            self.assertIn("VAL-DIAG-META-001", rule_ids)
            self.assertIn("VAL-DIAG-MERMAID-001", rule_ids)


if __name__ == "__main__":
    unittest.main()
