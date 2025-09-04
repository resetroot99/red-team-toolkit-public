#!/usr/bin/env python3
"""
RED Team Toolkit - Network Discovery Module
Real network reconnaissance functionality
"""

import socket
import subprocess
import platform
import ipaddress
import threading
import sys
from datetime import datetime

class NetworkDiscovery:
    def __init__(self):
        self.alive_hosts = []
        self.lock = threading.Lock()
        
    def ping_host(self, ip):
        """Ping a single host"""
        try:
            # Determine ping command based on OS
            if platform.system().lower() == "windows":
                cmd = ["ping", "-n", "1", "-w", "1000", str(ip)]
            else:
                cmd = ["ping", "-c", "1", "-W", "1", str(ip)]
            
            # Execute ping
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3)
            
            if result.returncode == 0:
                with self.lock:
                    self.alive_hosts.append(str(ip))
                return True
            return False
            
        except subprocess.TimeoutExpired:
            return False
        except Exception:
            return False
    
    def discover_network(self, network, threads=50):
        """Discover live hosts in a network"""
        try:
            net = ipaddress.IPv4Network(network, strict=False)
        except ValueError:
            print("❌ Invalid network format. Use CIDR notation (e.g., 192.168.1.0/24)")
            return []
        
        print(f"\n🔍 Discovering hosts in {network}")
        print(f"📊 Scanning {net.num_hosts} possible hosts")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 50)
        
        # Reset results
        self.alive_hosts = []
        
        # Create and manage threads
        thread_list = []
        for ip in net.hosts():
            thread = threading.Thread(target=self.ping_host, args=(ip,))
            thread_list.append(thread)
            thread.start()
            
            # Limit concurrent threads
            if len(thread_list) >= threads:
                for t in thread_list:
                    t.join()
                thread_list = []
        
        # Wait for remaining threads
        for thread in thread_list:
            thread.join()
        
        # Display results
        self.display_discovery_results(network)
        return self.alive_hosts
    
    def display_discovery_results(self, network):
        """Display network discovery results"""
        print(f"\n📊 Network Discovery Results for {network}")
        print("=" * 50)
        
        if self.alive_hosts:
            print(f"\n✅ Live Hosts ({len(self.alive_hosts)}):")
            for host in sorted(self.alive_hosts, key=lambda x: ipaddress.IPv4Address(x)):
                hostname = self.get_hostname(host)
                if hostname and hostname != host:
                    print(f"   {host:15s} ({hostname})")
                else:
                    print(f"   {host:15s}")
        else:
            print("\n❌ No live hosts found")
        
        print(f"\n📈 Summary:")
        print(f"   Live hosts: {len(self.alive_hosts)}")
        print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def get_hostname(self, ip):
        """Get hostname for IP address"""
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            return hostname
        except:
            return None
    
    def get_local_network(self):
        """Get local network information"""
        try:
            # Get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            # Assume /24 network
            network_parts = local_ip.split('.')
            network = f"{network_parts[0]}.{network_parts[1]}.{network_parts[2]}.0/24"
            
            return network, local_ip
        except:
            return None, None
    
    def arp_scan(self):
        """Perform ARP scan on local network"""
        print("\n🔍 ARP SCAN")
        print("=" * 20)
        
        network, local_ip = self.get_local_network()
        if not network:
            print("❌ Could not determine local network")
            return
        
        print(f"Local IP: {local_ip}")
        print(f"Network: {network}")
        
        try:
            if platform.system().lower() == "windows":
                result = subprocess.run(["arp", "-a"], capture_output=True, text=True)
            else:
                result = subprocess.run(["arp", "-a"], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"\n📊 ARP Table:")
                print("-" * 40)
                lines = result.stdout.split('\n')
                for line in lines:
                    if line.strip() and ('dynamic' in line.lower() or 'ether' in line.lower()):
                        print(f"   {line.strip()}")
            else:
                print("❌ Could not retrieve ARP table")
                
        except Exception as e:
            print(f"❌ ARP scan failed: {e}")

def main():
    """Main network discovery interface"""
    discovery = NetworkDiscovery()
    
    print("\n🔍 NETWORK DISCOVERY")
    print("=" * 30)
    print("⚠️  Use only on networks you own or have permission to scan")
    print()
    
    while True:
        print("\nOptions:")
        print("1. Auto-discover local network")
        print("2. Scan specific network")
        print("3. Ping single host")
        print("4. ARP scan")
        print("0. Back to main menu")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == '1':
            network, local_ip = discovery.get_local_network()
            if network:
                print(f"Detected local network: {network}")
                print(f"Your IP: {local_ip}")
                confirm = input("Proceed with scan? (y/N): ")
                if confirm.lower() == 'y':
                    discovery.discover_network(network)
            else:
                print("❌ Could not detect local network")
                
        elif choice == '2':
            network = input("Enter network (CIDR format, e.g., 192.168.1.0/24): ").strip()
            if not network:
                print("❌ Network is required")
                continue
            
            # Validate network format
            try:
                ipaddress.IPv4Network(network, strict=False)
                discovery.discover_network(network)
            except ValueError:
                print("❌ Invalid network format")
                
        elif choice == '3':
            target = input("Enter target IP/hostname: ").strip()
            if not target:
                print("❌ Target is required")
                continue
            
            print(f"\n🔍 Pinging {target}")
            if discovery.ping_host(target):
                print(f"✅ {target} is alive")
                hostname = discovery.get_hostname(target)
                if hostname and hostname != target:
                    print(f"   Hostname: {hostname}")
            else:
                print(f"❌ {target} is not responding")
                
        elif choice == '4':
            discovery.arp_scan()
            
        elif choice == '0':
            break
        else:
            print("❌ Invalid option")

if __name__ == "__main__":
    main()
