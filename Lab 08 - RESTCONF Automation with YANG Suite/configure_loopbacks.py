import argparse
from common import item_uri, load_data, render_payload, require, session_and_base

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()
data = load_data()
session, base = session_and_base(data)
for item in data["loopbacks"]:
    url, payload = base + item_uri(data, item["name"]), render_payload(item)
    print("PUT", url)
    if args.apply:
        response = session.put(url, json=payload, timeout=30)
        require(response, {200, 201, 204})
        print(" ", response.status_code)
if not args.apply:
    print(
        "Dry run only. Use --apply after validating the URI and payload in YANG Suite."
    )
