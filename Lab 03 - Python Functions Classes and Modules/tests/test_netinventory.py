"""Behavior tests for the beginner Lab 3 package."""

import unittest

from netinventory.formatters import connection_message, format_device_label
from netinventory.models import Device
from netinventory.services import Inventory


class FunctionTests(unittest.TestCase):
    def test_device_label(self):
        self.assertEqual(format_device_label("edge-r1", "router"), "edge-r1 [router]")
        self.assertEqual(format_device_label("r2"), "r2 [unknown]")

    def test_connection_message_and_default_port(self):
        self.assertEqual(
            connection_message("edge-r1", "192.0.2.10"),
            "Connecting to edge-r1 at 192.0.2.10:22",
        )
        self.assertTrue(connection_message("r1", "192.0.2.1", 830).endswith(":830"))


class DeviceTests(unittest.TestCase):
    def test_device_properties_and_methods(self):
        device = Device("edge-r1", "192.0.2.10", "router", "iosxe")
        self.assertEqual(device.name, "edge-r1")
        self.assertEqual(device.management_ip, "192.0.2.10")
        self.assertEqual(device.label(), "edge-r1 [router]")
        self.assertTrue(device.enabled)
        device.disable()
        self.assertFalse(device.enabled)

    def test_device_rejects_invalid_values(self):
        with self.assertRaises(ValueError):
            Device("", "192.0.2.1", "router")
        with self.assertRaises(ValueError):
            Device("bad", "999.1.1.1", "router")
        with self.assertRaises(TypeError):
            Device("r1", "192.0.2.1", "router", enabled="yes")

    def test_repr(self):
        self.assertIn("Device(", repr(Device("r1", "192.0.2.1", "router")))


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.r1 = Device("r1", "192.0.2.1", "router")
        self.sw1 = Device("sw1", "192.0.2.2", "switch", enabled=False)

    def test_add_search_and_length(self):
        inventory = Inventory([self.r1])
        inventory.add(self.sw1)
        self.assertEqual(len(inventory), 2)
        self.assertEqual(inventory.enabled(), [self.r1])
        self.assertEqual(inventory.by_role("switch"), [self.sw1])

    def test_rejects_wrong_type_and_duplicate_name(self):
        inventory = Inventory([self.r1])
        with self.assertRaises(TypeError):
            inventory.add("r2")
        with self.assertRaises(ValueError):
            inventory.add(Device("r1", "192.0.2.9", "router"))


if __name__ == "__main__":
    unittest.main()
