#!/bin/bash
# Build Debian package for Mini Fail2Ban

set -e

# Package information
PACKAGE_NAME="mini-fail2ban"
VERSION="1.0.0"
ARCH="all"  # Architecture-independent (Python script)
MAINTAINER="Your Name <your.email@example.com>"

# Build directory
BUILD_DIR="build/${PACKAGE_NAME}_${VERSION}_${ARCH}"

echo "================================"
echo "Building Mini Fail2Ban DEB Package"
echo "================================"
echo ""
echo "Package: ${PACKAGE_NAME}"
echo "Version: ${VERSION}"
echo "Architecture: ${ARCH}"
echo ""

# Clean previous build
echo "[1/7] Cleaning previous build..."
rm -rf build
mkdir -p "$BUILD_DIR"

# Create directory structure
echo "[2/7] Creating directory structure..."
mkdir -p "$BUILD_DIR/DEBIAN"
mkdir -p "$BUILD_DIR/opt/mini-fail2ban"
mkdir -p "$BUILD_DIR/etc/mini-fail2ban"
mkdir -p "$BUILD_DIR/etc/systemd/system"
mkdir -p "$BUILD_DIR/usr/local/bin"
mkdir -p "$BUILD_DIR/usr/share/doc/mini-fail2ban"

# Copy program files
echo "[3/7] Copying program files..."
cp mini_fail2ban_daemon.py "$BUILD_DIR/opt/mini-fail2ban/"
chmod 755 "$BUILD_DIR/opt/mini-fail2ban/mini_fail2ban_daemon.py"

# Copy configuration file
cp config.json "$BUILD_DIR/etc/mini-fail2ban/config.json"

# Copy systemd service file
cp mini-fail2ban.service "$BUILD_DIR/etc/systemd/system/"

# Copy documentation
cp DAEMON_README.md "$BUILD_DIR/usr/share/doc/mini-fail2ban/README.md"

# Create management script
echo "[4/7] Creating management script..."
cat > "$BUILD_DIR/usr/local/bin/mini-fail2ban" << 'EOF'
#!/bin/bash
# Mini Fail2Ban Management Command

case "$1" in
    start)
        systemctl start mini-fail2ban
        ;;
    stop)
        systemctl stop mini-fail2ban
        ;;
    restart)
        systemctl restart mini-fail2ban
        ;;
    reload)
        systemctl reload mini-fail2ban
        ;;
    status)
        systemctl status mini-fail2ban
        ;;
    enable)
        systemctl enable mini-fail2ban
        ;;
    disable)
        systemctl disable mini-fail2ban
        ;;
    logs)
        tail -f /var/log/mini-fail2ban.log
        ;;
    config)
        ${EDITOR:-nano} /etc/mini-fail2ban/config.json
        ;;
    banned)
        iptables -L INPUT -n -v | grep DROP
        ;;
    unban)
        if [ -z "$2" ]; then
            echo "Usage: mini-fail2ban unban <IP_ADDRESS>"
            exit 1
        fi
        iptables -D INPUT -s "$2" -j DROP
        echo "Unbanned: $2"
        ;;
    *)
        echo "Mini Fail2Ban Management Tool"
        echo ""
        echo "Usage: mini-fail2ban <command> [args]"
        echo ""
        echo "Commands:"
        echo "  start      Start service"
        echo "  stop       Stop service"
        echo "  restart    Restart service"
        echo "  reload     Reload configuration"
        echo "  status     Show status"
        echo "  enable     Enable auto-start"
        echo "  disable    Disable auto-start"
        echo "  logs       View logs"
        echo "  config     Edit configuration"
        echo "  banned     Show banned IPs"
        echo "  unban <IP> Unban specific IP"
        echo ""
        exit 1
        ;;
esac
EOF

chmod 755 "$BUILD_DIR/usr/local/bin/mini-fail2ban"

# Create control file
echo "[5/7] Creating control file..."
cat > "$BUILD_DIR/DEBIAN/control" << EOF
Package: ${PACKAGE_NAME}
Version: ${VERSION}
Section: admin
Priority: optional
Architecture: ${ARCH}
Depends: python3 (>= 3.6), iptables, systemd
Maintainer: ${MAINTAINER}
Description: Lightweight SSH login protection daemon
 Mini Fail2Ban is a lightweight daemon that monitors SSH login failures
 and automatically bans malicious IP addresses using iptables.
 .
 Features:
  - Real-time log monitoring
  - Automatic IP banning/unbanning
  - Hot-reload configuration
  - Systemd integration
  - Whitelist support (CIDR format)
Homepage: https://github.com/yourusername/mini-fail2ban
EOF

# Create postinst script (after installation)
echo "[6/7] Creating post-installation script..."
cat > "$BUILD_DIR/DEBIAN/postinst" << 'EOF'
#!/bin/bash
# Post-installation script

set -e

# Reload systemd daemon
systemctl daemon-reload

# Create log file if not exists
touch /var/log/mini-fail2ban.log
chmod 640 /var/log/mini-fail2ban.log

echo ""
echo "================================"
echo "Mini Fail2Ban installed successfully!"
echo "================================"
echo ""
echo "Configuration file: /etc/mini-fail2ban/config.json"
echo "Log file: /var/log/mini-fail2ban.log"
echo ""
echo "Quick Start:"
echo "  1. Edit config:  sudo mini-fail2ban config"
echo "  2. Start service: sudo mini-fail2ban start"
echo "  3. Check status:  sudo mini-fail2ban status"
echo "  4. Enable auto-start: sudo mini-fail2ban enable"
echo ""
echo "For more help: mini-fail2ban"
echo ""

exit 0
EOF

chmod 755 "$BUILD_DIR/DEBIAN/postinst"

# Create prerm script (before removal)
cat > "$BUILD_DIR/DEBIAN/prerm" << 'EOF'
#!/bin/bash
# Pre-removal script

set -e

# Stop service if running
if systemctl is-active --quiet mini-fail2ban; then
    echo "Stopping Mini Fail2Ban service..."
    systemctl stop mini-fail2ban
fi

# Disable service if enabled
if systemctl is-enabled --quiet mini-fail2ban 2>/dev/null; then
    echo "Disabling Mini Fail2Ban service..."
    systemctl disable mini-fail2ban
fi

exit 0
EOF

chmod 755 "$BUILD_DIR/DEBIAN/prerm"

# Create postrm script (after removal)
cat > "$BUILD_DIR/DEBIAN/postrm" << 'EOF'
#!/bin/bash
# Post-removal script

set -e

# Reload systemd daemon
systemctl daemon-reload

# Remove log file on purge
if [ "$1" = "purge" ]; then
    rm -f /var/log/mini-fail2ban.log
    echo "Mini Fail2Ban has been completely removed."
fi

exit 0
EOF

chmod 755 "$BUILD_DIR/DEBIAN/postrm"

# Build the package
echo "[7/7] Building DEB package..."
dpkg-deb --build "$BUILD_DIR"

# Move to current directory
mv "build/${PACKAGE_NAME}_${VERSION}_${ARCH}.deb" .

echo ""
echo "================================"
echo "Build Successful!"
echo "================================"
echo ""
echo "Package: ${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"
echo ""
echo "Installation:"
echo "  sudo dpkg -i ${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"
echo ""
echo "Removal:"
echo "  sudo dpkg -r ${PACKAGE_NAME}"
echo ""
echo "Complete removal (including config):"
echo "  sudo dpkg --purge ${PACKAGE_NAME}"
echo ""
