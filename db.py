"""
db.py
Lightweight SQLite cache so we don't hammer the public APIs on every request
and so we keep a local audit trail of what's been searched.
"""

import sqlite3
import json
import os
import time

def _pick_db_path():
    """Use a DB file next to this module if that directory is writable
    (normal local dev), otherwise fall back to /tmp (serverless hosts like
    Vercel, where only /tmp is writable).

    We deliberately test writability directly rather than trusting an env
    var like VERCEL=1 — that variable is opt-in (Project Settings ->
    "Enable access to System Environment Variables") and isn't set by
    default, so relying on it can silently pick the wrong, read-only path
    and crash init_db() at import time, taking down every request.
    """
    local_dir = os.path.dirname(__file__)
    if os.access(local_dir, os.W_OK):
        try:
            probe = os.path.join(local_dir, ".write_test")
            with open(probe, "w") as f:
                f.write("x")
            os.remove(probe)
            return os.path.join(local_dir, "tracker.db")
        except OSError:
            pass
    return "/tmp/tracker.db"


# On serverless hosts, /tmp is the only writable directory, and it is
# wiped between cold starts / not shared across function instances — so
# this cache becomes best-effort/per-invocation there rather than a
# durable local audit trail. That's fine for a demo cache; swap in a real
# hosted DB (Postgres, Turso, etc.) if you need the history to persist.
DB_PATH = _pick_db_path()


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Sets up the searches table. Swallows failures on purpose: this cache
    is a nice-to-have, and a broken DB (e.g. an unexpected read-only path)
    should never prevent the Flask app from starting up at all."""
    try:
        conn = get_conn()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS searches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                address TEXT NOT NULL,
                chain TEXT NOT NULL,
                data_json TEXT NOT NULL,
                risk_json TEXT NOT NULL,
                searched_at INTEGER NOT NULL
            )
        """)
        conn.commit()
        conn.close()
    except Exception:
        pass


def cache_search(address, chain, data, risk):
    conn = get_conn()
    conn.execute(
        "INSERT INTO searches (address, chain, data_json, risk_json, searched_at) VALUES (?, ?, ?, ?, ?)",
        (address, chain, json.dumps(data), json.dumps(risk), int(time.time())),
    )
    conn.commit()
    conn.close()


def recent_searches(limit=10):
    conn = get_conn()
    rows = conn.execute(
        "SELECT address, chain, risk_json, searched_at FROM searches ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    result = []
    for r in rows:
        risk = json.loads(r["risk_json"])
        result.append({
            "address": r["address"],
            "chain": r["chain"],
            "risk_level": risk["level"],
            "searched_at": r["searched_at"],
        })
    return result
