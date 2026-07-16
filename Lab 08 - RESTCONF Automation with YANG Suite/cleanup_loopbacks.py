import argparse
from common import item_uri, load_data, require, session_and_base

parser = argparse.ArgumentParser(); parser.add_argument("--apply", action="store_true"); args = parser.parse_args()
data = load_data(); session, base = session_and_base(data)
for item in data["loopbacks"]:
    url = base + item_uri(data, item["name"]); print("DELETE", url)
    if not args.apply: continue
    current = session.get(url, timeout=30)
    if current.status_code == 404: continue
    require(current, {200})
    if item["description"] not in current.text:
        raise RuntimeError(f"Refusing to remove {item['name']}: ownership description differs")
    response = session.delete(url, timeout=30); require(response, {200, 204}); print(" ", response.status_code)
if not args.apply: print("Dry run only. Use --apply to remove lab-owned interfaces.")
