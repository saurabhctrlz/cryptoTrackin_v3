#!/usr/bin/env python3
"""
cli.py — command-line interface for Crypto Tracker.

Lets the tool be used two ways:
  1. As a CLI: cryptotracker -a <address> [--json]
  2. As a web dashboard: cryptotracker --web

Designed to be installed as a system-wide command via setup.py,
the way most Kali tools (sqlmap, nikto, etc.) expose a CLI entry point.
"""

import argparse
import json
import sys
import os

try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init(autoreset=True)
except ImportError:
    class _NoColor:
        def __getattr__(self, name):
            return ""
    Fore = Style = _NoColor()

import fetcher
import risk_list
import db

BANNER_ART = r""" ▄████▄   ██▀███ ▓██   ██▓ ██▓███  ▄▄▄█████▓ ▒█████  ▄▄▄█████▓ ██▀███   ▄▄▄       ▄████▄   ██ ▄█▀ ██▓ ███▄    █ 
▒██▀ ▀█  ▓██ ▒ ██▒▒██  ██▒▓██░  ██▒▓  ██▒ ▓▒▒██▒  ██▒▓  ██▒ ▓▒▓██ ▒ ██▒▒████▄    ▒██▀ ▀█   ██▄█▒ ▓██▒ ██ ▀█   █ 
▒▓█    ▄ ▓██ ░▄█ ▒ ▒██ ██░▓██░ ██▓▒▒ ▓██░ ▒░▒██░  ██▒▒ ▓██░ ▒░▓██ ░▄█ ▒▒██  ▀█▄  ▒▓█    ▄ ▓███▄░ ▒██▒▓██  ▀█ ██▒
▒▓▓▄ ▄██▒▒██▀▀█▄   ░ ▐██▓░▒██▄█▓▒ ▒░ ▓██▓ ░ ▒██   ██░░ ▓██▓ ░ ▒██▀▀█▄  ░██▄▄▄▄██ ▒▓▓▄ ▄██▒▓██ █▄ ░██░▓██▒  ▐▌██▒
▒ ▓███▀ ░░██▓ ▒██▒ ░ ██▒▓░▒██▒ ░  ░  ▒██▒ ░ ░ ████▓▒░  ▒██▒ ░ ░██▓ ▒██▒ ▓█   ▓██▒▒ ▓███▀ ░▒██▒ █▄░██░▒██░   ▓██░
░ ░▒ ▒  ░░ ▒▓ ░▒▓░  ██▒▒▒ ▒▓▒░ ░  ░  ▒ ░░   ░ ▒░▒░▒░   ▒ ░░   ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░░ ░▒ ▒  ░▒ ▒▒ ▓▒░▓  ░ ▒░   ▒ ▒ 
  ░  ▒     ░▒ ░ ▒░▓██ ░▒░ ░▒ ░         ░      ░ ▒ ▒░     ░      ░▒ ░ ▒░  ▒   ▒▒ ░  ░  ▒   ░ ░▒ ▒░ ▒ ░░ ░░   ░ ▒░
░          ░░   ░ ▒ ▒ ░░  ░░         ░      ░ ░ ░ ▒    ░        ░░   ░   ░   ▒   ░        ░ ░░ ░  ▒ ░   ░   ░ ░ 
░ ░         ░     ░ ░                           ░ ░              ░           ░  ░░ ░      ░  ░    ░           ░ 
░                 ░ ░                                                            ░"""

SUBTITLE = "\n     Blockchain Transaction Forensics Tool  |  v1.0\n     Built by ambatron_ctrlz\n"

# True-color ANSI codes so the terminal banner matches the exact brand hex colors
_ANSI_CYAN = "\033[38;2;38;251;255m"   # #26FBFF
_ANSI_RED = "\033[38;2;255;59;59m"     # accent red
_ANSI_RESET = "\033[0m"

# Solid block characters -> main brand color (cyan); shading characters -> red accent
_CYAN_CHARS = set("█▄▀")
_RED_CHARS = set("▓▒░")


def render_banner():
    """Colors the ASCII art two-tone: solid blocks cyan (#26FBFF), shading chars red."""
    out = []
    current = None
    buf = []

    def flush():
        if not buf:
            return
        text = "".join(buf)
        if current == "cyan":
            out.append(_ANSI_CYAN + text + _ANSI_RESET)
        elif current == "red":
            out.append(_ANSI_RED + text + _ANSI_RESET)
        else:
            out.append(text)

    for ch in BANNER_ART:
        cls = "cyan" if ch in _CYAN_CHARS else ("red" if ch in _RED_CHARS else None)
        if cls != current:
            flush()
            buf.clear()
            current = cls
        buf.append(ch)
    flush()
    return "".join(out) + _ANSI_CYAN + SUBTITLE + _ANSI_RESET


