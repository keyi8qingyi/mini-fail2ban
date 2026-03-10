#!/bin/bash
# Mini Fail2Ban Installation Script

set -e

echo "================================"
echo "Mini Fail2Ban Installation"
echo "================================"
echo ""

# Check root permission
if [ "$EUID" -ne 0 ]; then 
    echo "[ERROR] Root permission required"
    echo "Usage: sudo bash install.sh"
    exit 1
fi

# Installation directories
INSTALL_DIR="/opt/mini-fail2ban"
CONFIG_DIR="/etc/mini-fail2ban"
LOG_DIR="/var/log"

echo "[1/6] Creating installation directories..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$CONFIG_DIR"

echo "[2/6] Copying program files..."
cp mini_fail2ban_daemon.py "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/mini_fail2ban_daemon.py"

echo "[3/6] Creating configuration file..."
if [ ! -f "$CONFIG_DIR/config.json" ]; then
    cp config.json "$CONFIG_DIR/"
    echo "  Configuration file created: $CONFIG_DIR/config.json"
else
    echo "  Configuration file already exists, skipping"
fi

echo "[4/6] Installing systemd service..."
cp mini-fail2ban.service /etc/systemd/system/
systemctl daemon-reload

echo "[5/6] Creating management command..."
cat > /usr/local/bin/mini-fail2ban << 'EOF'
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

chmod +x /usr/local/bin/mini-fail2ban

echo "[6/6] Installation completed"
echo ""
echo "================================"
echo "Installation Successful!"
echo "================================"
echo ""
echo "Configuration file: $CONFIG_DIR/config.json"
echo "Log file: $LOG_DIR/mini-fail2ban.log"
echo ""
echo "Quick Start:"
echo "  1. Edit config:  mini-fail2ban config"
echo "  2. Start service: mini-fail2ban start"
echo "  3. Check status:  mini-fail2ban status"
echo "  4. View logs:     mini-fail2ban logs"
echo "  5. Enable auto-start: mini-fail2ban enable"
echo ""
echo "For more help: mini-fail2ban"
echo ""
