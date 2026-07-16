#!/usr/bin/env python3
"""Verify the running Lab 10 console without changing a router."""

import json
import sys
import urllib.error
import urllib.request

URL = "http://127.0.0.1:8000/api/routers"

try:
    with urllib.request.urlopen(URL, timeout=5) as response:
        body = response.read().decode("utf-8")
        inventory = json.loads(body)
        if response.status != 200 or not isinstance(inventory, list):
            raise ValueError("Expected HTTP 200 and a JSON list")
except (OSError, ValueError, json.JSONDecodeError) as error:
    print(f"Container verification failed: {error}", file=sys.stderr)
    raise SystemExit(1) from error

print(f"Container verification passed; inventory entries: {len(inventory)}")
