"""Validates bidirectional traceability links across models/requirements, models/testing, and models/security."""

from __future__ import annotations

import sys
from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    errors = 0
    req_data = yaml.safe_load(
        (REPO_ROOT / "models/requirements/requirements.yaml").read_text(encoding="utf-8")
    )
    br_data = yaml.safe_load(
        (REPO_ROOT / "models/requirements/business-rules.yaml").read_text(encoding="utf-8")
    )
    ac_data = yaml.safe_load(
        (REPO_ROOT / "models/requirements/acceptance-criteria.yaml").read_text(encoding="utf-8")
    )
    test_data = yaml.safe_load(
        (REPO_ROOT / "models/testing/testing.yaml").read_text(encoding="utf-8")
    )
    sec_data = yaml.safe_load(
        (REPO_ROOT / "models/security/threat-model.yaml").read_text(encoding="utf-8")
    )
    arch_data = yaml.safe_load(
        (REPO_ROOT / "models/architecture/architecture.yaml").read_text(encoding="utf-8")
    )

    known_reqs = {r["id"] for r in req_data.get("functional_requirements", [])} | {
        r["id"] for r in req_data.get("non_functional_requirements", [])
    }
    known_brs = {b["id"] for b in br_data.get("business_rules", [])}
    known_acs = {a["id"] for a in ac_data.get("acceptance_criteria", [])}
    known_tcs = {t["id"] for t in test_data.get("test_cases", [])}
    known_ctrls = {c["id"] for c in sec_data.get("controls", [])}
    known_threats = {t["id"] for t in sec_data.get("threats", [])}

    # 1. Verify AC -> FR and AC -> TC links
    for ac in ac_data.get("acceptance_criteria", []):
        req_id = ac.get("requirement_id")
        if req_id not in known_reqs:
            print(f"[ERROR] AC {ac.get('id')} references unknown requirement '{req_id}'")
            errors += 1
        for tc_ref in ac.get("test_case_refs", []):
            if tc_ref not in known_tcs:
                print(f"[ERROR] AC {ac.get('id')} references unknown test case '{tc_ref}'")
                errors += 1

    # 2. Verify TC -> FR/BR/CTRL and test_path existence
    valid_refs = known_reqs | known_brs | known_ctrls
    for tc in test_data.get("test_cases", []):
        for ref in tc.get("requirement_refs", []):
            if ref not in valid_refs:
                print(f"[ERROR] Test Case {tc.get('id')} references unknown artifact '{ref}'")
                errors += 1
        tpath = REPO_ROOT / tc.get("test_path", "")
        if not tpath.exists():
            print(f"[ERROR] Test Case {tc.get('id')} test_path does not exist: '{tc.get('test_path')}'")
            errors += 1

    # 3. Verify Threat <-> Control links
    for thr in sec_data.get("threats", []):
        for ctrl_id in thr.get("mitigated_by", []):
            if ctrl_id not in known_ctrls:
                print(f"[ERROR] Threat {thr.get('id')} references unknown control '{ctrl_id}'")
                errors += 1
    for ctrl in sec_data.get("controls", []):
        for thr_id in ctrl.get("mitigates", []):
            if thr_id not in known_threats:
                print(f"[ERROR] Control {ctrl.get('id')} references unknown threat '{thr_id}'")
                errors += 1

    # 4. Verify ADR file paths in architecture.yaml
    for dec in arch_data.get("decisions", []):
        if not (REPO_ROOT / dec.get("path", "")).exists():
            print(f"[ERROR] Decision {dec.get('id')} path missing: {dec.get('path')}")
            errors += 1

    print(
        f"[validate_traceability] Verified {len(known_reqs)} requirements, {len(known_acs)} ACs, "
        f"{len(known_tcs)} test cases, and {len(known_ctrls)} security controls -> {errors} error(s)."
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
