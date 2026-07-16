import json
from pathlib import Path
from common import connect, load_inventory

data = load_inventory()
with connect(data) as device:
    result = device.send_command("show ip interface brief", use_textfsm=True)
if not isinstance(result, list):
    raise RuntimeError("TextFSM returned raw text; verify textfsm and ntc-templates")
expected = {f"Loopback{x['id']}" for x in data["loopbacks"]}
found = {r.get("intf", r.get("interface")) for r in result}
Path("artifacts").mkdir(exist_ok=True)
Path("artifacts/interfaces.json").write_text(json.dumps(result, indent=2))
print("Present:", sorted(expected & found))
print("Missing:", sorted(expected - found))
