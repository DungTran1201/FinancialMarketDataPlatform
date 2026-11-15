"""Automated positive and isolated negative tests for DOCS-004 semantic validators (TC-017)."""

from __future__ import annotations

import contextlib
import io
import shutil
import tempfile
import unittest
from collections.abc import Callable
from pathlib import Path

from tools.validators import (
    validate_diagrams,
    validate_docs,
    validate_identifiers,
    validate_models,
    validate_traceability,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


class DocumentationValidatorsTestCase(unittest.TestCase):
    """Verify semantic validators pass on the real repository and fail deterministically on defects."""

    @staticmethod
    def _copy_repo_subset(
        tmp_dir: str,
        dirs: tuple[str, ...] = (),
        files: tuple[str, ...] = (),
    ) -> Path:
        root = Path(tmp_dir)
        for rel_dir in dirs:
            src = REPO_ROOT / rel_dir
            if src.exists():
                shutil.copytree(src, root / rel_dir)
        for rel_file in files:
            src = REPO_ROOT / rel_file
            dst = root / rel_file
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        return root

    @staticmethod
    def _run_silent(fn: Callable[..., int], *args: object, **kwargs: object) -> int:
        with contextlib.redirect_stdout(io.StringIO()):
            return fn(*args, **kwargs)

    def test_baseline_semantic_validators_pass_on_real_repo(self) -> None:
        self.assertEqual(self._run_silent(validate_models.validate_repo, REPO_ROOT), 0)
        self.assertEqual(self._run_silent(validate_diagrams.validate_repo, REPO_ROOT), 0)
        self.assertEqual(self._run_silent(validate_identifiers.validate_repo, REPO_ROOT), 0)
        self.assertEqual(self._run_silent(validate_docs.validate_repo, REPO_ROOT), 0)
        self.assertEqual(
            self._run_silent(validate_traceability.validate_repo, REPO_ROOT, verify_runtime_contracts=True),
            0,
        )

    def test_validate_models_rejects_missing_data_platform_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_repo = self._copy_repo_subset(tmp_dir, dirs=("models",))
            shutil.rmtree(tmp_repo / "models" / "data-platform")
            self.assertEqual(self._run_silent(validate_models.validate_repo, tmp_repo), 1)

    def test_validate_diagrams_rejects_missing_id_duplicate_id_and_unquoted_parens(self) -> None:
        scenarios: list[tuple[str, str, Callable[[str], str]]] = [
            (
                "missing_diagram_id",
                "docs/diagrams/system/01-system-context.md",
                lambda text: text.replace("DIAG-CTX-001", "REMOVED-ID"),
            ),
            (
                "duplicate_diagram_id",
                "docs/diagrams/system/02-c4-container.md",
                lambda text: text.replace("DIAG-C4-002", "DIAG-CTX-001"),
            ),
            (
                "unquoted_parens_in_node_label",
                "docs/diagrams/system/01-system-context.md",
                lambda text: text.replace("```mermaid\n", "```mermaid\nflowchart LR\n  BAD[Broken (Label)]\n", 1),
            ),
        ]
        for label, target_rel, mutator in scenarios:
            with self.subTest(scenario=label), tempfile.TemporaryDirectory() as tmp_dir:
                tmp_repo = self._copy_repo_subset(tmp_dir, dirs=("docs/diagrams",))
                target = tmp_repo / target_rel
                original = target.read_text(encoding="utf-8")
                mutated = mutator(original)
                self.assertNotEqual(original, mutated)
                target.write_text(mutated, encoding="utf-8")
                self.assertEqual(self._run_silent(validate_diagrams.validate_repo, tmp_repo), 1)

    def test_validate_docs_rejects_duplicate_root_broken_links_and_nonexistent_paths(self) -> None:
        overview_rel = "docs/architecture/00-architecture-overview.md"
        scenarios: list[tuple[str, Callable[[Path], None]]] = [
            (
                "duplicate_diagrams_root",
                lambda root: (root / "diagrams").mkdir(parents=True, exist_ok=True),
            ),
            (
                "broken_relative_markdown_link",
                lambda root: (root / overview_rel).write_text(
                    (root / overview_rel).read_text(encoding="utf-8")
                    + "\nSee [MissingDoc](nonexistent-sibling-doc.md).\n",
                    encoding="utf-8",
                ),
            ),
            (
                "nonexistent_backtick_path",
                lambda root: (root / overview_rel).write_text(
                    (root / overview_rel).read_text(encoding="utf-8")
                    + "\nCheck `models/api/phantom-contract.yaml` for details.\n",
                    encoding="utf-8",
                ),
            ),
        ]
        for label, mutator in scenarios:
            with self.subTest(scenario=label), tempfile.TemporaryDirectory() as tmp_dir:
                tmp_repo = self._copy_repo_subset(
                    tmp_dir,
                    dirs=("docs", "work-items", ".agents", "models", "tools"),
                    files=("AGENTS.md", "README.md"),
                )
                mutator(tmp_repo)
                self.assertEqual(self._run_silent(validate_docs.validate_repo, tmp_repo), 1)

    def test_validate_identifiers_rejects_missing_adr_008_or_duplicate_api_id(self) -> None:
        scenarios: list[tuple[str, str, Callable[[str], str]]] = [
            (
                "missing_adr_008",
                "models/architecture/architecture.yaml",
                lambda text: text.replace("ADR-008", "ADR-006"),
            ),
            (
                "duplicate_api_id",
                "models/api/api.yaml",
                lambda text: text.replace('id: "API-002"', 'id: "API-001"', 1),
            ),
        ]
        for label, target_rel, mutator in scenarios:
            with self.subTest(scenario=label), tempfile.TemporaryDirectory() as tmp_dir:
                tmp_repo = self._copy_repo_subset(
                    tmp_dir,
                    dirs=(".agents", "models", "docs/architecture", "docs/diagrams"),
                )
                target = tmp_repo / target_rel
                original = target.read_text(encoding="utf-8")
                mutated = mutator(original)
                self.assertNotEqual(original, mutated)
                target.write_text(mutated, encoding="utf-8")
                self.assertEqual(self._run_silent(validate_identifiers.validate_repo, tmp_repo), 1)

    def test_validate_traceability_rejects_broken_ac_tc_link(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_repo = self._copy_repo_subset(tmp_dir, dirs=("models", "deploy", "docs/architecture"))
            ac_path = tmp_repo / "models" / "requirements" / "acceptance-criteria.yaml"
            text = ac_path.read_text(encoding="utf-8")
            mutated = text.replace('"TC-001"', '"TC-999"', 1)
            self.assertNotEqual(text, mutated)
            ac_path.write_text(mutated, encoding="utf-8")
            self.assertEqual(
                self._run_silent(validate_traceability.validate_repo, tmp_repo, verify_runtime_contracts=False),
                1,
            )

    def test_validate_deployment_and_observability_rejects_port_collision_and_bad_prometheus_yaml(self) -> None:
        scenarios: list[tuple[str, str, Callable[[str], str]]] = [
            (
                "compose_host_port_collision",
                "docker-compose.yml",
                lambda text: text.replace("${MINIO_API_PORT:-9010}:9000", "9000:9000", 1),
            ),
            (
                "invalid_prometheus_yaml",
                "deploy/observability/prometheus/prometheus.yml",
                lambda _text: "scrape_configs:\n  - job_name: [broken\n",
            ),
        ]
        for label, target_rel, mutator in scenarios:
            with self.subTest(scenario=label), tempfile.TemporaryDirectory() as tmp_dir:
                tmp_repo = self._copy_repo_subset(tmp_dir, dirs=("deploy",), files=("docker-compose.yml",))
                target = tmp_repo / target_rel
                original = target.read_text(encoding="utf-8")
                mutated = mutator(original)
                self.assertNotEqual(original, mutated)
                target.write_text(mutated, encoding="utf-8")
                self.assertGreater(
                    self._run_silent(validate_traceability.validate_deployment_and_observability, tmp_repo),
                    0,
                )

    def test_validate_runtime_contract_parity_rejects_route_and_event_drift(self) -> None:
        scenarios: list[tuple[str, str, Callable[[str], str]]] = [
            (
                "api_route_drift",
                "models/api/api.yaml",
                lambda text: text.replace('path: "/api/v1/market/prices"', 'path: "/api/v1/market/phantom"', 1),
            ),
            (
                "event_type_drift",
                "models/data-platform/events.yaml",
                lambda text: text.replace('runtime_event_type: "trade"', 'runtime_event_type: "phantom_trade"', 1),
            ),
        ]
        for label, target_rel, mutator in scenarios:
            with self.subTest(scenario=label), tempfile.TemporaryDirectory() as tmp_dir:
                tmp_repo = self._copy_repo_subset(tmp_dir, dirs=("models",))
                target = tmp_repo / target_rel
                original = target.read_text(encoding="utf-8")
                mutated = mutator(original)
                self.assertNotEqual(original, mutated)
                target.write_text(mutated, encoding="utf-8")
                self.assertGreater(
                    self._run_silent(validate_traceability.validate_runtime_contract_parity, tmp_repo),
                    0,
                )


if __name__ == "__main__":
    unittest.main()
