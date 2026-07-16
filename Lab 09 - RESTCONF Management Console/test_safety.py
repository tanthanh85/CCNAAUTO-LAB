import unittest

from restconf import validate_loopback, validate_route


class SafetyRules(unittest.TestCase):
    def test_default_route_is_blocked(self):
        with self.assertRaisesRegex(ValueError, "default route"):
            validate_route({"prefix": "0.0.0.0", "mask": "0.0.0.0", "next_hop": "192.0.2.1"})

    def test_regular_route_is_allowed(self):
        network = validate_route({"prefix": "192.0.2.0", "mask": "255.255.255.0", "next_hop": "198.51.100.1"})
        self.assertEqual(str(network), "192.0.2.0/24")

    def test_loopback_zero_is_blocked(self):
        with self.assertRaisesRegex(ValueError, "greater than 0"):
            validate_loopback({"number": 0, "address": "198.18.9.1", "mask": "255.255.255.255"})

    def test_managed_loopback_is_allowed(self):
        self.assertEqual(validate_loopback({"number": 901, "address": "198.18.9.1", "mask": "255.255.255.255"}), 901)


if __name__ == "__main__":
    unittest.main()
