#!/usr/bin/env python3
"""
RED Team Toolkit - Port Scanner Module
Real network port scanning functionality for demo
"""

import socket
import threading
import sys
from datetime import datetime
import subprocess
import platform

class PortScanner:
    def __init__(self):
        self.open_ports = []
        self.closed_ports = []
        self.filtered_ports = []
        self.lock = threading.Lock()
        
    def scan_port(self, target, port, timeout=1):
        """Scan a single port"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((target, port))
            sock.close()
            
            with self.lock:
                if result == 0:
                    self.open_ports.append(port)
                    return True
                else:
                    self.closed_ports.append(port)
                    return False
        except socket.gaierror:
            with self.lock:
                self.filtered_ports.append(port)
            return False
        except Exception:
            with self.lock:
                self.filtered_ports.append(port)
            return False
    
    def get_service_name(self, port):
        """Get service name for common ports"""
        services = {
            21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
            80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 993: "IMAPS",
            995: "POP3S", 3389: "RDP", 5432: "PostgreSQL", 3306: "MySQL",
            1433: "MSSQL", 6379: "Redis", 27017: "MongoDB", 5984: "CouchDB"
        }
        return services.get(port, "Unknown")
    
    def scan_range(self, target, start_port, end_port, threads=50):
        """Scan a range of ports with threading"""
        print(f"\n🔍 Scanning {target} ports {start_port}-{end_port}")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 50)
        
        # Reset results
        self.open_ports = []
        self.closed_ports = []
        self.filtered_ports = []
        
        # Create and start threads
        thread_list = []
        for port in range(start_port, end_port + 1):
            thread = threading.Thread(target=self.scan_port, args=(target, port))
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
        self.display_results(target)
    
    def scan_common_ports(self, target):
        """Scan common ports"""
        common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3389, 5432, 3306, 1433]
        
        print(f"\n🎯 Scanning common ports on {target}")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 50)
        
        # Reset results
        self.open_ports = []
        self.closed_ports = []
        self.filtered_ports = []
        
        threads = []
        for port in common_ports:
            thread = threading.Thread(target=self.scan_port, args=(target, port))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        self.display_results(target)
    
    def display_results(self, target):
        """Display scan results"""
        print(f"\n📊 Scan Results for {target}")
        print("=" * 50)
        
        if self.open_ports:
            print(f"\n✅ Open Ports ({len(self.open_ports)}):")
            for port in sorted(self.open_ports):
                service = self.get_service_name(port)
                print(f"   {port:5d}/tcp   open    {service}")
        
        if self.filtered_ports:
            print(f"\n🚫 Filtered Ports ({len(self.filtered_ports)}):")
            for port in sorted(self.filtered_ports)[:10]:  # Show first 10
                print(f"   {port:5d}/tcp   filtered")
            if len(self.filtered_ports) > 10:
                print(f"   ... and {len(self.filtered_ports) - 10} more")
        
        print(f"\n📈 Summary:")
        print(f"   Open: {len(self.open_ports)}")
        print(f"   Closed: {len(self.closed_ports)}")
        print(f"   Filtered: {len(self.filtered_ports)}")
        print(f"   Total Scanned: {len(self.open_ports) + len(self.closed_ports) + len(self.filtered_ports)}")
        
        print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def validate_target(target):
    """Validate target IP or hostname"""
    try:
        socket.gethostbyname(target)
        return True
    except socket.gaierror:
        return False

def main():
    """Main port scanner interface"""
    scanner = PortScanner()
    
    print("\n🔍 PORT SCANNER")
    print("=" * 30)
    print("⚠️  Use only on systems you own or have permission to test")
    print()
    
    while True:
        print("\nOptions:")
        print("1. Scan common ports")
        print("2. Scan port range")
        print("3. Scan single port")
        print("0. Back to main menu")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == '1':
            target = input("Enter target IP/hostname: ").strip()
            if not target:
                print("❌ Target is required")
                continue
            
            if not validate_target(target):
                print("❌ Invalid target or unable to resolve hostname")
                continue
            
            scanner.scan_common_ports(target)
            
        elif choice == '2':
            target = input("Enter target IP/hostname: ").strip()
            if not target:
                print("❌ Target is required")
                continue
            
            if not validate_target(target):
                print("❌ Invalid target or unable to resolve hostname")
                continue
            
            try:
                start_port = int(input("Enter start port (1-65535): "))
                end_port = int(input("Enter end port (1-65535): "))
                
                if start_port < 1 or end_port > 65535 or start_port > end_port:
                    print("❌ Invalid port range")
                    continue
                
                if end_port - start_port > 1000:
                    confirm = input(f"⚠️  Scanning {end_port - start_port + 1} ports. Continue? (y/N): ")
                    if confirm.lower() != 'y':
                        continue
                
                scanner.scan_range(target, start_port, end_port)
                
            except ValueError:
                print("❌ Invalid port number")
                continue
                
        elif choice == '3':
            target = input("Enter target IP/hostname: ").strip()
            if not target:
                print("❌ Target is required")
                continue
            
            if not validate_target(target):
                print("❌ Invalid target or unable to resolve hostname")
                continue
            
            try:
                port = int(input("Enter port (1-65535): "))
                if port < 1 or port > 65535:
                    print("❌ Invalid port number")
                    continue
                
                print(f"\n🔍 Scanning {target}:{port}")
                if scanner.scan_port(target, port):
                    service = scanner.get_service_name(port)
                    print(f"✅ Port {port} is OPEN ({service})")
                else:
                    print(f"❌ Port {port} is CLOSED or FILTERED")
                    
            except ValueError:
                print("❌ Invalid port number")
                continue
                
        elif choice == '0':
            break
        else:
            print("❌ Invalid option")

if __name__ == "__main__":
    main()
