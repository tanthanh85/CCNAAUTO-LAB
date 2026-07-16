import json
import os
from pathlib import Path
from urllib.parse import quote

import requests
import yaml
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader, StrictUndefined

ROOT = Path(__file__).parent
HEADERS = {"Accept": "application/yang-data+json", "Content-Type": "application/yang-data+json"}

def load_data():
    data = yaml.safe_load((ROOT / "restconf.yaml").read_text())
    if len(data["loopbacks"]) != 10:
        raise ValueError("Define exactly ten loopbacks")
    return data

def session_and_base(data):
    load_dotenv(ROOT / ".env")
    user, password = os.getenv("LAB_USERNAME"), os.getenv("LAB_PASSWORD")
    if not user or not password:
        raise RuntimeError("Set LAB_USERNAME and LAB_PASSWORD in .env")
    if data["device"]["host"].startswith("REPLACE_"):
        raise RuntimeError("Replace the host in restconf.yaml")
    session = requests.Session(); session.auth = (user, password); session.headers.update(HEADERS)
    ca = os.getenv("LAB_CA_BUNDLE", "").strip()
    session.verify = ca if ca else True
    return session, f"https://{data['device']['host']}:{data['device']['port']}"

def item_uri(data, name):
    return data["restconf"]["interface_item_uri"].format(name=quote(name, safe=""))

def render_payload(loopback):
    env = Environment(loader=FileSystemLoader(ROOT / "payloads"), undefined=StrictUndefined)
    text = env.get_template("interface.json.j2").render(loopback=loopback)
    return json.loads(text)

def require(response, allowed):
    if response.status_code not in allowed:
        raise RuntimeError(f"HTTP {response.status_code} for {response.request.method} {response.url}\n{response.text}")
