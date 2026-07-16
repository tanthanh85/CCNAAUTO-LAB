"""Classes that represent network inventory objects."""

import ipaddress

from .formatters import format_device_label


class Device:
    """Represent one network device and its basic properties."""

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
        """Return a readable label for this device."""
        raise NotImplementedError("Complete Device.label in Lab 3")

    def disable(self) -> None:
        """Mark this device as unavailable for automation."""
        raise NotImplementedError("Complete Device.disable in Lab 3")

    def __repr__(self) -> str:
        """Return a developer-oriented representation of this object."""
        raise NotImplementedError("Complete Device.__repr__ in Lab 3")
