#!/usr/bin/env python3
"""Command-line entry point for the Lab 3 network inventory."""

from netinventory import Device, Inventory, connection_message


def build_inventory() -> Inventory:
    """Create and return the small training inventory."""
    raise NotImplementedError("Complete build_inventory in Lab 3")


def main() -> int:
    """Display the enabled devices in the training inventory."""
    raise NotImplementedError("Complete main in Lab 3")


if __name__ == "__main__":
    raise SystemExit(main())
