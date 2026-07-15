"""Unit tests for the Lab 4 data pipeline."""

import json
import tempfile
import unittest
from pathlib import Path

from data_pipeline import (
    load_devices,
    normalize_device,
    parse_bool,
    parse_csv,
    parse_json,
    parse_xml,
    parse_yaml,
    validate_devices,
    write_json,
)


ROOT = Path(__file__).parents[1]
DATA = ROOT / "data"


class CsvTests(unittest.TestCase):
    def test_parse_bool(self):
        self.assertIs(parse_bool(" TRUE "), True)
        self.assertIs(parse_bool("false"), False)
        with self.assertRaises(ValueError):
            parse_bool("yes")

    def test_csv_converts_boolean(self):
        records = parse_csv(DATA / "devices.csv")
        self.assertEqual(len(records), 3)
        self.assertIs(records[0]["enabled"], True)
        self.assertIs(records[2]["enabled"], False)


class JsonTests(unittest.TestCase):
    def test_json_devices(self):
        records = parse_json(DATA / "devices.json")
        self.assertEqual(records[0]["name"], "edge-r1")


class YamlTests(unittest.TestCase):
    def test_yaml_devices(self):
        records = parse_yaml(DATA / "devices.yaml")
        self.assertEqual(records[1]["role"], "switch")


class XmlTests(unittest.TestCase):
    def test_xml_devices(self):
        records = parse_xml(DATA / "devices.xml")
        self.assertEqual(records[2]["platform"], "ftd")
        self.assertIs(records[2]["enabled"], False)


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.valid_record = {
            "name": " EDGE-R1 ",
            "management_ip": "192.0.2.10",
            "role": " Router ",
            "platform": " IOSXE ",
            "enabled": True,
            "site": " Hanoi ",
        }

    def test_normalizes_record(self):
        device = normalize_device(self.valid_record)
        self.assertEqual(device["name"], "edge-r1")
        self.assertEqual(device["role"], "router")
        self.assertEqual(device["site"], "hanoi")

    def test_rejects_missing_unknown_and_invalid_fields(self):
        missing = self.valid_record.copy()
        missing.pop("role")
        with self.assertRaises(ValueError):
            normalize_device(missing)
        unknown = self.valid_record | {"password": "must-not-appear"}
        with self.assertRaises(ValueError):
            normalize_device(unknown)
        invalid_ip = self.valid_record | {"management_ip": "999.1.1.1"}
        with self.assertRaises(ValueError):
            normalize_device(invalid_ip)

    def test_rejects_duplicates(self):
        with self.assertRaises(ValueError):
            validate_devices([self.valid_record, self.valid_record.copy()])


class PipelineTests(unittest.TestCase):
    def test_all_formats_are_equivalent(self):
        results = [
            load_devices(DATA / name)
            for name in ("devices.csv", "devices.json", "devices.yaml", "devices.xml")
        ]
        self.assertTrue(all(result == results[0] for result in results[1:]))

    def test_write_json_round_trip(self):
        devices = load_devices(DATA / "devices.yaml")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "nested" / "devices.json"
            write_json(output, devices)
            document = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(document, {"devices": devices})


if __name__ == "__main__":
    unittest.main()

