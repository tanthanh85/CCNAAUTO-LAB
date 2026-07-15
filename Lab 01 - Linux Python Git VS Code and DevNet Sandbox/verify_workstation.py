#!/usr/bin/env python3
"""Verify the Lab 01 Python environment and parse the sample inventory."""

from __future__ import annotations

import ipaddress
import json
import platform
import sys
from pathlib import Path

import requests
import yaml


INVENTORY_FILE = Path(__file__).with_name("inventory.yaml")


def load_inventory(path: Path) -> dict:
    """Load YAML and validate the small structure used by this lab."""
    with path.open(encoding="utf-8") as stream:
        inventory = yaml.safe_load(stream)

    if not isinstance(inventory, dict):
        raise ValueError("The inventory root must be a mapping.")
    if not isinstance(inventory.get("lab"), str):
        raise ValueError("The inventory requires a string 'lab' value.")
    if not isinstance(inventory.get("devices"), list):
        raise ValueError("The inventory requires a 'devices' list.")

    for position, device in enumerate(inventory["devices"], start=1):
        if not isinstance(device, dict):
            raise ValueError(f"Device {position} must be a mapping.")
        for key in ("name", "management_ip", "platform"):
            if not isinstance(device.get(key), str):
                raise ValueError(f"Device {position} requires a string '{key}'.")
        ipaddress.ip_address(device["management_ip"])

    return inventory


def main() -> int:
    """Display interpreter, dependency, and parsed-inventory information."""
    inventory = load_inventory(INVENTORY_FILE)
    device_names = [device["name"] for device in inventory["devices"]]

    print(f"Python executable : {sys.executable}")
    print(f"Python version    : {platform.python_version()}")
    print(f"Requests version  : {requests.__version__}")
    print(f"PyYAML version    : {yaml.__version__}")
    print(f"Lab name          : {inventory['lab']}")
    print(f"Device count      : {len(device_names)}")
    print(f"Device names      : {', '.join(device_names)}")
    print("JSON representation:")
    print(json.dumps(inventory, indent=2))
    print("Lab 01 Python environment is ready.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, yaml.YAMLError) as error:
        print(f"Validation failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error

