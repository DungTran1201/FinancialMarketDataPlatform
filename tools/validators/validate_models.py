"""Validates canonical YAML models and .template.yaml schemas across models/."""

from __future__ import annotations

import sys
from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
MODELS_ROOT = REPO_ROOT / "models"

EXPECTED_MODEL_DIRS = {
    "requirements",
    "process",
    "context",
    "architecture",
    "domain",
    "api",
    "interaction",
    "state",
    "security",
    "ux",
    "testing",
    "deployment",
}

ALLOWED_STATUSES = {
    "TEMPLATE",
    "DRAFT",
    "PROPOSED",
    "IN_REVIEW",
    "REVIEW_REQUIRED",
    "APPROVED",
    "BASELINED",
    "DEPRECATED",
    "SUPERSEDED",
}

REQUIRED_META_KEYS = {
    "model_id",
    "name",
    "description",
    "status",
    "canonical_model",
    "created_at",
    "updated_at",
    "owner",
    "source_documents",
}


def main() -> int:
    errors = 0
    if not MODELS_ROOT.exists():
        print("[ERROR] models/ directory does not exist.")
        return 1

    existing_dirs = {p.name for p in MODELS_ROOT.iterdir() if p.is_dir()}
    missing = EXPECTED_MODEL_DIRS - existing_dirs
    if missing:
        print(f"[ERROR] Missing model directories: {sorted(missing)}")
        errors += 1

    yaml_files = sorted(MODELS_ROOT.rglob("*.yaml"))
    seen_model_ids: set[str] = set()

    for yf in yaml_files:
        rel = yf.relative_to(REPO_ROOT).as_posix()
        try:
            data = yaml.safe_load(yf.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"[ERROR] {rel}: Invalid YAML syntax: {exc}")
            errors += 1
            continue

        if not isinstance(data, dict) or data.get("version") != "1.0":
            print(f"[ERROR] {rel}: Missing top-level version: '1.0'")
            errors += 1
            continue

        meta = data.get("metadata")
        if not isinstance(meta, dict):
            print(f"[ERROR] {rel}: Missing 'metadata' dictionary")
            errors += 1
            continue

        missing_keys = REQUIRED_META_KEYS - set(meta.keys())
        if missing_keys:
            print(f"[ERROR] {rel}: Missing metadata keys: {sorted(missing_keys)}")
            errors += 1

        model_id = str(meta.get("model_id", ""))
        if model_id in seen_model_ids:
            print(f"[ERROR] {rel}: Duplicate model_id '{model_id}'")
            errors += 1
        seen_model_ids.add(model_id)

        status = meta.get("status")
        if status not in ALLOWED_STATUSES:
            print(f"[ERROR] {rel}: Invalid status '{status}'")
            errors += 1

        for src_doc in meta.get("source_documents", []):
            if not (REPO_ROOT / src_doc).exists():
                print(f"[ERROR] {rel}: Referenced source_document does not exist: '{src_doc}'")
                errors += 1

    print(f"[validate_models] Checked {len(yaml_files)} YAML model files -> {errors} error(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
