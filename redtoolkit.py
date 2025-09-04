#!/usr/bin/env python3
"""
RED Team Toolkit - Public Demo Version
Licensed under Strat24 Research License

This is the public version distributed after license generation.
Full functionality requires valid license key.
"""

import json
import sys
import os
import requests
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import platform

__version__ = "3.0.0"
__repo_url__ = "https://api.github.com/repos/YOUR_USERNAME/red-team-toolkit-public"

class LicenseManager:
    def __init__(self):
        self.license_file = Path(__file__).parent / "license.json"
        self.config_file = Path(__file__).parent / "config.json"
        
    def load_license(self):
        """Load license from file"""
        if not self.license_file.exists():
            return None
        
        try:
            with open(self.license_file, 'r') as f:
                return json.load(f)
        except:
            return None
    
    def save_license(self, license_data):
        """Save license to file"""
        try:
            with open(self.license_file, 'w') as f:
                json.dump(license_data, f, indent=2)
            return True
        except:
            return False
    
    def validate_license_key(self, license_key, email, company):
        """Validate license key format and generate license data"""
        if not license_key or len(license_key) < 10:
            return None
        
        # Generate deterministic license data based on key
        license_hash = hashlib.sha256(f"{license_key}{email}{company}".encode()).hexdigest()
        
        # Create license with 30-day validity
        expires = datetime.now() + timedelta(days=30)
        
        license_data = {
            "license_key": license_key,
            "email": email,
            "company": company,
            "expires": expires.isoformat(),
            "version": __version__,
            "platform": platform.system().lower(),
            "hash": license_hash[:16],
            "created": datetime.now().isoformat()
        }
        
        return license_data
    
    def is_license_valid(self, license_data):
        """Check if license is still valid"""
        if not license_data:
            return False
        
        try:
            expires = datetime.fromisoformat(license_data['expires'])
            return datetime.now() < expires
        except:
            return False
    
    def get_days_remaining(self, license_data):
        """Get days remaining on license"""
        try:
            expires = datetime.fromisoformat(license_data['expires'])
            remaining = expires - datetime.now()
            return max(0, remaining.days)
        except:
            return 0

class UpdateManager:
    def __init__(self):
        self.repo_url = __repo_url__
        self.current_version = __version__
    
    def check_for_updates(self):
        """Check for updates from GitHub repository"""
        try:
            response = requests.get(f"{self.repo_url}/releases/latest", timeout=5)
            if response.status_code == 200:
                release_data = response.json()
                latest_version = release_data.get('tag_name', '').replace('v', '')
                
                if self.is_newer_version(latest_version, self.current_version):
                    return {
                        'available': True,
                        'version': latest_version,
                        'url': release_data.get('html_url'),
                        'notes': release_data.get('body', 'No release notes available')
                    }
            
            return {'available': False}
        except:
            return {'available': False, 'error': 'Unable to check for updates'}
    
    def is_newer_version(self, latest, current):
        """Compare version strings"""
        try:
            latest_parts = [int(x) for x in latest.split('.')]
            current_parts = [int(x) for x in current.split('.')]
            
            # Pad shorter version with zeros
            max_len = max(len(latest_parts), len(current_parts))
            latest_parts += [0] * (max_len - len(latest_parts))
            current_parts += [0] * (max_len - len(current_parts))
            
            return latest_parts > current_parts
        except:
            return False
    
    def download_update(self, download_url):
        """Download and install update"""
        try:
            print("🔄 Downloading update...")
            response = requests.get(download_url, timeout=30)
            
            if response.status_code == 200:
                # Save new version
                backup_file = Path(__file__).parent / f"redtoolkit_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
                Path(__file__).rename(backup_file)
                
                with open(__file__, 'wb') as f:
                    f.write(response.content)
                
                print("✅ Update downloaded successfully!")
                print("🔄 Please restart the application to use the new version")
                return True
            
        except Exception as e:
            print(f"❌ Update failed: {e}")
            return False

