import os
import sqlite3
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

ROOT = Path(__file__).parent
DB = ROOT / "instance" / "inventory.db"


def connection():
    DB.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with connection() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS routers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            ip TEXT NOT NULL,
            username TEXT NOT NULL,
            password BLOB NOT NULL,
            ssh_port INTEGER NOT NULL DEFAULT 22,
            restconf_port INTEGER NOT NULL DEFAULT 443
        )""")


def cipher():
    key = os.getenv("INVENTORY_ENCRYPTION_KEY", "").encode()
    if not key:
        raise RuntimeError("INVENTORY_ENCRYPTION_KEY is not configured")
    return Fernet(key)


def list_routers():
    with connection() as conn:
        return [dict(row) | {"password": None} for row in conn.execute(
            "SELECT id,name,ip,username,ssh_port,restconf_port,password FROM routers ORDER BY name"
        )]


def get_router(router_id):
    with connection() as conn:
        row = conn.execute("SELECT * FROM routers WHERE id=?", (router_id,)).fetchone()
    if not row:
        raise LookupError("Router not found")
    result = dict(row)
    try:
        result["password"] = cipher().decrypt(result["password"]).decode()
    except InvalidToken as exc:
        raise RuntimeError("Unable to decrypt inventory credential") from exc
    return result


def add_router(item):
    encrypted = cipher().encrypt(item["password"].encode())
    try:
        with connection() as conn:
            cursor = conn.execute(
                "INSERT INTO routers(name,ip,username,password,ssh_port,restconf_port) VALUES(?,?,?,?,?,?)",
                (item["name"], item["ip"], item["username"], encrypted,
                 item["ssh_port"], item.get("restconf_port", 443)),
            )
            return cursor.lastrowid
    except sqlite3.IntegrityError as exc:
        raise ValueError(f"A router named {item['name']!r} already exists") from exc


def delete_router(router_id):
    with connection() as conn:
        conn.execute("DELETE FROM routers WHERE id=?", (router_id,))
