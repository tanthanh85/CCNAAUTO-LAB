import ipaddress
import os
from collections import defaultdict, deque

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

import database
from restconf import IOSXE, RestconfError, validate_loopback, validate_route

load_dotenv()
app = Flask(__name__, instance_relative_config=True)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY")
if not app.config["SECRET_KEY"]:
    raise RuntimeError("FLASK_SECRET_KEY is not configured")
database.init_db()
samples = defaultdict(lambda: deque(maxlen=120))


def body():
    data = request.get_json(silent=True)
    if not isinstance(data, dict): raise ValueError("A JSON object is required")
    return data


def device(router_id):
    return IOSXE(database.get_router(router_id))


@app.errorhandler(ValueError)
@app.errorhandler(LookupError)
def bad_request(error): return jsonify(error=str(error)), 400


@app.errorhandler(RestconfError)
def upstream(error): return jsonify(error=str(error)), 502


@app.errorhandler(Exception)
def unexpected(error):
    app.logger.exception("Request failed")
    return jsonify(error="The operation failed; review the server log."), 500


@app.get("/")
def index(): return render_template("index.html")


@app.get("/api/routers")
def routers(): return jsonify(database.list_routers())


@app.post("/api/routers")
def router_add():
    item = body()
    for field in ("name", "ip", "username", "password"):
        if not str(item.get(field, "")).strip(): raise ValueError(f"{field} is required")
    ipaddress.ip_address(item["ip"])
    item["ssh_port"] = int(item.get("ssh_port", 22)); item["restconf_port"] = int(item.get("restconf_port", 443))
    if not 1 <= item["ssh_port"] <= 65535 or not 1 <= item["restconf_port"] <= 65535:
        raise ValueError("Port must be between 1 and 65535")
    return jsonify(id=database.add_router(item)), 201


@app.delete("/api/routers/<int:router_id>")
def router_delete(router_id): database.delete_router(router_id); return "", 204


@app.get("/api/routers/<int:router_id>/routes")
def routes(router_id): return jsonify(device(router_id).routes())


@app.post("/api/routers/<int:router_id>/routes/bulk")
def routes_add(router_id):
    entries = body().get("entries", [])
    if not 1 <= len(entries) <= 50: raise ValueError("Submit between 1 and 50 routes")
    for entry in entries: validate_route(entry)
    client = device(router_id)
    for entry in entries: client.put_route(entry)
    return jsonify(processed=len(entries))


@app.delete("/api/routers/<int:router_id>/routes/bulk")
def routes_delete(router_id):
    entries = body().get("entries", [])
    if not 1 <= len(entries) <= 50: raise ValueError("Select between 1 and 50 routes")
    for entry in entries: validate_route(entry)
    client = device(router_id)
    for entry in entries: client.delete_route(entry)
    return jsonify(processed=len(entries))


@app.get("/api/routers/<int:router_id>/loopbacks")
def loopbacks(router_id): return jsonify(device(router_id).loopbacks())


@app.post("/api/routers/<int:router_id>/loopbacks/bulk")
def loopbacks_add(router_id):
    entries = body().get("entries", [])
    if not 1 <= len(entries) <= 50: raise ValueError("Submit between 1 and 50 loopbacks")
    for entry in entries: validate_loopback(entry)
    client = device(router_id)
    for entry in entries: client.put_loopback(entry)
    return jsonify(processed=len(entries))


@app.delete("/api/routers/<int:router_id>/loopbacks/bulk")
def loopbacks_delete(router_id):
    entries = body().get("entries", [])
    if not 1 <= len(entries) <= 50: raise ValueError("Select between 1 and 50 loopbacks")
    for entry in entries: validate_loopback(entry)
    client = device(router_id)
    for entry in entries: client.delete_loopback(entry)
    return jsonify(processed=len(entries))


@app.get("/api/routers/<int:router_id>/utilization")
def utilization(router_id):
    current = device(router_id).counters(); history = samples[router_id]
    result = {"timestamp": current["time"], "input_bps": 0, "output_bps": 0,
              "input_percent": 0, "output_percent": 0}
    if history:
        previous = history[-1]; elapsed = current["time"] - previous["time"]
        if elapsed > 0:
            in_bps = max(0, current["in_octets"] - previous["in_octets"]) * 8 / elapsed
            out_bps = max(0, current["out_octets"] - previous["out_octets"]) * 8 / elapsed
            result |= {"input_bps": round(in_bps), "output_bps": round(out_bps),
                       "input_percent": round(in_bps/current["speed_bps"]*100, 3),
                       "output_percent": round(out_bps/current["speed_bps"]*100, 3)}
    history.append(current)
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
