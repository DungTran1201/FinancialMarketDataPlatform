"""PreToolUse hook guarding against destructive shell commands."""

from __future__ import annotations

import json
import sys

FORBIDDEN_PATTERNS = ("rm -rf /", "format c:", "del /f /s /q c:\\")


def main() -> int:
    raw_stdin = ""
    if not sys.stdin.isatty():
        try:
            raw_stdin = sys.stdin.read()
        except Exception:
            raw_stdin = ""

    command_text = " ".join(sys.argv[1:])
    if raw_stdin.strip():
        try:
            payload = json.loads(raw_stdin)
            cmd_arg = (
                payload.get("toolCall", {})
                .get("args", {})
                .get("CommandLine", "")
            )
            command_text = f"{command_text} {cmd_arg}"
        except Exception:
            command_text = f"{command_text} {raw_stdin}"

    lowered = command_text.lower()
    for pat in FORBIDDEN_PATTERNS:
        if pat in lowered:
            print(
                json.dumps(
                    {
                        "decision": "deny",
                        "reason": f"Destructive command pattern detected: {pat}",
                    }
                )
            )
            return 0

    print(json.dumps({"decision": "allow"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())

