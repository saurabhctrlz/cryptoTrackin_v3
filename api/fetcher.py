"""
fetcher.py
Pulls transaction data for a wallet address from public blockchain APIs.

Bitcoin  -> blockchain.info (no API key needed)
Ethereum -> Etherscan (free API key, get one at https://etherscan.io/apis)
Litecoin -> BlockCypher (no API key needed for reasonable request volumes)

"""

import requests
import json
import os
import time
ETHERSCAN_API_KEY = os.environ.get("ETHERSCAN_API_KEY", "")


def _safe_list(value):
    """Returns value if it's a list, otherwise an empty list. Guards against
    APIs that return an explicit `null` for a field instead of omitting it
    (a plain `.get(key, [])` default only kicks in when the key is missing
    entirely, not when it's present but null)."""
    return value if isinstance(value, list) else []


def _safe_dict(value):
    """Same idea as _safe_list, but for dict-shaped fields."""
    return value if isinstance(value, dict) else {}


def detect_chain(address):
    """Rough heuristic based on address prefix/format:
    - 0x + 42 chars           -> Ethereum
    - starts with L or M, or ltc1 -> Litecoin
    - everything else         -> Bitcoin (default)

    Note: legacy Litecoin addresses starting with '3' are indistinguishable
    from Bitcoin P2SH addresses by prefix alone, so those will be treated
    as Bitcoin here. Modern Litecoin P2SH addresses use 'M' instead of '3'
    specifically to avoid this collision, and are detected correctly.
    """
    if address.startswith("0x") and len(address) == 42:
        return "ethereum"
    if address.startswith("ltc1") or address.startswith("L") or address.startswith("M"):
        return "litecoin"
    return "bitcoin"


def fetch_bitcoin_transactions(address, limit=20):
    """Fetch transactions for a BTC address via blockchain.info."""
    url = f"https://blockchain.info/rawaddr/{address}?limit={limit}"
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    raw = resp.json()

    if not isinstance(raw, dict):
        raise ValueError(f"Unexpected response from blockchain.info for '{address}' — is this a valid Bitcoin address?")

    txs = []
    for tx in _safe_list(raw.get("txs")):
        tx = _safe_dict(tx)
        inputs = _safe_list(tx.get("inputs"))
        outs = _safe_list(tx.get("out"))
        total_out = sum(_safe_dict(o).get("value", 0) or 0 for o in outs)
        senders = list({
            _safe_dict(_safe_dict(i).get("prev_out")).get("addr")
            for i in inputs
            if _safe_dict(_safe_dict(i).get("prev_out")).get("addr")
        })
        receivers = list({
            _safe_dict(o).get("addr") for o in outs if _safe_dict(o).get("addr")
        })
        txs.append({
            "hash": tx.get("hash"),
            "time": tx.get("time"),
            "from": senders,
            "to": receivers,
            "value_btc": round(total_out / 1e8, 8),
        })
    return {
        "address": address,
        "final_balance_btc": round((raw.get("final_balance") or 0) / 1e8, 8),
        "n_tx": raw.get("n_tx", 0),
        "transactions": txs,
    }


