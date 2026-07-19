import json
from pathlib import Path
from common import load_data, render_payload

data = load_data()
target = Path("artifacts/payloads")
target.mkdir(parents=True, exist_ok=True)
for item in data["loopbacks"]:
    payload = render_payload(item)
    (target / f"{item['name']}.json").write_text(json.dumps(payload, indent=2))
    print(item["name"], json.dumps(payload, indent=2))
