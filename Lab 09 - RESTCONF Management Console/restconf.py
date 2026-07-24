import ipaddress
import os
import time
from urllib.parse import quote

import requests

import config

HEADERS = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json",
}


class RestconfError(RuntimeError):
    pass


class IOSXE:
    def __init__(self, router):
        self.router = router
        self.base = f"https://{router['ip']}:{router['restconf_port']}"
        self.session = requests.Session()
        self.session.auth = (router["username"], router["password"])
        self.session.headers.update(HEADERS)
        ca = os.getenv("LAB_CA_BUNDLE", "").strip()
        self.session.verify = ca if ca else True

    def request(self, method, uri, allow_not_found=False, **kwargs):
        try:
            response = self.session.request(
                method, self.base + uri, timeout=12, **kwargs
            )
        except requests.RequestException as exc:
            raise RestconfError(f"Connection failed: {exc}") from exc
        if response.status_code == 404 and allow_not_found:
            return {}
        if response.status_code not in {200, 201, 204}:
            detail = response.text[:600] or response.reason
            raise RestconfError(f"HTTP {response.status_code}: {detail}")
        return response.json() if response.content else {}

    def routes(self):
        data = self.request("GET", config.ROUTES_URI, allow_not_found=True)
        items = find_list(data, "ip-route-interface-forwarding-list")
        result = []
        for item in items:
            next_hops = item.get("fwd-list", [])
            if isinstance(next_hops, dict):
                next_hops = [next_hops]
            if not next_hops:
                next_hops = [{"fwd": ""}]
            for hop in next_hops:
                result.append(
                    {
                        "prefix": item.get("prefix", ""),
                        "mask": item.get("mask", ""),
                        "next_hop": hop.get("fwd", hop.get("next-hop", "")),
                    }
                )
        return result

    def put_route(self, route):
        network = validate_route(route)
        prefix, mask = str(network.network_address), str(network.netmask)
        uri = config.ROUTE_ITEM_URI.format(
            prefix=quote(prefix, safe=""),
            mask=quote(mask, safe=""),
        )
        payload = {
            "Cisco-IOS-XE-native:ip-route-interface-forwarding-list": {
                "prefix": prefix,
                "mask": mask,
                "fwd-list": [{"fwd": route["next_hop"]}],
            }
        }
        self.request("PUT", uri, json=payload)

    def delete_route(self, route):
        network = validate_route(route)
        uri = config.ROUTE_ITEM_URI.format(
            prefix=quote(str(network.network_address), safe=""),
            mask=quote(str(network.netmask), safe=""),
        )
        self.request("DELETE", uri)

    def loopbacks(self):
        data = self.request("GET", config.LOOPBACKS_URI, allow_not_found=True)
        items = find_list(data, "Loopback")
        result = []
        for item in items:
            primary = item.get("ip", {}).get("address", {}).get("primary", {})
            result.append(
                {
                    "number": int(item.get("name", item.get("number", 0))),
                    "description": item.get("description", ""),
                    "address": primary.get("address", ""),
                    "mask": primary.get("mask", ""),
                }
            )
        return result

    def put_loopback(self, item):
        number = validate_loopback(item)
        payload = {
            "Cisco-IOS-XE-native:Loopback": {
                "name": number,
                "description": item.get("description", "LAB9_MANAGED"),
                "ip": {
                    "address": {
                        "primary": {"address": item["address"], "mask": item["mask"]}
                    }
                },
            }
        }
        self.request(
            "PUT", config.LOOPBACK_ITEM_URI.format(number=number), json=payload
        )

    def delete_loopback(self, item):
        number = int(item["number"])
        if number == 0:
            raise ValueError("Loopback0 is protected")
        self.request("DELETE", config.LOOPBACK_ITEM_URI.format(number=number))

    def counters(self):
        data = self.request("GET", config.INTERFACE_STATS_URI)
        interface = find_dict(data, "interface")
        stats = interface.get("statistics", interface)
        return {
            "time": time.time(),
            "in_octets": integer(stats, "in-octets-64", "in-octets"),
            "out_octets": integer(stats, "out-octets-64", "out-octets"),
            "speed_bps": integer(interface, "speed", "bandwidth") or 1_000_000_000,
        }


def find_list(value, suffix):
    if isinstance(value, dict):
        for key, child in value.items():
            if key.split(":")[-1] == suffix:
                return child if isinstance(child, list) else [child]
            found = find_list(child, suffix)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = find_list(child, suffix)
            if found:
                return found
    return []


def find_dict(value, suffix):
    items = find_list(value, suffix)
    return items[0] if items and isinstance(items[0], dict) else {}


def integer(mapping, *keys):
    for key in keys:
        if key in mapping:
            try:
                return int(mapping[key])
            except (TypeError, ValueError):
                pass
    return 0


def validate_route(item):
    network = ipaddress.ip_network(f"{item['prefix']}/{item['mask']}", strict=False)
    if network.version != 4:
        raise ValueError("Only IPv4 static routes are supported")
    if network.prefixlen == 0:
        raise ValueError("The default route is protected")
    if ipaddress.ip_address(item["next_hop"]).version != 4:
        raise ValueError("Next hop must be IPv4")
    return network


def validate_loopback(item):
    number = int(item["number"])
    if not 1 <= number <= 2147483647:
        raise ValueError("Loopback number must be greater than 0")
    address = ipaddress.ip_address(item["address"])
    mask = ipaddress.ip_address(item["mask"])
    if address.version != 4 or mask.version != 4:
        raise ValueError("Loopback address and mask must be IPv4")
    try:
        ipaddress.ip_network(f"0.0.0.0/{item['mask']}")
    except ValueError as exc:
        raise ValueError("Loopback mask must be a contiguous IPv4 subnet mask") from exc
    return number
