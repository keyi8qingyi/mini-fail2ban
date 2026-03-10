# Mini Fail2Ban - Debian Package Build Guide

## Quick Build

```bash
# Make build script executable
chmod +x build-deb.sh

# Build the package
./build-deb.sh
```

This will create: `mini-fail2ban_1.0.0_all.deb`

## Installation

```bash
# Install the package
sudo dpkg -i mini-fail2ban_1.0.0_all.deb

# If dependencies are missing, fix them
sudo apt-get install -f
```

## Usage After Installation

```bash
# Start service
sudo mini-fail2ban start

# Check status
sudo mini-fail2ban status

# Enable auto-start
sudo mini-fail2ban enable
```

## Removal

```bash
# Remove package (keep config)
sudo dpkg -r mini-fail2ban

# Complete removal (including config)
sudo dpkg --purge mini-fail2ban
```

## Package Information

- **Architecture**: all (works on any architecture)
- **Dependencies**: python3 (>= 3.6), iptables, systemd
- **Size**: ~20KB

## Files Installed

```
/opt/mini-fail2ban/mini_fail2ban_daemon.py
/etc/mini-fail2ban/config.json
/etc/systemd/system/mini-fail2ban.service
/usr/local/bin/mini-fail2ban
/usr/share/doc/mini-fail2ban/README.md
/var/log/mini-fail2ban.log
```
