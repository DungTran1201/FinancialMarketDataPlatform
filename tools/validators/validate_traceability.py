"""Validates bidirectional model traceability plus runtime API, event, Compose, and Prometheus parity."""

from __future__ import annotations

import dataclasses
import re
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

COMPOSE_PORT_RE = re.compile(r"^(?:[0-9.]+:)?(?:\$\{[A-Z0-9_]+:-(\d+)\}|(\d+)):\d+$")


def _collect_fastapi_routes(router_obj: Any, prefix: str = "") -> set[tuple[str, str]]:
    """Recursively flatten mounted FastAPI routes including `_IncludedRouter` wrappers."""
    out: set[tuple[str, str]] = set()
    for r in getattr(router_obj, "routes", []):
        if hasattr(r, "original_router") and hasattr(r, "include_context"):
            out |= _collect_fastapi_routes(r.original_router, prefix + (r.include_context.prefix or ""))
        elif hasattr(r, "router") and hasattr(r, "prefix"):
            out |= _collect_fastapi_routes(r.router, prefix + (r.prefix or ""))
        else:
            p = prefix + (getattr(r, "path", "") or "")
            if not p.startswith("/api/") and not p.startswith("/ws/") and p != "/metrics":
                continue
            if p in ("/api/docs", "/api/openapi.json"):
                continue
            methods = getattr(r, "methods", None)
            if methods:
                for m in methods:
                    if m in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
                        out.add((m, p))
            else:
                out.add(("WS", p))
    return out


def validate_deployment_and_observability(repo_root: Path) -> int:
    """Validate `docker-compose.yml` port collisions and Prometheus/alerts YAML syntax."""
    errors = 0
    compose_path = repo_root / "docker-compose.yml"
    if compose_path.exists():
        try:
            dc = yaml.safe_load(compose_path.read_text(encoding="utf-8")) or {}
        except Exception as exc:
            print(f"[ERROR] docker-compose.yml invalid YAML: {exc}")
            return 1
        host_ports: dict[int, list[str]] = {}
        for svc_name, svc in (dc.get("services") or {}).items():
            for raw_port in svc.get("ports") or []:
                m = COMPOSE_PORT_RE.match(str(raw_port).strip())
                if m:
                    hp = int(m.group(1) or m.group(2))
                    host_ports.setdefault(hp, []).append(svc_name)
        for hp, svcs in sorted(host_ports.items()):
            if len(svcs) > 1:
                print(f"[ERROR] docker-compose.yml host port collision on :{hp} -> {svcs}")
                errors += 1

    for prom_rel in (
        "deploy/observability/prometheus/prometheus.yml",
        "deploy/observability/prometheus/alerts.yml",
    ):
        prom_path = repo_root / prom_rel
        if prom_path.exists():
            try:
                parsed = yaml.safe_load(prom_path.read_text(encoding="utf-8")) or {}
                if prom_rel.endswith("prometheus.yml") and not parsed.get("scrape_configs"):
                    print(f"[ERROR] {prom_rel}: Missing or empty 'scrape_configs'")
                    errors += 1
            except Exception as exc:
                print(f"[ERROR] {prom_rel} invalid YAML: {exc}")
                errors += 1
    return errors


def validate_runtime_contract_parity(repo_root: Path) -> int:
    """Validate code-vs-YAML parity for FastAPI routes, EventType/envelopes, topics, and CGs."""
    errors = 0
    from src.serving.api.main import create_app
    from src.shared.contracts.events.market_events import (
        DeadLetterEnvelopeV1,
        EventEnvelopeV1,
        EventType,
        KafkaTopic,
    )
    from src.streaming.contracts.topics import (
        CG_ANALYTICS_CH,
        CG_ANOMALY_DETECTOR,
        CG_HOT_REDIS,
        CG_LAKEHOUSE_BRONZE,
    )

    api_yaml_path = repo_root / "models/api/api.yaml"
    if api_yaml_path.exists():
        api_yaml = yaml.safe_load(api_yaml_path.read_text(encoding="utf-8")) or {}
        yaml_active = {
            (ep["method"].upper(), ep["path"])
            for ep in api_yaml.get("endpoints", [])
            if ep.get("implementation_status") != "PLANNED"
        }
        yaml_planned = {
            (ep["method"].upper(), ep["path"])
            for ep in api_yaml.get("endpoints", [])
            if ep.get("implementation_status") == "PLANNED"
        }
        app_routes = _collect_fastapi_routes(create_app())
        extra_in_app = sorted(app_routes - yaml_active)
        missing_from_app = sorted(yaml_active - app_routes)
        planned_but_mounted = sorted(yaml_planned & app_routes)
        if extra_in_app:
            print(f"[ERROR] FastAPI monolith routes missing from models/api/api.yaml: {extra_in_app}")
            errors += 1
        if missing_from_app:
            print(f"[ERROR] models/api/api.yaml non-PLANNED routes missing in monolith: {missing_from_app}")
            errors += 1
        if planned_but_mounted:
            print(f"[ERROR] PLANNED API routes unexpectedly mounted in monolith: {planned_but_mounted}")
            errors += 1

    events_path = repo_root / "models/data-platform/events.yaml"
    if events_path.exists():
        events_y = yaml.safe_load(events_path.read_text(encoding="utf-8")) or {}
        code_et = {e.value for e in EventType}
        yaml_et = {e["runtime_event_type"] for e in events_y.get("events", []) if e.get("runtime_event_type")}
        if code_et != yaml_et:
            print(f"[ERROR] EventType mismatch code={sorted(code_et)} vs events.yaml={sorted(yaml_et)}")
            errors += 1
        env_fields = [f.name for f in dataclasses.fields(EventEnvelopeV1)]
        dlq_fields = [f.name for f in dataclasses.fields(DeadLetterEnvelopeV1)]
        if env_fields != events_y.get("envelope_fields"):
            print(f"[ERROR] EventEnvelopeV1 fields mismatch code={env_fields} vs events.yaml")
            errors += 1
        if dlq_fields != events_y.get("dlq_envelope_fields"):
            print(f"[ERROR] DeadLetterEnvelopeV1 fields mismatch code={dlq_fields} vs events.yaml")
            errors += 1

    topics_path = repo_root / "models/data-platform/topics.yaml"
    if topics_path.exists():
        topics_y = yaml.safe_load(topics_path.read_text(encoding="utf-8")) or {}
        code_topics = {t.value for t in KafkaTopic}
        yaml_topics = {t["name"] for t in topics_y.get("topics", [])}
        if code_topics != yaml_topics:
            print(f"[ERROR] KafkaTopic mismatch code={sorted(code_topics)} vs topics.yaml={sorted(yaml_topics)}")
            errors += 1
        code_cgs = {CG_HOT_REDIS, CG_ANALYTICS_CH, CG_LAKEHOUSE_BRONZE, CG_ANOMALY_DETECTOR}
        yaml_cgs = {c["group_id"] for c in topics_y.get("consumer_groups", [])}
        if not code_cgs.issubset(yaml_cgs):
            print(f"[ERROR] Consumer groups missing from topics.yaml: {sorted(code_cgs - yaml_cgs)}")
            errors += 1

    return errors


