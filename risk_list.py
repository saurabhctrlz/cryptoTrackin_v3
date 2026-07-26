"""
risk_list.py

A local list of "flagged" addresses used to demonstrate risk-scoring logic.
In a real deployment, this would be built from:
  - OFAC SDN list (sanctioned crypto addresses, published by US Treasury)
  - Public ransomware payment trackers (e.g. ransomwhe.re API)
  - Chainalysis / Elliptic threat intel feeds (commercial)

For this project, we simulate it with a small local list + simple keyword
heuristics so the flagging logic is easy to demo and explain in your report.
"""

FLAGGED_ADDRESSES = {
    "1Suspect111mixerAddrXXXXXXXXXXXXXX": "Known mixing/tumbling service",
    "1RansomwarePayoutXXXXXXXXXXXXXXXX": "Associated with ransomware payout (sample)",
    "0xScamContractAddrXXXXXXXXXXXXXXXXXXXXXX": "Reported phishing/scam contract (sample)",
    "LSuspectMixerAddrXXXXXXXXXXXXXXXX": "Known mixing/tumbling service (Litecoin, sample)",
    "LScamMarketPayoutXXXXXXXXXXXXXXXX": "Associated with dark-market payout (Litecoin, sample)",
}

# Heuristic flags applied to transaction patterns, not just address matches
def score_address(address, transactions):
    """
    Returns a risk assessment dict for a given address based on its
    transaction history. This is intentionally simple / explainable —
    good material for a viva/report walkthrough.
    """
    flags = []
    score = 0

    # 1. Direct match against known flagged addresses
    counterparties = set()
    for tx in transactions:
        counterparties.update(tx.get("from", []))
        counterparties.update(tx.get("to", []))
    counterparties.discard(address)

    for addr in counterparties:
        if addr in FLAGGED_ADDRESSES:
            flags.append(f"Transacted with flagged address {addr}: {FLAGGED_ADDRESSES[addr]}")
            score += 40

    # 2. Rapid fan-out: sending to many distinct addresses in short succession
    outgoing_targets = set()
    for tx in transactions:
        if address in tx.get("from", []):
            outgoing_targets.update(tx.get("to", []))
    if len(outgoing_targets) >= 4:
        flags.append(f"Fan-out pattern: funds sent to {len(outgoing_targets)} distinct addresses")
        score += 15

    # 3. High transaction frequency (placeholder heuristic)
    if len(transactions) >= 10:
        flags.append("High transaction volume for tracked window")
        score += 10

    score = min(score, 100)
    if score >= 60:
        level = "HIGH"
    elif score >= 25:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {"score": score, "level": level, "flags": flags}
