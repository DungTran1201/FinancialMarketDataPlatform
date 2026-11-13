"""Validates AGENTS.md, .agents/ roles, rules, skills, configs, hooks.json, and manifests."""

from __future__ import annotations

import json
import sys
from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = REPO_ROOT / ".agents"


def main() -> int:
    errors = 0
    if not (REPO_ROOT / "AGENTS.md").exists():
        print("[ERROR] Root AGENTS.md is missing.")
        errors += 1

    # 1. Check hooks.json
    hooks_path = AGENTS_DIR / "hooks.json"
    if not hooks_path.exists():
        print("[ERROR] .agents/hooks.json is missing.")
        errors += 1
    else:
        hooks = json.loads(hooks_path.read_text(encoding="utf-8"))
        for hname, hcfg in hooks.items():
            for phase in ("PreToolUse", "PostToolUse", "Stop"):
                for entry in hcfg.get(phase, []):
                    for hk in entry.get("hooks", [entry]):
                        cmd = hk.get("command", "")
                        if cmd.startswith("python "):
                            script_rel = cmd.replace("python ", "").strip()
                            candidate_paths = [
                                (AGENTS_DIR / script_rel).resolve(),
                                (REPO_ROOT / script_rel).resolve(),
                            ]
                            if not any(cp.exists() for cp in candidate_paths):
                                print(f"[ERROR] hooks.json ({hname}): Missing script '{script_rel}'")
                                errors += 1

    # 2. Check skill-registry.yaml and skills_manifest.json match .agents/skills/
    reg = yaml.safe_load((AGENTS_DIR / "skill-registry.yaml").read_text(encoding="utf-8"))
    manifest = json.loads((AGENTS_DIR / "skills_manifest.json").read_text(encoding="utf-8"))

    active_skills = set(reg.get("active_skills", []))
    manifest_skills = {s["id"] for s in manifest.get("skills", [])}
    disk_skills = {
        p.name for p in (AGENTS_DIR / "skills").iterdir() if p.is_dir()
    }

    if active_skills != manifest_skills or active_skills != disk_skills:
        print(
            f"[ERROR] Skill mismatch: registry={len(active_skills)}, "
            f"manifest={len(manifest_skills)}, disk={len(disk_skills)}"
        )
        errors += 1

    for sk in disk_skills:
        sfile = AGENTS_DIR / "skills" / sk / "SKILL.md"
        if not sfile.exists():
            print(f"[ERROR] Missing SKILL.md in .agents/skills/{sk}/")
            errors += 1

    # 3. Check 11 Agent roles and 10 Agent rules
    roles = [p for p in (AGENTS_DIR / "agents").glob("*.md") if p.name.lower() != "readme.md"]
    rules = [p for p in (AGENTS_DIR / "rules").glob("*.md") if p.name.lower() != "readme.md"]
    if len(roles) < 11:
        print(f"[ERROR] Expected >= 11 Agent roles in .agents/agents/, found {len(roles)}")
        errors += 1
    if len(rules) < 10:
        print(f"[ERROR] Expected >= 10 Agent rules in .agents/rules/, found {len(rules)}")
        errors += 1

    print(
        f"[validate_agent_config] Checked {len(roles)} roles, {len(rules)} rules, "
        f"{len(active_skills)} skills, and hooks.json -> {errors} error(s)."
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
