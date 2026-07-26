from flask import Flask, render_template, request, jsonify, send_from_directory
import fetcher
import risk_list
import db
import os
import threading
import webbrowser

app = Flask(__name__)
db.init_db()

REACT_BUILD = os.path.join(os.path.dirname(__file__), "frontend", "dist")
FANPAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kyle_crane_fanpage")

@app.route("/")
def index():
    return send_from_directory(REACT_BUILD, "index.html")

@app.route("/<path:path>")
def serve_react(path):
    file_path = os.path.join(REACT_BUILD, path)
    if os.path.isfile(file_path):
        return send_from_directory(REACT_BUILD, path)
    return send_from_directory(REACT_BUILD, "index.html")


@app.route("/kyle_crane_fanpage/")
@app.route("/kyle_crane_fanpage/<path:filename>")
def serve_fanpage(filename="index.html"):
    return send_from_directory(FANPAGE_DIR, filename)


@app.route("/api/track", methods=["POST"])
def track():
    address = request.json.get("address", "").strip()
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
        # Best-effort cache only — never fail the request over it (e.g. on
        # a read-only filesystem or a fresh serverless instance).
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


def _short(addr):
    return addr if len(addr) <= 16 else addr[:8] + "…" + addr[-6:]


def _open_browser(port):
    webbrowser.open(f"http://127.0.0.1:{port}")


if __name__ == "__main__":
    PORT = int(os.environ.get("CRYPTO_TRACKER_PORT", 5000))
    # Auto-open the dashboard in the default browser shortly after the
    # server starts. Skipped when Flask's debug reloader spawns a second
    # process (so the browser doesn't pop open twice), and can be disabled
    # entirely with CRYPTO_TRACKER_NO_BROWSER=true.
    if os.environ.get("CRYPTO_TRACKER_NO_BROWSER", "false").lower() != "true" \
            and os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        threading.Timer(1.5, _open_browser, args=(PORT,)).start()

    app.run(debug=True, port=PORT)
