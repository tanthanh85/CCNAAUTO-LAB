import argparse
from common import connect, load_inventory

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()
data = load_inventory()
commands = [f"no interface Loopback{x['id']}" for x in data["loopbacks"]]
print("\n".join(commands))
if not args.apply:
    print("Dry run only. Use --apply to remove the lab interfaces.")
    raise SystemExit
with connect(data) as device:
    parsed = device.send_command("show ip interface brief", use_textfsm=True)
    if not isinstance(parsed, list):
        raise RuntimeError("Cleanup pre-check requires structured TextFSM output")
    existing_names = {
        row.get("intf", row.get("interface")) for row in parsed if isinstance(row, dict)
    }
    for item in data["loopbacks"]:
        name = f"Loopback{item['id']}"
        if name not in existing_names:
            continue
        running = device.send_command(f"show running-config interface {name}")
        if f"description {item['description']}" not in running:
            raise RuntimeError(
                f"Refusing to remove {name}: ownership description differs"
            )
    print(device.send_config_set(commands))
