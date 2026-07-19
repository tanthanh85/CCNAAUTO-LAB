import ipaddress
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from netmiko import ConnectHandler

ROOT = Path(__file__).parent


def load_inventory():
    data = yaml.safe_load((ROOT / "device.yaml").read_text())
    items = data["loopbacks"]
    if len(items) != 10:
        raise ValueError("device.yaml must contain exactly ten loopbacks")
    names, addresses = set(), set()
    for item in items:
        name = f"Loopback{item['id']}"
        if not isinstance(item["id"], int) or not 701 <= item["id"] <= 710:
            raise ValueError("Loopback IDs must be integers from 701 through 710")
        address = ipaddress.ip_interface(item["ipv4"])
        if address.version != 4 or address.network.prefixlen != 32:
            raise ValueError(f"{name} must use an IPv4 /32")
        if not str(item["description"]).startswith("LAB7_"):
            raise ValueError(f"{name} requires a LAB7_ description")
        if name in names or str(address.ip) in addresses:
            raise ValueError("Interface names and addresses must be unique")
        names.add(name)
        addresses.add(str(address.ip))
    if names != {f"Loopback{number}" for number in range(701, 711)}:
        raise ValueError("Define Loopback701 through Loopback710 exactly once")
    return data


def render_config(data):
    env = Environment(
        loader=FileSystemLoader(ROOT / "templates"),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["address"] = lambda value: str(ipaddress.ip_interface(value).ip)
    env.filters["netmask"] = lambda value: str(ipaddress.ip_interface(value).netmask)
    return (
        env.get_template("loopbacks.j2").render(loopbacks=data["loopbacks"]).strip()
        + "\n"
    )


def connect(data):
    load_dotenv(ROOT / ".env")
    username, password = os.getenv("LAB_USERNAME"), os.getenv("LAB_PASSWORD")
    if not username or not password:
        raise RuntimeError("Set LAB_USERNAME and LAB_PASSWORD in .env")
    params = {
        **data["device"],
        "username": username,
        "password": password,
        "secret": os.getenv("LAB_SECRET", ""),
    }
    if params["host"].startswith("REPLACE_"):
        raise RuntimeError("Replace the device host in device.yaml")
    return ConnectHandler(**params)
