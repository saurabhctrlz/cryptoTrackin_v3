"""
api/index.py

Vercel entrypoint for the CryptoTrackin API. Vercel's Python runtime looks
for a Flask instance named `app` inside the /api directory and turns this
whole file (plus its local imports below) into a single Vercel Function,
routed automatically at /api/*.

This is a deliberately slim, API-only sibling of the root app.py, which is
kept around for full local development (it also serves the built React app
and the fanpage easter egg directly with `python app.py`). On Vercel, the
built frontend is instead served as static output by Vercel itself — see
vercel.json — and the fanpage lives under frontend/public/kyle_crane_fanpage
so it's served as a static file too.
"""

from flask import Flask, request, jsonify
import traceback

import fetcher
import risk_list
import db

app = Flask(__name__)
db.init_db()


@app.errorhandler(Exception)
def handle_any_error(e):
    # A serverless function that crashes with no handler can come back as a
    # completely empty response body, which shows up client-side as
    # "Unexpected end of JSON input" — a dead end with zero information.
    # This guarantees the frontend always gets real JSON back, with the
    # actual error message, so failures are debuggable instead of silent.
    return jsonify({
        "error": f"{type(e).__name__}: {e}",
        "trace": traceback.format_exc(),
    }), 500


@app.route("/api/track", methods=["POST"])
def track():
    address = (request.json or {}).get("address", "").strip()
    if not address:
        return jsonify({"error": "Address required"}), 400

    # 🐉 Easter egg — unleash the beast
    if address.lower() == "unleash the beast":
        return jsonify({"easter_egg": True, "fanpage_url": "/kyle_crane_fanpage/index.html"})

    try:
        data = fetcher.fetch_transactions(address)
    except Exception as e:
        return jsonify({"error": f"Failed to fetch data: {str(e)}"}), 502

    risk = risk_list.score_address(address, data["transactions"])
    try:
        db.cache_search(address, data["chain"], data, risk)
    except Exception:
        # Best-effort cache only — never fail the request over it.
        pass

    # Build graph nodes/edges for vis.js
    nodes = {address: {"id": address, "label": _short(address), "group": "root"}}
    edges = []
    for tx in data["transactions"]:
        for sender in tx.get("from", []):
            if sender not in nodes:
                group = "flagged" if sender in risk_list.FLAGGED_ADDRESSES else "normal"
                nodes[sender] = {"id": sender, "label": _short(sender), "group": group}
        for receiver in tx.get("to", []):
            if receiver not in nodes:
                group = "flagged" if receiver in risk_list.FLAGGED_ADDRESSES else "normal"
                nodes[receiver] = {"id": receiver, "label": _short(receiver), "group": group}
        for sender in tx.get("from", []):
            for receiver in tx.get("to", []):
                edges.append({
                    "from": sender,
                    "to": receiver,
                    "label": f"{tx['value_btc']}",
                    "title": tx["hash"],
                })

    return jsonify({
        "data": data,
        "risk": risk,
        "graph": {"nodes": list(nodes.values()), "edges": edges},
    })


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


def _short(addr):
    return addr if len(addr) <= 16 else addr[:8] + "…" + addr[-6:]
