#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mini Fail2Ban - Daemon Version
Supports background running, hot-reload configuration, and process management
"""

import re
import time
import subprocess
import sys
import os
import signal
import json
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path


class MiniFail2BanDaemon:
    def __init__(self, config_file="/etc/mini-fail2ban/config.json"):
        """
        Initialize the daemon process
        
        Args:
            config_file (str): Path to configuration file
        """
        self.config_file = config_file
        self.config = {}
        self.config_mtime = 0
        
        # Runtime state
        self.running = True
        self.pid_file = "/var/run/mini-fail2ban.pid"
        
        # Store failure records: {ip: [timestamp1, timestamp2, ...]}
        self.failures = defaultdict(list)
        
        # Store banned IPs: {ip: ban_timestamp}
        self.banned_ips = {}
        
        # Regular expressions for SSH login failures
        self.fail_patterns = [
            re.compile(r'Failed password for .+ from (\d+\.\d+\.\d+\.\d+)'),
            re.compile(r'Failed password for invalid user .+ from (\d+\.\d+\.\d+\.\d+)'),
            re.compile(r'Invalid user .+ from (\d+\.\d+\.\d+\.\d+)'),
            re.compile(r'Connection closed by authenticating user .+ (\d+\.\d+\.\d+\.\d+)'),
            re.compile(r'Disconnected from authenticating user .+ (\d+\.\d+\.\d+\.\d+)'),
            re.compile(r'authentication failure.*rhost=(\d+\.\d+\.\d+\.\d+)'),
        ]
        
        # Load configuration
        self.load_config()
        
        # Setup signal handlers
        signal.signal(signal.SIGHUP, self.handle_reload)
        signal.signal(signal.SIGTERM, self.handle_stop)
        signal.signal(signal.SIGINT, self.handle_stop)
        
        self.log(f"Mini Fail2Ban daemon started")
        self.log(f"Config file: {self.config_file}")
        self.log(f"PID file: {self.pid_file}")
    
    def log(self, message, level="INFO"):
        """
        Write log message to console and log file
        
        Args:
            message (str): Log message
            level (str): Log level (INFO, WARN, ERROR)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] [{level}] {message}"
        
        # Output to console
        print(log_msg)
        
        # Output to log file
        log_file = self.config.get('log_file', '/var/log/mini-fail2ban.log')
        try:
            with open(log_file, 'a') as f:
                f.write(log_msg + '\n')
        except:
            pass
    
    def load_config(self):
        """
        Load configuration from JSON file
        Creates default config if file doesn't exist
        """
        try:
            # Check if config file exists
            if not os.path.exists(self.config_file):
                self.log(f"Config file not found, creating default: {self.config_file}", "WARN")
                self.create_default_config()
            
            # Read configuration
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
            
            # Record config file modification time
            self.config_mtime = os.path.getmtime(self.config_file)
            
            self.log(f"Configuration loaded successfully")
            self.log(f"  Log path: {self.config.get('log_path', '/var/log/auth.log')}")
            self.log(f"  Max retry: {self.config.get('max_retry', 3)} times")
            self.log(f"  Ban time: {self.config.get('ban_time', 300)} seconds")
            self.log(f"  Find time: {self.config.get('find_time', 600)} seconds")
            
        except json.JSONDecodeError as e:
            self.log(f"Invalid JSON format in config file: {e}", "ERROR")
            sys.exit(1)
        except Exception as e:
            self.log(f"Failed to load configuration: {e}", "ERROR")
            sys.exit(1)
    
    def create_default_config(self):
        """
        Create default configuration file with sensible defaults
        """
        default_config = {
            "log_path": "/var/log/auth.log",
            "log_file": "/var/log/mini-fail2ban.log",
            "max_retry": 3,
            "ban_time": 300,
            "find_time": 600,
            "whitelist": [
                "127.0.0.1",
                "::1",
                "192.168.0.0/16",
                "10.0.0.0/8"
            ],
            "enabled": True
        }
        
        # Create config directory
        config_dir = os.path.dirname(self.config_file)
        os.makedirs(config_dir, exist_ok=True)
        
        # Write default configuration
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        self.log(f"Default configuration created: {self.config_file}")
    
    def check_config_reload(self):
        """
        Check if config file has been modified and reload if necessary
        
        Returns:
            bool: True if config was reloaded, False otherwise
        """
        try:
            current_mtime = os.path.getmtime(self.config_file)
            if current_mtime > self.config_mtime:
                self.log("Config file changed, reloading configuration", "INFO")
                self.load_config()
                return True
        except:
            pass
        return False
    
    def handle_reload(self, signum, frame):
        """
        Handle SIGHUP signal - reload configuration
        
        Args:
            signum: Signal number
            frame: Current stack frame
        """
        self.log("Received SIGHUP signal, reloading configuration", "INFO")
        self.load_config()
    
    def handle_stop(self, signum, frame):
        """
        Handle SIGTERM/SIGINT signal - stop service
        
        Args:
            signum: Signal number
            frame: Current stack frame
        """
        self.log("Received stop signal, shutting down...", "INFO")
        self.running = False
    
    def is_ip_whitelisted(self, ip):
        """
        Check if IP address is in whitelist
        
        Args:
            ip (str): IP address to check
            
        Returns:
            bool: True if IP is whitelisted, False otherwise
        """
        whitelist = self.config.get('whitelist', [])
        
        for white_ip in whitelist:
            if '/' in white_ip:
                # CIDR format
                if self.ip_in_network(ip, white_ip):
                    return True
            else:
                # Exact match
                if ip == white_ip:
                    return True
        
        return False
    
    def ip_in_network(self, ip, network):
        """
        Check if IP address is within CIDR network range
        
        Args:
            ip (str): IP address to check
            network (str): CIDR network (e.g., "192.168.0.0/16")
            
        Returns:
            bool: True if IP is in network, False otherwise
        """
        try:
            import ipaddress
            return ipaddress.ip_address(ip) in ipaddress.ip_network(network, strict=False)
        except:
            return False
    
    def parse_log_line(self, line):
        """
        Parse log line and extract failed login IP address
        
        Args:
            line (str): Log line to parse
            
        Returns:
            str: IP address if found, None otherwise
        """
        for pattern in self.fail_patterns:
            match = pattern.search(line)
            if match:
                return match.group(1)
        return None
    
    def ban_ip(self, ip):
        """
        Ban IP address using iptables
        
        Args:
            ip (str): IP address to ban
        """
        if ip in self.banned_ips:
            return
        
        try:
            # Add iptables rule
            cmd = ['iptables', '-I', 'INPUT', '-s', ip, '-j', 'DROP']
            subprocess.run(cmd, check=True, capture_output=True)
            
            self.banned_ips[ip] = time.time()
            ban_time = self.config.get('ban_time', 300)
            ban_until = datetime.now() + timedelta(seconds=ban_time)
            
            self.log(f"Banned IP: {ip} (for {ban_time}s, until {ban_until.strftime('%H:%M:%S')})", "WARN")
            
        except subprocess.CalledProcessError as e:
            self.log(f"Failed to ban {ip}: {e}", "ERROR")
        except PermissionError:
            self.log(f"Root permission required to execute iptables", "ERROR")
    
    def unban_ip(self, ip):
        """
        Unban IP address by removing iptables rule
        
        Args:
            ip (str): IP address to unban
        """
        try:
            cmd = ['iptables', '-D', 'INPUT', '-s', ip, '-j', 'DROP']
            subprocess.run(cmd, check=True, capture_output=True)
            
            del self.banned_ips[ip]
            self.log(f"Unbanned IP: {ip}", "INFO")
            
        except subprocess.CalledProcessError:
            if ip in self.banned_ips:
                del self.banned_ips[ip]
    
    def check_and_ban(self, ip):
        """
        Check IP failure count and ban if threshold exceeded
        
        Args:
            ip (str): IP address to check
        """
        current_time = time.time()
        find_time = self.config.get('find_time', 600)
        max_retry = self.config.get('max_retry', 3)
        
        # Clean up expired failure records
        cutoff_time = current_time - find_time
        self.failures[ip] = [t for t in self.failures[ip] if t > cutoff_time]
        
        # Check failure count
        if len(self.failures[ip]) >= max_retry:
            self.ban_ip(ip)
            self.failures[ip] = []
    
    def check_unban(self):
        """
        Check and unban expired IPs
        """
        current_time = time.time()
        ban_time = self.config.get('ban_time', 300)
        to_unban = []
        
        for ip, ban_timestamp in self.banned_ips.items():
            if current_time - ban_timestamp >= ban_time:
                to_unban.append(ip)
        
        for ip in to_unban:
            self.unban_ip(ip)
    
    def process_line(self, line):
        """
        Process single log line
        
        Args:
            line (str): Log line to process
        """
        # Check if protection is enabled
        if not self.config.get('enabled', True):
            return
        
        ip = self.parse_log_line(line)
        
        if ip and not self.is_ip_whitelisted(ip):
            current_time = time.time()
            self.failures[ip].append(current_time)
            
            find_time = self.config.get('find_time', 600)
            max_retry = self.config.get('max_retry', 3)
            
            fail_count = len([t for t in self.failures[ip] 
                            if t > current_time - find_time])
            
            self.log(f"Failed login detected: {ip} ({fail_count}/{max_retry})", "INFO")
            
            self.check_and_ban(ip)
    
    def write_pid(self):
        """
        Write process ID to PID file
        """
        try:
            pid_dir = os.path.dirname(self.pid_file)
            os.makedirs(pid_dir, exist_ok=True)
            
            with open(self.pid_file, 'w') as f:
                f.write(str(os.getpid()))
            
            self.log(f"PID file created: {self.pid_file}")
        except Exception as e:
            self.log(f"Failed to create PID file: {e}", "ERROR")
    
    def remove_pid(self):
        """
        Remove PID file
        """
        try:
            if os.path.exists(self.pid_file):
                os.remove(self.pid_file)
                self.log(f"PID file removed")
        except Exception as e:
            self.log(f"Failed to remove PID file: {e}", "ERROR")
    
    def run(self):
        """
        Main loop - monitor log file for SSH failures
        """
        self.write_pid()
        
        log_path = self.config.get('log_path', '/var/log/auth.log')
        
        try:
            with open(log_path, 'r') as f:
                # Move to end of file
                f.seek(0, 2)
                
                self.log(f"Started monitoring log: {log_path}")
                
                check_count = 0
                
                while self.running:
                    line = f.readline()
                    
                    if line:
                        self.process_line(line.strip())
                    else:
                        # No new lines, wait
                        time.sleep(0.5)
                        
                        # Periodic checks
                        check_count += 1
                        if check_count >= 10:  # Check every 5 seconds
                            self.check_unban()
                            self.check_config_reload()
                            check_count = 0
                        
        except FileNotFoundError:
            self.log(f"Log file not found: {log_path}", "ERROR")
            sys.exit(1)
        except Exception as e:
            self.log(f"Runtime error: {e}", "ERROR")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """
        Cleanup resources and unban all IPs
        """
        self.log("Cleaning up resources...")
        
        # Unban all IPs
        for ip in list(self.banned_ips.keys()):
            self.unban_ip(ip)
        
        # Remove PID file
        self.remove_pid()
        
        self.log("Mini Fail2Ban stopped")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Mini Fail2Ban Daemon',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start daemon
  sudo python3 mini_fail2ban_daemon.py start
  
  # Stop daemon
  sudo python3 mini_fail2ban_daemon.py stop
  
  # Restart daemon
  sudo python3 mini_fail2ban_daemon.py restart
  
  # Reload configuration
  sudo python3 mini_fail2ban_daemon.py reload
  
  # Check status
  sudo python3 mini_fail2ban_daemon.py status
        """
    )
    
    parser.add_argument('action', choices=['start', 'stop', 'restart', 'reload', 'status'],
                       help='Action: start|stop|restart|reload|status')
    parser.add_argument('-c', '--config', default='/etc/mini-fail2ban/config.json',
                       help='Configuration file path (default: /etc/mini-fail2ban/config.json)')
    
    args = parser.parse_args()
    
    # Check root permission
    if os.geteuid() != 0:
        print("[ERROR] Root permission required")
        print("Please use: sudo python3 mini_fail2ban_daemon.py")
        sys.exit(1)
    
    pid_file = "/var/run/mini-fail2ban.pid"
    
    if args.action == 'start':
        # Check if already running
        if os.path.exists(pid_file):
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            try:
                os.kill(pid, 0)
                print(f"[ERROR] Mini Fail2Ban is already running (PID: {pid})")
                sys.exit(1)
            except OSError:
                # Process doesn't exist, remove old PID file
                os.remove(pid_file)
        
        # Start daemon
        daemon = MiniFail2BanDaemon(config_file=args.config)
        daemon.run()
    
    elif args.action == 'stop':
        if not os.path.exists(pid_file):
            print("[ERROR] Mini Fail2Ban is not running")
            sys.exit(1)
        
        with open(pid_file, 'r') as f:
            pid = int(f.read().strip())
        
        try:
            print(f"Stopping Mini Fail2Ban (PID: {pid})...")
            os.kill(pid, signal.SIGTERM)
            
            # Wait for process to terminate
            for _ in range(10):
                try:
                    os.kill(pid, 0)
                    time.sleep(0.5)
                except OSError:
                    break
            
            print("Mini Fail2Ban stopped")
        except OSError:
            print("[ERROR] Process not found")
            if os.path.exists(pid_file):
                os.remove(pid_file)
    
    elif args.action == 'restart':
        # Stop first
        if os.path.exists(pid_file):
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            try:
                print(f"Stopping Mini Fail2Ban (PID: {pid})...")
                os.kill(pid, signal.SIGTERM)
                time.sleep(2)
            except OSError:
                pass
        
        # Then start
        print("Starting Mini Fail2Ban...")
        daemon = MiniFail2BanDaemon(config_file=args.config)
        daemon.run()
    
    elif args.action == 'reload':
        if not os.path.exists(pid_file):
            print("[ERROR] Mini Fail2Ban is not running")
            sys.exit(1)
        
        with open(pid_file, 'r') as f:
            pid = int(f.read().strip())
        
        try:
            print(f"Reloading configuration (PID: {pid})...")
            os.kill(pid, signal.SIGHUP)
            print("Configuration reloaded")
        except OSError:
            print("[ERROR] Process not found")
    
    elif args.action == 'status':
        if not os.path.exists(pid_file):
            print("Status: Not running")
            sys.exit(1)
        
        with open(pid_file, 'r') as f:
            pid = int(f.read().strip())
        
        try:
            os.kill(pid, 0)
            print(f"Status: Running (PID: {pid})")
            
            # Display configuration info
            if os.path.exists(args.config):
                with open(args.config, 'r') as f:
                    config = json.load(f)
                print(f"\nConfiguration file: {args.config}")
                print(f"  Log path: {config.get('log_path')}")
                print(f"  Max retry: {config.get('max_retry')} times")
                print(f"  Ban time: {config.get('ban_time')} seconds")
                print(f"  Find time: {config.get('find_time')} seconds")
                print(f"  Enabled: {'Yes' if config.get('enabled') else 'No'}")
        except OSError:
            print("Status: Not running (PID file exists but process not found)")
            os.remove(pid_file)


if __name__ == '__main__':
    main()
