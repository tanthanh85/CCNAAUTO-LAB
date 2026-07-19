from common import item_uri, load_data, require, session_and_base

data = load_data()
session, base = session_and_base(data)
missing = []
for item in data["loopbacks"]:
    response = session.get(base + item_uri(data, item["name"]), timeout=30)
    if response.status_code == 404:
        missing.append(item["name"])
        continue
    require(response, {200})
    print(item["name"], response.json())
print("Missing:", missing)
