"""Validates .agents/config/artifact-matrix.yaml, change-types.yaml, and document-map.yaml."""

from __future__ import annotations

import sys
from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CFG_DIR = REPO_ROOT / ".agents" / "config"


def main() -> int:
    errors = 0
    matrix = yaml.safe_load((CFG_DIR / "artifact-matrix.yaml").read_text(encoding="utf-8"))
    ctypes = yaml.safe_load((CFG_DIR / "change-types.yaml").read_text(encoding="utf-8"))
    docmap = yaml.safe_load((CFG_DIR / "document-map.yaml").read_text(encoding="utf-8"))

    matrix_types = set(matrix.get("change_types", {}).keys())
    configured_types = set(ctypes.get("change_types", {}).keys())
    if matrix_types != configured_types:
        print(
            f"[ERROR] Mismatch between artifact-matrix change_types {matrix_types} "
            f"and change-types.yaml {configured_types}"
        )
        errors += 1

    # Check all paths in document-map.yaml exist on disk
    for phase_key, pinfo in docmap.get("product_lifecycle_phases", {}).items():
        for key in ("path", "templates_dir", "diagrams_dir"):
            rel = pinfo.get(key)
            if rel and not (REPO_ROOT / rel).exists():
                print(f"[ERROR] document-map.yaml ({phase_key}.{key}) path does not exist: {rel}")
                errors += 1
        for npath in pinfo.get("nested_paths", []):
            if not (REPO_ROOT / npath).exists():
                print(f"[ERROR] document-map.yaml ({phase_key}) nested path does not exist: {npath}")
                errors += 1
        for mpath in pinfo.get("canonical_models", []):
            if not (REPO_ROOT / mpath).exists():
                print(f"[ERROR] document-map.yaml ({phase_key}) model does not exist: {mpath}")
                errors += 1

    print(
        f"[validate_artifact_matrix] Checked {len(matrix_types)} change types and 15 phase mappings -> {errors} error(s)."
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
