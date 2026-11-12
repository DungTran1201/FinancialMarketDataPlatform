"""Validates identifier registry patterns, uniqueness, and preservation of FR-01..10 & ADR-001..006."""

from __future__ import annotations

import re
import sys
from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
REG_PATH = REPO_ROOT / ".agents" / "config" / "identifier-registry.yaml"


def main() -> int:
    errors = 0
    if not REG_PATH.exists():
        print("[ERROR] Missing .agents/config/identifier-registry.yaml")
        return 1

    reg = yaml.safe_load(REG_PATH.read_text(encoding="utf-8"))
    namespaces = reg.get("namespaces", {})
    if len(namespaces) < 20:
        print(f"[ERROR] Expected >= 20 identifier namespaces, found {len(namespaces)}")
        errors += 1

    # Verify compiled regex patterns for all registered namespaces
    compiled: dict[str, re.Pattern[str]] = {}
    for ns, spec in namespaces.items():
        pat = spec.get("pattern")
        if not pat:
            print(f"[ERROR] Namespace {ns} missing regex pattern")
            errors += 1
            continue
        compiled[ns] = re.compile(pat)

    # Verify preserved FR-01..10 in models/requirements/requirements.yaml
    req_model = yaml.safe_load(
        (REPO_ROOT / "models" / "requirements" / "requirements.yaml").read_text(encoding="utf-8")
    )
    fr_ids = [item["id"] for item in req_model.get("functional_requirements", [])]
    expected_frs = [f"FR-{i:02d}" for i in range(1, 11)]
    for efr in expected_frs:
        if efr not in fr_ids:
            print(f"[ERROR] Preserved Data Platform requirement '{efr}' missing from requirements.yaml")
            errors += 1
        elif not compiled["FR"].match(efr):
            print(f"[ERROR] '{efr}' failed FR regex pattern check")
            errors += 1

    # Verify preserved ADR-001..006 in models/architecture/architecture.yaml
    arch_model = yaml.safe_load(
        (REPO_ROOT / "models" / "architecture" / "architecture.yaml").read_text(encoding="utf-8")
    )
    adr_ids = [item["id"] for item in arch_model.get("decisions", [])]
    expected_adrs = [f"ADR-00{i}" for i in range(1, 7)]
    for eadr in expected_adrs:
        if eadr not in adr_ids:
            print(f"[ERROR] Preserved ADR '{eadr}' missing from architecture.yaml")
            errors += 1
        elif not compiled["ADR"].match(eadr):
            print(f"[ERROR] '{eadr}' failed ADR regex pattern check")
            errors += 1

    print(
        f"[validate_identifiers] Checked {len(namespaces)} namespaces and preserved IDs -> {errors} error(s)."
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
