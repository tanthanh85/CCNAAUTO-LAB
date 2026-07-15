#!/usr/bin/env python3
"""Black-box validation for the learner's Lab 2 script."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).with_name("inventory_report.py")
REQUIRED_TEXT = (
    "Cisco DevNet Associate inventory",
    "edge-r1",
    "access-sw1",
    "lab-fw1",
    "Average measured latency",
    "Connection-attempt simulation",
    "Attempt 3 of 3",
    "Simulated connection succeeded",
)


def main() -> int:
    if not SCRIPT.exists():
        print("FAIL: inventory_report.py does not exist", file=sys.stderr)
        return 1

    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        input="10\n",
        text=True,
        capture_output=True,
        timeout=10,
        check=False,
    )
    if result.returncode != 0:
        print("FAIL: learner script returned a nonzero status", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        return 1

    missing = [text for text in REQUIRED_TEXT if text not in result.stdout]
    if "WARNING" not in result.stdout:
        missing.append("WARNING for threshold 10")
    if missing:
        print("FAIL: expected output is missing:", file=sys.stderr)
        for text in missing:
            print(f"  - {text}", file=sys.stderr)
        return 1

    print("Lab 2 validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