class RedTeamToolkit:
    def __init__(self):
        self.license_manager = LicenseManager()
        self.update_manager = UpdateManager()
        self.license_data = None
        
    def display_banner(self):
        """Display application banner"""
        print("\n" + "="*60)
        print("""
██████╗ ███████╗██████╗ 
██╔══██╗██╔════╝██╔══██╗
██████╔╝█████╗  ██║  ██║
██╔══██╗██╔══╝  ██║  ██║
██║  ██║███████╗██████╔╝
╚═╝  ╚═╝╚══════╝╚═════╝ 
        """)
        print("    Advanced Penetration Testing Framework v" + __version__)
        print("    Strat24 Research + V3ctor Security")
        print("="*60)
    
    def setup_license(self):
        """Interactive license setup"""
        print("\n🔐 License Setup Required")
        print("-" * 30)
        
        license_key = input("Enter License Key: ").strip()
        if not license_key:
            print("❌ License key is required")
            return False
        
        email = input("Enter Email: ").strip()
        if not email:
            print("❌ Email is required")
            return False
        
        company = input("Enter Company/Organization: ").strip()
        if not company:
            print("❌ Company is required")
            return False
        
        # Validate and create license
        license_data = self.license_manager.validate_license_key(license_key, email, company)
        
        if license_data and self.license_manager.save_license(license_data):
            self.license_data = license_data
            print("✅ License activated successfully!")
            print(f"📅 Valid until: {datetime.fromisoformat(license_data['expires']).strftime('%Y-%m-%d')}")
            return True
        else:
            print("❌ Invalid license key or setup failed")
            return False
    
    def check_license(self):
        """Check and validate license"""
        self.license_data = self.license_manager.load_license()
        
        if not self.license_data:
            print("❌ No license found")
            return self.setup_license()
        
        if not self.license_manager.is_license_valid(self.license_data):
            days_remaining = self.license_manager.get_days_remaining(self.license_data)
            if days_remaining <= 0:
                print("❌ License has expired")
                print("📧 Contact sudo@hxcode.xyz for renewal")
                return False
        
        days_remaining = self.license_manager.get_days_remaining(self.license_data)
        print(f"✅ License valid - {days_remaining} days remaining")
        print(f"📧 Licensed to: {self.license_data['email']}")
        
        if days_remaining <= 7:
            print(f"⚠️  License expires in {days_remaining} days")
            print("📧 Contact sudo@hxcode.xyz for renewal")
        
        return True
    
    def check_updates(self):
        """Check for application updates"""
        print("\n🔄 Checking for updates...")
        update_info = self.update_manager.check_for_updates()
        
        if update_info.get('available'):
            print(f"🆕 Update available: v{update_info['version']}")
            print(f"📝 Release notes: {update_info['notes'][:100]}...")
            
            choice = input("\nDownload update? (y/N): ").lower().strip()
            if choice == 'y':
                # For demo, just show the URL
                print(f"🔗 Download from: {update_info['url']}")
                print("📥 Manual installation required for demo version")
        elif update_info.get('error'):
            print(f"⚠️  {update_info['error']}")
        else:
            print("✅ You have the latest version")
    
    def show_main_menu(self):
        """Display main application menu"""
        while True:
            print("\n" + "="*40)
            print("🎯 MAIN MENU")
            print("="*40)
            print("1. 🔍 Reconnaissance Tools")
            print("2. 💥 Exploit Framework") 
            print("3. 🤖 AI Analysis")
            print("4. 📱 Mobile Testing")
            print("5. 🌐 Web Testing")
            print("6. 📊 Reporting")
            print("7. ⚙️  Settings")
            print("8. 🔄 Check Updates")
            print("9. ℹ️  License Info")
            print("0. 🚪 Exit")
            print("-"*40)
            
            choice = input("Select option (0-9): ").strip()
            
            if choice == '1':
                self.reconnaissance_menu()
            elif choice == '2':
                self.exploit_menu()
            elif choice == '3':
                self.ai_analysis_menu()
            elif choice == '4':
                self.mobile_testing_menu()
            elif choice == '5':
                self.web_testing_menu()
            elif choice == '6':
                self.reporting_menu()
            elif choice == '7':
                self.settings_menu()
            elif choice == '8':
                self.check_updates()
            elif choice == '9':
                self.show_license_info()
            elif choice == '0':
                print("\n👋 Goodbye!")
                break
            else:
                print("❌ Invalid option. Please try again.")
    
    def reconnaissance_menu(self):
        """Reconnaissance tools menu"""
        print("\n🔍 RECONNAISSANCE TOOLS")
        print("-"*30)
        
        while True:
            print("\nAvailable Tools:")
            print("1. 🌐 Network Discovery")
            print("2. 🔍 Port Scanner")
            print("3. 📄 Banner Grabber")
            print("0. ← Back to Main Menu")
            
            choice = input("\nSelect tool: ").strip()
            
            if choice == '1':
                try:
                    from modules.recon.network_discovery import main as network_discovery
                    network_discovery()
                except ImportError:
                    print("❌ Network discovery module not available")
                    input("Press Enter to continue...")
                    
            elif choice == '2':
                try:
                    from modules.network.port_scanner import main as port_scanner
                    port_scanner()
                except ImportError:
                    print("❌ Port scanner module not available")
                    input("Press Enter to continue...")
                    
            elif choice == '3':
                try:
                    from modules.exploits.banner_grabber import main as banner_grabber
                    banner_grabber()
                except ImportError:
                    print("❌ Banner grabber module not available")
                    input("Press Enter to continue...")
                    
            elif choice == '0':
                break
            else:
                print("❌ Invalid option")
    
    def exploit_menu(self):
        """Exploit framework menu"""
        print("\n💥 EXPLOIT FRAMEWORK")
        print("-"*30)
        
        while True:
            print("\nDemo Capabilities:")
            print("1. 🔍 Service Fingerprinting")
            print("2. 🌐 Basic Web Attacks")
            print("3. 📊 Vulnerability Assessment")
            print("4. 📚 CVE Information (Demo)")
            print("0. ← Back to Main Menu")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == '1':
                try:
                    from modules.exploits.banner_grabber import main as banner_grabber
                    banner_grabber()
                except ImportError:
                    print("❌ Banner grabber module not available")
                    input("Press Enter to continue...")
                    
            elif choice == '2':
                try:
                    from modules.exploits.web_scanner import main as web_scanner
                    web_scanner()
                except ImportError:
                    print("❌ Web scanner module not available")
                    input("Press Enter to continue...")
                    
            elif choice == '3':
                print("\n📊 VULNERABILITY ASSESSMENT")
                print("Combines reconnaissance and exploitation techniques")
                
                target = input("Enter target IP/hostname: ").strip()
                if not target:
                    continue
                
                try:
                    from modules.network.port_scanner import PortScanner
                    from modules.exploits.banner_grabber import BannerGrabber
                    
                    print(f"\n🎯 Assessing {target}")
                    print("=" * 40)
                    
                    # Port scan
                    scanner = PortScanner()
                    scanner.scan_common_ports(target)
                    
                    # Banner grab open ports
                    if scanner.open_ports:
                        print("\n🔍 Grabbing service banners...")
                        grabber = BannerGrabber()
                        grabber.scan_multiple_ports(target, scanner.open_ports)
                    
                    input("\nAssessment complete. Press Enter to continue...")
                    
                except ImportError:
                    print("❌ Assessment modules not available")
                    input("Press Enter to continue...")
                    
            elif choice == '4':
                print("\n📚 CVE INFORMATION (Demo)")
                print("In the full version, this provides:")
                print("• Real-time CVE database access")
                print("• Exploit code generation")
                print("• Vulnerability matching")
                print("• Automated exploitation")
                print("\n📧 Contact sudo@hxcode.xyz for full version")
                input("Press Enter to continue...")
                
            elif choice == '0':
                break
            else:
                print("❌ Invalid option")
    
    def ai_analysis_menu(self):
        """AI analysis menu"""
        print("\n🤖 AI ANALYSIS")
        print("-"*30)
        print("Demo Version - Limited Functionality")
        print("• Vulnerability pattern recognition")
        print("• Automated report generation")
        print("• Threat intelligence analysis")
        print("\n📧 Contact sudo@hxcode.xyz for full version")
        input("\nPress Enter to continue...")
    
    def mobile_testing_menu(self):
        """Mobile testing menu"""
        print("\n📱 MOBILE TESTING")
        print("-"*30)
        print("Demo Version - Limited Functionality")
        print("• iOS app analysis")
        print("• Android security testing")
        print("• Mobile device exploitation")
        print("\n📧 Contact sudo@hxcode.xyz for full version")
        input("\nPress Enter to continue...")
    
    def web_testing_menu(self):
        """Web testing menu"""
        print("\n🌐 WEB TESTING")
        print("-"*30)
        
        while True:
            print("\nAvailable Tools:")
            print("1. 🔍 Web Vulnerability Scanner")
            print("2. 🛡️ Security Headers Check")
            print("3. 📊 Full Website Analysis")
            print("0. ← Back to Main Menu")
            
            choice = input("\nSelect tool: ").strip()
            
            if choice == '1':
                try:
                    from modules.exploits.web_scanner import main as web_scanner
                    web_scanner()
                except ImportError:
                    print("❌ Web scanner module not available")
                    input("Press Enter to continue...")
                    
            elif choice == '2':
                try:
                    from modules.exploits.web_scanner import WebScanner
                    scanner = WebScanner()
                    url = input("Enter URL to check headers: ").strip()
                    if url:
                        if not url.startswith(('http://', 'https://')):
                            url = 'http://' + url
                        scanner.check_security_headers(url)
                    input("Press Enter to continue...")
                except ImportError:
                    print("❌ Web scanner module not available")
                    input("Press Enter to continue...")
                    
            elif choice == '3':
                print("\n🔍 FULL WEBSITE ANALYSIS")
                print("This combines multiple scanning techniques:")
                try:
                    from modules.exploits.web_scanner import WebScanner
                    from modules.network.port_scanner import PortScanner
                    
                    target = input("Enter website URL or IP: ").strip()
                    if not target:
                        continue
                        
                    # Extract hostname for port scanning
                    if target.startswith(('http://', 'https://')):
                        import urllib.parse
                        parsed = urllib.parse.urlparse(target)
                        hostname = parsed.hostname
                        url = target
                    else:
                        hostname = target
                        url = f"http://{target}"
                    
                    print(f"\n🎯 Analyzing {target}")
                    print("=" * 50)
                    
                    # Port scan first
                    print("Phase 1: Port Scanning")
                    port_scanner = PortScanner()
                    port_scanner.scan_common_ports(hostname)
                    
                    # Web vulnerability scan
                    print("\nPhase 2: Web Vulnerability Scanning")
                    web_scanner = WebScanner()
                    web_scanner.scan_url(url)
                    
                    input("\nAnalysis complete. Press Enter to continue...")
                    
                except ImportError:
                    print("❌ Analysis modules not available")
                    input("Press Enter to continue...")
                    
            elif choice == '0':
                break
            else:
                print("❌ Invalid option")
    
    def reporting_menu(self):
        """Reporting menu"""
        print("\n📊 REPORTING")
        print("-"*30)
        print("Demo Version - Limited Functionality")
        print("• Executive summary templates")
        print("• Technical findings reports")
        print("• Risk assessment matrices")
        print("\n📧 Contact sudo@hxcode.xyz for full version")
        input("\nPress Enter to continue...")
    
    def settings_menu(self):
        """Settings menu"""
        print("\n⚙️  SETTINGS")
        print("-"*20)
        print("1. 🔑 Update License")
        print("2. 📧 Contact Information")
        print("3. 🔄 Reset Configuration")
        print("0. ← Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == '1':
            self.setup_license()
        elif choice == '2':
            print("\n📧 Support Contact: sudo@hxcode.xyz")
            print("🌐 Website: www.509938.xyz")
            input("\nPress Enter to continue...")
        elif choice == '3':
            confirm = input("⚠️  Reset all configuration? (y/N): ").lower().strip()
            if confirm == 'y':
                try:
                    if self.license_manager.license_file.exists():
                        self.license_manager.license_file.unlink()
                    print("✅ Configuration reset")
                except:
                    print("❌ Reset failed")
            input("Press Enter to continue...")
    
    def show_license_info(self):
        """Display license information"""
        if not self.license_data:
            print("❌ No license information available")
            return
        
        print("\n🔐 LICENSE INFORMATION")
        print("-"*30)
        print(f"License Key: {self.license_data['license_key']}")
        print(f"Email: {self.license_data['email']}")
        print(f"Company: {self.license_data['company']}")
        print(f"Version: {self.license_data['version']}")
        print(f"Platform: {self.license_data['platform']}")
        print(f"Created: {datetime.fromisoformat(self.license_data['created']).strftime('%Y-%m-%d %H:%M')}")
        print(f"Expires: {datetime.fromisoformat(self.license_data['expires']).strftime('%Y-%m-%d %H:%M')}")
        
        days_remaining = self.license_manager.get_days_remaining(self.license_data)
        print(f"Days Remaining: {days_remaining}")
        
        print("\n📧 Contact sudo@hxcode.xyz for full version")
        input("\nPress Enter to continue...")
    
    def run(self):
        """Main application entry point"""
        try:
            self.display_banner()
            
            if not self.check_license():
                print("\n❌ License validation failed")
                print("📧 Contact sudo@hxcode.xyz for support")
                return False
            
            self.show_main_menu()
            return True
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            return True
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            print("📧 Contact sudo@hxcode.xyz for support")
            return False

def main():
    """Application entry point"""
    if len(sys.argv) > 1:
        if sys.argv[1] == '--version':
            print(f"RED Team Toolkit v{__version__}")
            return
        elif sys.argv[1] == '--help':
            print(f"RED Team Toolkit v{__version__}")
            print("Usage: redtoolkit [--version] [--help]")
            print("\nFor support: sudo@hxcode.xyz")
            return
    
    toolkit = RedTeamToolkit()
    toolkit.run()

if __name__ == "__main__":
    main()
