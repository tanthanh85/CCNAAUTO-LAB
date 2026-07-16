"""Tests for the beginner Lab 4 data workflow."""

import json
import tempfile
import unittest
from pathlib import Path

from data_pipeline import (
    build_report,
    count_roles,
    enabled_devices,
    parse_bool,
    read_csv,
    read_devices,
    read_json,
    read_xml,
    read_yaml,
    write_report,
)

ROOT = Path(__file__).parents[1]
DATA = ROOT / "data"


class ReaderTests(unittest.TestCase):
    def test_parse_bool(self):
        self.assertIs(parse_bool(" TRUE "), True)
        self.assertIs(parse_bool("false"), False)
        with self.assertRaises(ValueError):
            parse_bool("yes")

    def test_csv(self):
        devices = read_csv(DATA / "devices.csv")
        self.assertEqual(len(devices), 3)
        self.assertIs(devices[0]["enabled"], True)

    def test_json(self):
        self.assertEqual(read_json(DATA / "devices.json")[0]["name"], "edge-r1")

    def test_yaml(self):
        self.assertEqual(read_yaml(DATA / "devices.yaml")[1]["role"], "switch")

    def test_xml(self):
        devices = read_xml(DATA / "devices.xml")
        self.assertEqual(devices[2]["platform"], "ftd")
        self.assertIs(devices[2]["enabled"], False)

    def test_reader_selection(self):
        for filename in ("devices.csv", "devices.json", "devices.yaml", "devices.xml"):
            self.assertEqual(len(read_devices(DATA / filename)), 3)
        with self.assertRaises(ValueError):
            read_devices(DATA / "devices.txt")


class ProcessingTests(unittest.TestCase):
    def setUp(self):
        self.devices = read_json(DATA / "devices.json")

    def test_extract_enabled_devices(self):
        self.assertEqual(
            [item["name"] for item in enabled_devices(self.devices)],
            ["edge-r1", "access-sw1"],
        )

    def test_count_roles(self):
        self.assertEqual(count_roles(self.devices), {"router": 1, "switch": 1, "firewall": 1})

    def test_build_and_write_report(self):
        report = build_report(self.devices, DATA / "devices.json")
        self.assertEqual(report["device_count"], 3)
        self.assertEqual(report["enabled_count"], 2)
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "nested" / "report.json"
            write_report(destination, report)
            saved = json.loads(destination.read_text(encoding="utf-8"))
        self.assertEqual(saved, report)


if __name__ == "__main__":
    unittest.main()
