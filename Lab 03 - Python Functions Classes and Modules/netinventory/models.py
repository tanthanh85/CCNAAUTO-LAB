"""Domain models for the network inventory."""

import ipaddress

from .formatters import format_device_label


class Device:
    """A validated network-device record."""

    def __init__(
        self,
        name: str,
        management_ip: str,
        role: str,
        platform: str = "unknown",
        enabled: bool = True,
    ) -> None:
        raise NotImplementedError("Complete Device.__init__ in Lab 3")

    def label(self) -> str:
        """Return the standard display label."""
        raise NotImplementedError("Complete Device.label in Lab 3")

    def __repr__(self) -> str:
        raise NotImplementedError("Complete Device.__repr__ in Lab 3")

