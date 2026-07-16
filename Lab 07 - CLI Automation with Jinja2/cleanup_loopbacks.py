import argparse
from common import connect, load_inventory

parser = argparse.ArgumentParser(); parser.add_argument("--apply", action="store_true")
args = parser.parse_args(); data = load_inventory()
commands = [f"no interface Loopback{x['id']}" for x in data["loopbacks"]]
print("\n".join(commands))
if not args.apply:
    print("Dry run only. Use --apply to remove the lab interfaces."); raise SystemExit
with connect(data) as device:
    for item in data["loopbacks"]:
        name = f"Loopback{item['id']}"
        running = device.send_command(f"show running-config interface {name}")
        if running and item["description"] not in running:
            raise RuntimeError(f"Refusing to remove {name}: ownership description differs")
    print(device.send_config_set(commands))
