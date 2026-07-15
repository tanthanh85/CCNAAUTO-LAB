"""Behavior tests for the Lab 3 package."""

import unittest

from netinventory.formatters import format_device_label, normalize_interface
from netinventory.models import Device
from netinventory.services import Inventory


class FormatterTests(unittest.TestCase):
    def test_normalize_long_interface(self):
        self.assertEqual(normalize_interface(" GigabitEthernet 1/0/1 "), "gi1/0/1")

    def test_normalize_unknown_interface(self):
        self.assertEqual(normalize_interface("Loopback 0"), "loopback0")

    def test_label_and_default_role(self):
        self.assertEqual(format_device_label(" EDGE-R1 ", "Router"), "edge-r1 [router]")
        self.assertEqual(format_device_label("R2"), "r2 [unknown]")


class DeviceTests(unittest.TestCase):
    def test_device_normalizes_fields(self):
        device = Device(" EDGE-R1 ", "192.0.2.10", "Router", "IOSXE")
        self.assertEqual(device.name, "edge-r1")
        self.assertEqual(device.role, "router")
        self.assertEqual(device.platform, "iosxe")

    def test_device_rejects_invalid_address(self):
        with self.assertRaises(ValueError):
            Device("bad", "999.1.1.1", "router")

    def test_device_label_and_repr(self):
        device = Device("r1", "192.0.2.1", "router")
        self.assertEqual(device.label(), "r1 [router]")
        self.assertIn("Device(", repr(device))


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.r1 = Device("r1", "192.0.2.1", "router")
        self.sw1 = Device("sw1", "192.0.2.2", "switch", enabled=False)

    def test_add_filter_roles_and_length(self):
        inventory = Inventory([self.r1])
        inventory.add(self.sw1)
        self.assertEqual(len(inventory), 2)
        self.assertEqual(inventory.enabled(), [self.r1])
        self.assertEqual(inventory.by_role(" SWITCH "), [self.sw1])
        self.assertEqual(inventory.roles(), {"router", "switch"})

    def test_rejects_duplicate_name(self):
        inventory = Inventory([self.r1])
        with self.assertRaises(ValueError):
            inventory.add(Device("r1", "192.0.2.9", "router"))

    def test_defensive_copy(self):
        source = [self.r1]
        inventory = Inventory(source)
        source.append(self.sw1)
        self.assertEqual(len(inventory), 1)


if __name__ == "__main__":
    unittest.main()