def color_level(level):
    return {
        "HIGH": Fore.RED + level + Style.RESET_ALL,
        "MEDIUM": Fore.YELLOW + level + Style.RESET_ALL,
        "LOW": Fore.GREEN + level + Style.RESET_ALL,
    }.get(level, level)


def run_track(address, as_json=False, limit=20):
    try:
        data = fetcher.fetch_transactions(address, limit=limit)
    except Exception as e:
        print(f"{Fore.RED}[!] Failed to fetch data: {e}{Style.RESET_ALL}")
        sys.exit(1)

    risk = risk_list.score_address(address, data["transactions"])
    db.cache_search(address, data["chain"], data, risk)

    if as_json:
        print(json.dumps({"data": data, "risk": risk}, indent=2))
        return

    print(f"\n{Fore.CYAN}Address:{Style.RESET_ALL}   {address}")
    print(f"{Fore.CYAN}Chain:{Style.RESET_ALL}     {data['chain']}")
    print(f"{Fore.CYAN}Tx count:{Style.RESET_ALL}  {data['n_tx']}")
    print(f"{Fore.CYAN}Balance:{Style.RESET_ALL}   {data.get('final_balance_btc', 'n/a')}")
    print(f"\n{Fore.CYAN}Risk Level:{Style.RESET_ALL} {color_level(risk['level'])}  (score {risk['score']}/100)")

    if risk["flags"]:
        print(f"\n{Fore.YELLOW}[!] Flags raised:{Style.RESET_ALL}")
        for f in risk["flags"]:
            print(f"    - {f}")
    else:
        print(f"\n{Fore.GREEN}[+] No risk flags raised.{Style.RESET_ALL}")

    print(f"\n{Fore.CYAN}Recent transactions:{Style.RESET_ALL}")
    for tx in data["transactions"][:10]:
        frm = ", ".join(tx["from"]) or "unknown"
        to = ", ".join(tx["to"]) or "unknown"
        print(f"    [{tx['hash'][:12]}] {frm[:14]}... -> {to[:14]}...  {tx['value_btc']}")
    print()


def run_history(limit):
    rows = db.recent_searches(limit)
    if not rows:
        print(f"{Fore.YELLOW}No search history yet.{Style.RESET_ALL}")
        return
    print(f"\n{Fore.CYAN}{'Address':44}{'Chain':10}{'Risk':8}{'When'}{Style.RESET_ALL}")
    for r in rows:
        import datetime
        ts = datetime.datetime.fromtimestamp(r["searched_at"]).strftime("%Y-%m-%d %H:%M")
        risk_padded = r['risk_level'].ljust(8)  # pad BEFORE adding color codes
        print(f"{r['address']:44}{r['chain']:10}{color_level(risk_padded)}{ts}")
    print()


def run_web(host, port):
    import app as flask_app
    print(f"{Fore.GREEN}[+] Starting web dashboard at http://{host}:{port}{Style.RESET_ALL}")
    flask_app.app.run(host=host, port=port, debug=False)


def main():
    db.init_db()

    parser = argparse.ArgumentParser(
        prog="cryptotrackin",
        description="Trace cryptocurrency wallet transactions and flag risk indicators.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-a", "--address", help="Wallet address to trace (BTC, ETH, or LTC)")
    parser.add_argument("-l", "--limit", type=int, default=20, help="Max transactions to fetch (default: 20)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON instead of formatted text")
    parser.add_argument("--history", action="store_true", help="Show recent search history")
    parser.add_argument("--web", action="store_true", help="Launch the web dashboard instead of CLI mode")
    parser.add_argument("--host", default="127.0.0.1", help="Host for --web mode (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5000, help="Port for --web mode (default: 5000)")
    parser.add_argument("--no-banner", action="store_true", help="Suppress the ASCII banner")

    args = parser.parse_args()

    if not args.no_banner and not args.json:
        print(render_banner())

    if args.web:
        run_web(args.host, args.port)
    elif args.history:
        run_history(args.limit)
    elif args.address:
        if args.address.lower() == "unleash the beast":
            import webbrowser
            import pathlib
            print(f"{Fore.GREEN}[+] Unleashing the beast...{Style.RESET_ALL}")
            page_path = pathlib.Path(__file__).parent / "kyle_crane_fanpage" / "index.html"
            webbrowser.open(page_path.resolve().as_uri())
            return
        run_track(args.address, as_json=args.json, limit=args.limit)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
