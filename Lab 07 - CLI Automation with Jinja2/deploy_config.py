import argparse
from common import connect, load_inventory, render_config

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()
data = load_inventory()
rendered = render_config(data)
commands = [
    line for line in rendered.splitlines() if line.strip() and line.strip() != "!"
]
print(rendered)
if not args.apply:
    print("Dry run only. Use --apply after reviewing every command.")
    raise SystemExit
with connect(data) as device:
    parsed = device.send_command("show ip interface brief", use_textfsm=True)
    if not isinstance(parsed, list):
        raise RuntimeError("Pre-check requires structured TextFSM output")
    existing_names = {
        row.get("intf", row.get("interface")) for row in parsed if isinstance(row, dict)
    }
    for item in data["loopbacks"]:
        name = f"Loopback{item['id']}"
        if name not in existing_names:
            continue
        existing = device.send_command(f"show running-config interface {name}")
        if f"description {item['description']}" not in existing:
            raise RuntimeError(f"Refusing to take ownership of existing {name}")
    print(device.send_config_set(commands))
print("Configuration sent; it was not saved to startup configuration.")
