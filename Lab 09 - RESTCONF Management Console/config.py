"""Model paths for the IOS XE release used by the course sandbox.

Confirm these in YANG Suite. IOS XE releases can expose different revisions or
payload shapes; keeping paths in one file makes the adapter easy to update.
"""

ROUTES_URI = "/restconf/data/Cisco-IOS-XE-native:native/ip/route/ip-route-interface-forwarding-list"
ROUTE_ITEM_URI = ROUTES_URI + "={prefix},{mask}"
LOOPBACKS_URI = "/restconf/data/Cisco-IOS-XE-native:native/interface/Loopback"
LOOPBACK_ITEM_URI = LOOPBACKS_URI + "={number}"
INTERFACE_STATS_URI = (
    "/restconf/data/Cisco-IOS-XE-interfaces-oper:interfaces/interface=GigabitEthernet1"
)
