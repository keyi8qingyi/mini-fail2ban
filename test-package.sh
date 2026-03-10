#!/bin/bash
# Test the built package

set -e

PACKAGE="mini-fail2ban_1.0.0_all.deb"

echo "================================"
echo "Testing Mini Fail2Ban Package"
echo "================================"
echo ""

# Check if package exists
if [ ! -f "$PACKAGE" ]; then
    echo "[ERROR] Package not found: $PACKAGE"
    echo "Please run: ./build-deb.sh first"
    exit 1
fi

# Show package info
echo "[1/4] Package Information:"
dpkg-deb --info "$PACKAGE"
echo ""

# Show package contents
echo "[2/4] Package Contents:"
dpkg-deb --contents "$PACKAGE"
echo ""

# Check package integrity
echo "[3/4] Checking Package Integrity:"
dpkg-deb --check "$PACKAGE" && echo "✓ Package is valid" || echo "✗ Package has errors"
echo ""

# Show installation instructions
echo "[4/4] Installation Instructions:"
echo ""
echo "To install:"
echo "  sudo dpkg -i $PACKAGE"
echo ""
echo "To remove:"
echo "  sudo dpkg -r mini-fail2ban"
echo ""
echo "To purge (remove with config):"
echo "  sudo dpkg --purge mini-fail2ban"
echo ""
