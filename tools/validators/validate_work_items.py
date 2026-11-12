"""Validates work-items/_template/ and all active work item directories."""

from __future__ import annotations

import sys
from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
WI_ROOT = REPO_ROOT / "work-items"
GATES_CFG = REPO_ROOT / ".agents" / "config" / "phase-gates.yaml"

REQUIRED_WI_FILES = [
    "README.md",
    "request.md",
    "discovery.md",
    "impact-analysis.md",
    "artifact-plan.yaml",
    "implementation-plan.md",
    "verification-plan.md",
    "review.md",
    "state.yaml",
]

ALLOWED_ACTIONS = {"CREATED", "UPDATED", "REVIEWED", "UNCHANGED", "DEPRECATED"}


def main() -> int:
    errors = 0
    if not WI_ROOT.exists():
        print("[ERROR] work-items/ directory does not exist.")
        return 1

    gates_data = yaml.safe_load(GATES_CFG.read_text(encoding="utf-8"))
    valid_states = set(gates_data.get("work_item_states", []))
    allowed_transitions = gates_data.get("allowed_state_transitions", {})

    wi_dirs = [p for p in sorted(WI_ROOT.iterdir()) if p.is_dir()]
    if len(wi_dirs) < 2:
        print("[ERROR] Expected at least '_template' and 'DOCS-001-documentation-engineering-foundation'")
        errors += 1

    for wdir in wi_dirs:
        rel = wdir.relative_to(REPO_ROOT).as_posix()
        for req_f in REQUIRED_WI_FILES:
            if not (wdir / req_f).exists():
                print(f"[ERROR] {rel}: Missing required work item file '{req_f}'")
                errors += 1

        state_file = wdir / "state.yaml"
        plan_file = wdir / "artifact-plan.yaml"
        if state_file.exists():
            sdata = yaml.safe_load(state_file.read_text(encoding="utf-8"))
            wi = sdata.get("work_item", {})
            st = wi.get("status")
            if st not in valid_states:
                print(f"[ERROR] {rel}/state.yaml: Invalid status '{st}'")
                errors += 1
            for h in wi.get("history", []):
                f_st = h.get("from_state")
                t_st = h.get("to_state")
                if f_st is not None and t_st not in allowed_transitions.get(f_st, []):
                    print(f"[ERROR] {rel}/state.yaml: Invalid transition {f_st} -> {t_st}")
                    errors += 1

        if plan_file.exists():
            pdata = yaml.safe_load(plan_file.read_text(encoding="utf-8"))
            for item in pdata.get("planned_artifacts", []):
                act = item.get("action")
                if act not in ALLOWED_ACTIONS:
                    print(f"[ERROR] {rel}/artifact-plan.yaml: Invalid action '{act}'")
                    errors += 1
                if wdir.name != "_template" and act in {"CREATED", "UPDATED", "REVIEWED"}:
                    p = item.get("path", "")
                    if not (REPO_ROOT / p).exists():
                        print(f"[ERROR] {rel}/artifact-plan.yaml: Planned path does not exist: '{p}'")
                        errors += 1

    print(f"[validate_work_items] Checked {len(wi_dirs)} work item directories -> {errors} error(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
