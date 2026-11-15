"""Validates identifier registry patterns, uniqueness, and preservation of FR-01..10, ADR-001..008 & DIAG-*."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DIAG_ID_META_RE = re.compile(r"\*\*Diagram ID\*\*\s*\|\s*`(DIAG-[A-Z0-9-]+)`")


def _check_unique_ids(
    items: list[dict],
    key: str,
    compiled_pat: re.Pattern[str] | None,
    ns_label: str,
    rel_file: str,
) -> tuple[int, list[str]]:
    errors = 0
    seen: set[str] = set()
    ids: list[str] = []
    for item in items:
        val = str(item.get(key, ""))
        if not val:
            continue
        if compiled_pat is not None and not compiled_pat.match(val):
            print(f"[ERROR] {rel_file}: '{val}' failed {ns_label} regex pattern check")
            errors += 1
        if val in seen:
            print(f"[ERROR] {rel_file}: Duplicate {ns_label} identifier '{val}'")
            errors += 1
        seen.add(val)
        ids.append(val)
    return errors, ids


def validate_repo(repo_root: Path = REPO_ROOT) -> int:
    """Validate identifier registry patterns, preserved IDs, and uniqueness under `repo_root`."""
    errors = 0
    reg_path = repo_root / ".agents" / "config" / "identifier-registry.yaml"
    if not reg_path.exists():
        print("[ERROR] Missing .agents/config/identifier-registry.yaml")
        return 1

    reg = yaml.safe_load(reg_path.read_text(encoding="utf-8"))
    namespaces = reg.get("namespaces", {})
    if len(namespaces) < 20:
        print(f"[ERROR] Expected >= 20 identifier namespaces, found {len(namespaces)}")
        errors += 1

    compiled: dict[str, re.Pattern[str]] = {}
    for ns, spec in namespaces.items():
        pat = spec.get("pattern")
        if not pat:
            print(f"[ERROR] Namespace {ns} missing regex pattern")
            errors += 1
            continue
        compiled[ns] = re.compile(pat)

    req_model = yaml.safe_load(
        (repo_root / "models" / "requirements" / "requirements.yaml").read_text(encoding="utf-8")
    )
    e_cnt, fr_ids = _check_unique_ids(
        req_model.get("functional_requirements", []),
        "id",
        compiled.get("FR"),
        "FR",
        "models/requirements/requirements.yaml",
    )
    errors += e_cnt
    e_cnt, _ = _check_unique_ids(
        req_model.get("non_functional_requirements", []),
        "id",
        compiled.get("NFR"),
        "NFR",
        "models/requirements/requirements.yaml",
    )
    errors += e_cnt

    for i in range(1, 11):
        efr = f"FR-{i:02d}"
        if efr not in fr_ids:
            print(f"[ERROR] Preserved Data Platform requirement '{efr}' missing from requirements.yaml")
            errors += 1

    arch_model = yaml.safe_load(
        (repo_root / "models" / "architecture" / "architecture.yaml").read_text(encoding="utf-8")
    )
    e_cnt, adr_ids = _check_unique_ids(
        arch_model.get("decisions", []),
        "id",
        compiled.get("ADR"),
        "ADR",
        "models/architecture/architecture.yaml",
    )
    errors += e_cnt
    for i in range(1, 9):
        eadr = f"ADR-{i:03d}"
        if eadr not in adr_ids:
            print(f"[ERROR] Preserved ADR '{eadr}' missing from architecture.yaml")
            errors += 1

    # Check active diagram IDs match DIAG namespace
    diag_root = repo_root / "docs" / "diagrams"
    if diag_root.exists() and "DIAG" in compiled:
        for df in sorted(diag_root.rglob("*.md")):
            if df.name.lower() == "readme.md" or df.name.endswith(".template.md"):
                continue
            m = DIAG_ID_META_RE.search(df.read_text(encoding="utf-8"))
            if not m:
                print(f"[ERROR] {df.relative_to(repo_root).as_posix()}: Missing Diagram ID metadata")
                errors += 1
            elif not compiled["DIAG"].match(m.group(1)):
                print(f"[ERROR] {df.relative_to(repo_root).as_posix()}: '{m.group(1)}' failed DIAG pattern")
                errors += 1

    # Check API and Test Case IDs if models exist
    api_path = repo_root / "models" / "api" / "api.yaml"
    if api_path.exists():
        api_data = yaml.safe_load(api_path.read_text(encoding="utf-8")) or {}
        e_cnt, _ = _check_unique_ids(
            api_data.get("endpoints", []), "id", compiled.get("API"), "API", "models/api/api.yaml"
        )
        errors += e_cnt

    test_path = repo_root / "models" / "testing" / "testing.yaml"
    if test_path.exists():
        test_data = yaml.safe_load(test_path.read_text(encoding="utf-8")) or {}
        e_cnt, _ = _check_unique_ids(
            test_data.get("test_cases", []), "id", compiled.get("TC"), "TC", "models/testing/testing.yaml"
        )
        errors += e_cnt

    print(
        f"[validate_identifiers] Checked {len(namespaces)} namespaces and preserved IDs -> {errors} error(s)."
    )
    return 1 if errors else 0


def main() -> int:
    return validate_repo(REPO_ROOT)


if __name__ == "__main__":
    sys.exit(main())
