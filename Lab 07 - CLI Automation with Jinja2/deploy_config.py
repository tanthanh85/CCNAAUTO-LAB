import argparse
from common import connect, load_inventory, render_config

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()
data = load_inventory()
rendered = render_config(data)
commands = [line for line in rendered.splitlines() if line.strip() and line.strip() != "!"]
print(rendered)
if not args.apply:
    print("Dry run only. Use --apply after reviewing every command.")
    raise SystemExit
with connect(data) as device:
    for item in data["loopbacks"]:
        name = f"Loopback{item['id']}"
        existing = device.send_command(f"show running-config interface {name}")
        if existing and "Invalid input" not in existing and item["description"] not in existing:
            raise RuntimeError(f"Refusing to take ownership of existing {name}")
    print(device.send_config_set(commands))
print("Configuration sent; it was not saved to startup configuration.")
