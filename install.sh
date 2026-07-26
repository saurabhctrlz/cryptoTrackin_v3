#!/bin/bash
# install.sh — installs CryptoTrackin as a system-wide Kali command: `cryptotrackin`
set -e

echo "[*] Installing CryptoTrackin..."

if ! command -v pip3 &> /dev/null; then
    echo "[!] pip3 not found. Install with: sudo apt install python3-pip"
    exit 1
fi

pip3 install -e . --break-system-packages

if command -v mandb &> /dev/null; then
    echo "[*] Installing man page..."
    sudo mkdir -p /usr/local/share/man/man1
    sudo cp cryptotrackin.1 /usr/local/share/man/man1/
    sudo mandb -q 2>/dev/null || true
    echo "[+] Man page installed. Try: man cryptotrackin"
fi

echo ""
echo "[+] Installed. Try it now:"
echo "    cryptotrackin -a 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
echo "    cryptotrackin --web"
echo "    cryptotrackin --help"
