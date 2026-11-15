"""Architectural Boundary & Clean Architecture Enforcement Tests (`TC-006`).

Verifies layer purity and strict inter-module isolation across the Event-Driven Modular Data Platform:
`shared`, `ingestion`, `streaming`, `lakehouse`, `serving`, and `intelligence`.
"""

from __future__ import annotations

import ast
import unittest
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"

EXPECTED_SERVING_MODULES = {
    "market",
    "historical",
    "analytics",
    "catalog",
    "iam",
    "platform_config",
    "agent_api",
    "reporting",
}

FORBIDDEN_DOMAIN_IMPORTS = {
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


def _extract_imports(py_file: Path) -> set[str]:
    tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


class TestArchitectureBoundaries(unittest.TestCase):
    """Validates Clean Architecture & Modular Data Platform boundaries."""

    def test_top_level_modular_packages_and_eight_serving_contexts_exist(self) -> None:
        for pkg in ("shared", "ingestion", "streaming", "lakehouse", "serving", "intelligence"):
            self.assertTrue((SRC_ROOT / pkg).is_dir(), f"Missing top-level package src/{pkg}/")

        modules_root = SRC_ROOT / "serving" / "api" / "modules"
        actual = {p.name for p in modules_root.iterdir() if p.is_dir() and p.name != "__pycache__"}
        self.assertEqual(actual, EXPECTED_SERVING_MODULES)

    def test_domain_layers_have_zero_framework_or_driver_dependencies(self) -> None:
        domain_files = list((SRC_ROOT / "serving" / "api" / "modules").glob("*/domain/*.py"))
        domain_files += list((SRC_ROOT / "shared" / "domain").glob("*.py"))
        domain_files += list((SRC_ROOT / "ingestion" / "domain").glob("*.py"))
        self.assertGreater(len(domain_files), 0)

        for py_file in domain_files:
            imported = _extract_imports(py_file)
            for mod in imported:
                root_pkg = mod.split(".")[0]
                self.assertNotIn(
                    root_pkg,
                    FORBIDDEN_DOMAIN_IMPORTS,
                    f"Domain layer {py_file} must not import framework/driver '{mod}'",
                )
                self.assertNotIn(
                    ".infrastructure",
                    mod,
                    f"Domain layer {py_file} must not import infrastructure '{mod}'",
                )
                self.assertNotIn(
                    ".presentation",
                    mod,
                    f"Domain layer {py_file} must not import presentation '{mod}'",
                )

    def test_shared_and_subsystem_isolation_no_cross_coupling(self) -> None:
        """Enforce directed acyclic module boundaries:
        - shared -> {}
        - ingestion -> {shared}
        - streaming -> {shared}
        - lakehouse/{bronze,silver,gold,quality,catalog} -> {shared}
        - intelligence -> {shared}
        - serving/api/{modules,gateway,services} -> {shared}
        Only composition roots (`lakehouse/orchestration`, `serving/infrastructure`) wire engines.
        """
        boundary_rules: list[tuple[Path, tuple[str, ...]]] = [
            (
                SRC_ROOT / "shared",
                ("src.ingestion", "src.streaming", "src.lakehouse", "src.serving", "src.intelligence"),
            ),
            (
                SRC_ROOT / "ingestion",
                ("src.streaming", "src.lakehouse", "src.serving", "src.intelligence"),
            ),
            (
                SRC_ROOT / "streaming",
                ("src.ingestion", "src.lakehouse", "src.serving", "src.intelligence"),
            ),
            (
                SRC_ROOT / "intelligence",
                ("src.ingestion", "src.streaming", "src.lakehouse", "src.serving"),
            ),
            (
                SRC_ROOT / "serving" / "api",
                ("src.ingestion", "src.streaming", "src.lakehouse", "src.intelligence"),
            ),
        ]
        for subpkg in ("bronze", "silver", "gold", "quality", "catalog"):
            boundary_rules.append(
                (
                    SRC_ROOT / "lakehouse" / subpkg,
                    ("src.ingestion", "src.streaming", "src.serving", "src.intelligence"),
                )
            )

        for target_dir, forbidden_prefixes in boundary_rules:
            for py_file in target_dir.rglob("*.py"):
                for mod in _extract_imports(py_file):
                    for prefix in forbidden_prefixes:
                        self.assertFalse(
                            mod.startswith(prefix),
                            f"Boundary violation: {py_file} must not import '{mod}' (forbidden '{prefix}')",
                        )
