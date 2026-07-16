"""Small reusable formatting functions for the network inventory."""


def format_device_label(name: str, role: str = "unknown") -> str:
    """Return a readable label containing a device name and role."""
    raise NotImplementedError("Complete format_device_label in Lab 3")


def connection_message(name: str, address: str, port: int = 22) -> str:
    """Return a message describing a planned device connection."""
    raise NotImplementedError("Complete connection_message in Lab 3")