def fetch_litecoin_transactions(address, limit=20):
    """Fetch transactions for an LTC address via BlockCypher (no API key
    needed for reasonable request volumes)."""
    url = f"https://api.blockcypher.com/v1/ltc/main/addrs/{address}/full?limit={limit}"
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    raw = resp.json()

    if not isinstance(raw, dict):
        raise ValueError(f"Unexpected response from BlockCypher for '{address}' — is this a valid Litecoin address?")
    if "error" in raw:
        raise ValueError(f"BlockCypher error for '{address}': {raw['error']}")

    txs = []
    for tx in _safe_list(raw.get("txs")):
        tx = _safe_dict(tx)
        inputs = _safe_list(tx.get("inputs"))
        outputs = _safe_list(tx.get("outputs"))
        total_out = sum(_safe_dict(o).get("value", 0) or 0 for o in outputs)
        senders = list({
            addr
            for i in inputs
            for addr in _safe_list(_safe_dict(i).get("addresses"))
        })
        receivers = list({
            addr
            for o in outputs
            for addr in _safe_list(_safe_dict(o).get("addresses"))
        })
        txs.append({
            "hash": tx.get("hash"),
            "time": tx.get("confirmed") or tx.get("received"),
            "from": senders,
            "to": receivers,
            "value_btc": round(total_out / 1e8, 8),  # LTC also uses 8 decimals
        })
    return {
        "address": address,
        "final_balance_btc": round((raw.get("balance") or 0) / 1e8, 8),
        "n_tx": raw.get("n_tx", 0),
        "transactions": txs,
    }


def fetch_ethereum_transactions(address, limit=20):
    """Fetch transactions for an ETH address via Etherscan.

    Uses API V2 (https://api.etherscan.io/v2/api) with chainid=1 for
    Ethereum mainnet. Etherscan fully retired the old V1 endpoint
    (https://api.etherscan.io/api) on August 15, 2025 — any request to it
    now just returns {"status":"0","message":"NOTOK","result":"You are
    using a deprecated V1 endpoint..."} instead of real data.
    """
    if not ETHERSCAN_API_KEY:
        raise ValueError(
            "No Etherscan API key configured. Set the ETHERSCAN_API_KEY "
            "environment variable (get a free key at https://etherscan.io/apis)."
        )

    url = (
        "https://api.etherscan.io/v2/api"
        "?chainid=1"
        f"&module=account&action=txlist&address={address}"
        f"&startblock=0&endblock=99999999&page=1&offset={limit}"
        f"&sort=desc&apikey={ETHERSCAN_API_KEY}"
    )
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    raw = resp.json()

    if not isinstance(raw, dict):
        raise ValueError(f"Unexpected response from Etherscan for '{address}' — is this a valid Ethereum address?")

    result = raw.get("result")
    # Etherscan returns status "0" with `result` as an error *string* (not a
    # list) for bad addresses, rate limits, or invalid API keys — iterating
    # over that string directly is what caused the earlier crash.
    if raw.get("status") == "0" or not isinstance(result, list):
        message = raw.get("message", "Unknown error")
        detail = result if isinstance(result, str) else message
        raise ValueError(f"Etherscan error for '{address}': {message} — {detail}")

    txs = []
    for tx in result:
        tx = _safe_dict(tx)
        txs.append({
            "hash": tx.get("hash"),
            "time": int(tx.get("timeStamp", 0) or 0),
            "from": [tx.get("from")],
            "to": [tx.get("to")],
            "value_btc": round(int(tx.get("value", 0) or 0) / 1e18, 8),  # actually ETH
        })
    return {
        "address": address,
        "final_balance_btc": None,  # would need a separate balance call
        "n_tx": len(txs),
        "transactions": txs,
    }


def fetch_transactions(address, limit=20):
    address = address.strip()

    # Catch a common typo: some keyboards/autocorrect turn "0x" into "0×"
    # (U+00D7 MULTIPLICATION SIGN) which looks identical but isn't the
    # letter x, so it silently fails Ethereum-address detection and gets
    # misrouted to Bitcoin instead, producing a confusing downstream error.
    if "\u00d7" in address:
        raise ValueError(
            f"'{address}' contains a '×' (multiplication sign) instead of "
            "the letter 'x' — this is usually an autocorrect/typo issue. "
            "Double-check the address and retype the 'x' manually."
        )

    chain = detect_chain(address)
    if chain == "ethereum":
        data = fetch_ethereum_transactions(address, limit)
    elif chain == "litecoin":
        data = fetch_litecoin_transactions(address, limit)
    else:
        data = fetch_bitcoin_transactions(address, limit)
    data["chain"] = chain
    return data