def validate_repo(repo_root: Path = REPO_ROOT, verify_runtime_contracts: bool = True) -> int:
    """Validate bidirectional YAML traceability, configs, and runtime code-model parity."""
    errors = 0
    req_data = yaml.safe_load(
        (repo_root / "models/requirements/requirements.yaml").read_text(encoding="utf-8")
    )
    br_data = yaml.safe_load(
        (repo_root / "models/requirements/business-rules.yaml").read_text(encoding="utf-8")
    )
    ac_data = yaml.safe_load(
        (repo_root / "models/requirements/acceptance-criteria.yaml").read_text(encoding="utf-8")
    )
    test_data = yaml.safe_load(
        (repo_root / "models/testing/testing.yaml").read_text(encoding="utf-8")
    )
    sec_data = yaml.safe_load(
        (repo_root / "models/security/threat-model.yaml").read_text(encoding="utf-8")
    )
    arch_data = yaml.safe_load(
        (repo_root / "models/architecture/architecture.yaml").read_text(encoding="utf-8")
    )

    known_reqs = {r["id"] for r in req_data.get("functional_requirements", [])} | {
        r["id"] for r in req_data.get("non_functional_requirements", [])
    }
    known_brs = {b["id"] for b in br_data.get("business_rules", [])}
    known_acs = {a["id"] for a in ac_data.get("acceptance_criteria", [])}
    known_tcs = {t["id"] for t in test_data.get("test_cases", [])}
    known_ctrls = {c["id"] for c in sec_data.get("controls", [])}
    known_threats = {t["id"] for t in sec_data.get("threats", [])}

    for ac in ac_data.get("acceptance_criteria", []):
        req_id = ac.get("requirement_id")
        if req_id not in known_reqs:
            print(f"[ERROR] AC {ac.get('id')} references unknown requirement '{req_id}'")
            errors += 1
        for tc_ref in ac.get("test_case_refs", []):
            if tc_ref not in known_tcs:
                print(f"[ERROR] AC {ac.get('id')} references unknown test case '{tc_ref}'")
                errors += 1

    valid_refs = known_reqs | known_brs | known_ctrls
    for tc in test_data.get("test_cases", []):
        for ref in tc.get("requirement_refs", []):
            if ref not in valid_refs:
                print(f"[ERROR] Test Case {tc.get('id')} references unknown artifact '{ref}'")
                errors += 1
        tpath = repo_root / tc.get("test_path", "")
        if not tpath.exists():
            print(f"[ERROR] Test Case {tc.get('id')} test_path does not exist: '{tc.get('test_path')}'")
            errors += 1

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

    for dec in arch_data.get("decisions", []):
        if not (repo_root / dec.get("path", "")).exists():
            print(f"[ERROR] Decision {dec.get('id')} path missing: {dec.get('path')}")
            errors += 1

    errors += validate_deployment_and_observability(repo_root)
    if verify_runtime_contracts:
        errors += validate_runtime_contract_parity(repo_root)

    print(
        f"[validate_traceability] Verified {len(known_reqs)} requirements, {len(known_acs)} ACs, "
        f"{len(known_tcs)} test cases, and {len(known_ctrls)} security controls -> {errors} error(s)."
    )
    return 1 if errors else 0


def main() -> int:
    return validate_repo(REPO_ROOT, verify_runtime_contracts=True)


if __name__ == "__main__":
    sys.exit(main())
