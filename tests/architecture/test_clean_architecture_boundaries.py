"""Automated Clean Architecture & Three-Plane Isolation Boundary Tests."""

from __future__ import annotations

import ast
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"

FORBIDDEN_DOMAIN_FRAMEWORKS = {
    "fastapi",
    "sqlalchemy",
    "asyncpg",
    "redis",
    "clickhouse_connect",
    "confluent_kafka",
    "httpx",
    "websockets",
    "langgraph",
    "pyspark",
}

EXPECTED_BACKEND_MODULES = {
    "market",
    "historical",
    "analytics",
    "catalog",
    "iam",
    "platform_config",
    "agent_api",
    "reporting",
}


def _extract_top_level_imports(py_file: Path) -> set[str]:
    tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports


class TestArchitectureBoundaries(unittest.TestCase):
    """Verifies Clean/Hexagonal boundaries and Plane A / Plane B / Plane C isolation."""

    def test_all_eight_backend_domain_modules_exist(self) -> None:
        modules_dir = SRC_ROOT / "backend" / "modules"
        existing = {p.name for p in modules_dir.iterdir() if p.is_dir() and not p.name.startswith("_")}
        self.assertEqual(existing, EXPECTED_BACKEND_MODULES)

    def test_domain_layers_have_zero_framework_or_driver_dependencies(self) -> None:
        domain_files = list(SRC_ROOT.glob("backend/modules/*/domain/*.py")) + list(
            SRC_ROOT.glob("shared/domain/*.py")
        )
        self.assertGreater(len(domain_files), 0, "Expected domain layer files to be present")

        for py_file in domain_files:
            imports = _extract_top_level_imports(py_file)
            for imp in imports:
                root_pkg = imp.split(".")[0]
                self.assertNotIn(
                    root_pkg,
                    FORBIDDEN_DOMAIN_FRAMEWORKS,
                    f"Clean Architecture violation in {py_file.relative_to(REPO_ROOT)}: "
                    f"Domain layer must not import '{imp}'",
                )
                self.assertFalse(
                    imp.startswith("src.backend.modules") and ".infrastructure" in imp,
                    f"Domain file {py_file.relative_to(REPO_ROOT)} must not import infrastructure '{imp}'",
                )
                self.assertFalse(
                    imp.startswith("src.backend.modules") and ".presentation" in imp,
                    f"Domain file {py_file.relative_to(REPO_ROOT)} must not import presentation '{imp}'",
                )

    def test_data_plane_never_depends_on_intelligence_plane(self) -> None:
        data_plane_dirs = [
            SRC_ROOT / "collectors",
            SRC_ROOT / "consumers",
            SRC_ROOT / "processing",
            SRC_ROOT / "quality",
        ]
        py_files = [f for d in data_plane_dirs for f in d.rglob("*.py")]
        self.assertGreater(len(py_files), 0)

        for py_file in py_files:
            imports = _extract_top_level_imports(py_file)
            for imp in imports:
                self.assertFalse(
                    imp == "src.agent" or imp.startswith("src.agent."),
                    f"Plane Isolation violation in {py_file.relative_to(REPO_ROOT)}: "
                    f"Data Plane must never depend on Intelligence Plane ('{imp}')",
                )


if __name__ == "__main__":
    unittest.main()

