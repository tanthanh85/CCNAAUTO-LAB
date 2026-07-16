#!/usr/bin/env python3
"""Read device data, extract values, iterate over records, and write a report."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import xmltodict
import yaml


def parse_bool(value: str) -> bool:
    """Convert the text true or false into a Python Boolean."""
    raise NotImplementedError("Complete parse_bool in Lab 4")


def read_csv(path: Path) -> list[dict]:
    """Read device records from CSV."""
    raise NotImplementedError("Complete read_csv in Lab 4")


def read_json(path: Path) -> list[dict]:
    """Read device records from JSON."""
    raise NotImplementedError("Complete read_json in Lab 4")


def read_yaml(path: Path) -> list[dict]:
    """Read device records from YAML."""
    raise NotImplementedError("Complete read_yaml in Lab 4")


def read_xml(path: Path) -> list[dict]:
    """Read device records from XML with xmltodict."""
    raise NotImplementedError("Complete read_xml in Lab 4")


READERS = {
    ".csv": read_csv,
    ".json": read_json,
    ".yaml": read_yaml,
    ".yml": read_yaml,
    ".xml": read_xml,
}


def read_devices(path: Path) -> list[dict]:
    """Select a reader from the filename extension."""
    reader = READERS.get(path.suffix.lower())
    if reader is None:
        raise ValueError(f"Unsupported file type: {path.suffix}")
    return reader(path)


def enabled_devices(devices: list[dict]) -> list[dict]:
    """Extract devices whose enabled value is True."""
    raise NotImplementedError("Complete enabled_devices in Lab 4")


def count_roles(devices: list[dict]) -> dict[str, int]:
    """Count devices by role with a loop and dictionary."""
    raise NotImplementedError("Complete count_roles in Lab 4")


def build_report(devices: list[dict], source: Path) -> dict:
    """Build a JSON-serializable report from the device list."""
    active = enabled_devices(devices)
    return {
        "source": source.name,
        "device_count": len(devices),
        "enabled_count": len(active),
        "roles": count_roles(devices),
        "enabled_devices": [device["name"] for device in active],
        "devices": devices,
    }


def write_report(path: Path, report: dict) -> None:
    """Write the report as formatted JSON."""
    raise NotImplementedError("Complete write_report in Lab 4")


def argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="CSV, JSON, YAML, or XML input")
    parser.add_argument("--output", type=Path, default=Path("output/report.json"))
    return parser


def main() -> int:
    args = argument_parser().parse_args()
    try:
        devices = read_devices(args.input)
        report = build_report(devices, args.input)
        write_report(args.output, report)
    except (OSError, KeyError, TypeError, ValueError, yaml.YAMLError) as error:
        print(f"Data processing failed: {error}")
        return 1

    print(f"Read {report['device_count']} devices from {args.input}")
    print(f"Enabled devices: {report['enabled_count']}")
    for role, count in sorted(report["roles"].items()):
        print(f"  {role}: {count}")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
