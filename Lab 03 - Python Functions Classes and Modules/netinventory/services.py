"""Inventory services composed from Device objects."""

from .models import Device


class Inventory:
    """A collection of Device objects with reporting operations."""

    def __init__(self, devices: list[Device] | None = None) -> None:
        raise NotImplementedError("Complete Inventory.__init__ in Lab 3")

    def add(self, device: Device) -> None:
        raise NotImplementedError("Complete Inventory.add in Lab 3")

    def enabled(self) -> list[Device]:
        raise NotImplementedError("Complete Inventory.enabled in Lab 3")

    def by_role(self, role: str) -> list[Device]:
        raise NotImplementedError("Complete Inventory.by_role in Lab 3")

    def roles(self) -> set[str]:
        raise NotImplementedError("Complete Inventory.roles in Lab 3")

    def __len__(self) -> int:
        raise NotImplementedError("Complete Inventory.__len__ in Lab 3")

