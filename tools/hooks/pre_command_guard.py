"""PreToolUse hook guarding against destructive shell commands."""

from __future__ import annotations

import sys

FORBIDDEN_PATTERNS = ("rm -rf /", "format c:", "del /f /s /q c:\\")


def main() -> int:
    args = " ".join(sys.argv[1:]).lower()
    for pat in FORBIDDEN_PATTERNS:
        if pat in args:
            print(f"[BLOCKED] Destructive command pattern detected: {pat}")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
