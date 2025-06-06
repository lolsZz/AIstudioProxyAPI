#!/usr/bin/env python3
"""
AIstudioProxyAPI Python Startup Script
Simple Python wrapper for easy startup of the AI Studio Proxy API
"""

import os
import sys
import subprocess
import argparse
import json
import requests
from pathlib import Path
from typing import Optional

# Colors for terminal output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def print_status(message: str):
    print(f"{Colors.GREEN}[INFO]{Colors.NC} {message}")

def print_warning(message: str):
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")

def print_error(message: str):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")

def print_header():
    print(f"{Colors.BLUE}================================{Colors.NC}")
    print(f"{Colors.BLUE}  AI Studio Proxy API Launcher{Colors.NC}")
    print(f"{Colors.BLUE}================================{Colors.NC}")

class AIStudioLauncher:
    def __init__(self):
        self.script_dir = Path(__file__).parent.absolute()
        self.venv_dir = self.script_dir / ".venv"
        self.auth_active_dir = self.script_dir / "auth_profiles" / "active"
        self.auth_saved_dir = self.script_dir / "auth_profiles" / "saved"
        
        # Default configuration
        self.default_server_port = 2048
        self.default_stream_port = 3120
        self.default_helper = ""
        self.default_proxy = ""
    
    def check_environment(self) -> bool:
        """Check if virtual environment exists and dependencies are installed"""
        if not self.venv_dir.exists():
            print_error(f"Virtual environment not found at {self.venv_dir}")
            print_error("Please run: uv venv .venv && source .venv/bin/activate && uv install -r requirements.txt")
            return False
        
        # Check if launch_camoufox.py exists
        if not (self.script_dir / "launch_camoufox.py").exists():
            print_error("launch_camoufox.py not found in current directory")
            return False
        
        print_status("Environment check passed")
        return True
    
    def check_authentication(self) -> bool:
        """Check if authentication files are available"""
        # Create auth directories if they don't exist
        self.auth_active_dir.mkdir(parents=True, exist_ok=True)
        self.auth_saved_dir.mkdir(parents=True, exist_ok=True)
        
        # Check for active authentication files
        active_files = list(self.auth_active_dir.glob("*.json"))
        saved_files = list(self.auth_saved_dir.glob("*.json"))
        
        if active_files:
            print_status("Active authentication found - can run in headless mode")
            return True
        elif saved_files:
            print_warning("Saved authentication found but not active")
            print_status("Moving saved authentication to active directory...")
            for saved_file in saved_files:
                target = self.auth_active_dir / saved_file.name
                target.write_bytes(saved_file.read_bytes())
            return True
        else:
            print_warning("No authentication found - will need to authenticate first")
            return False
    
    def run_command(self, mode: str, server_port: int, stream_port: int) -> int:
        """Run the launch command with specified parameters"""
        # Prepare the command
        python_exe = self.venv_dir / "bin" / "python3"
        if not python_exe.exists():
            python_exe = "python3"  # Fallback to system python
        
        cmd = [
            str(python_exe),
            "launch_camoufox.py",
            f"--{mode}",
            "--server-port", str(server_port),
            "--stream-port", str(stream_port),
            "--helper", self.default_helper,
            "--internal-camoufox-proxy", self.default_proxy
        ]
        
        # Set environment variables
        env = os.environ.copy()
        if self.venv_dir.exists():
            env["PATH"] = f"{self.venv_dir / 'bin'}:{env.get('PATH', '')}"
            env["VIRTUAL_ENV"] = str(self.venv_dir)
        
        print_status(f"Starting in {mode} mode...")
        print_status(f"Server will be available at: http://127.0.0.1:{server_port}")
        
        try:
            # Run the command
            result = subprocess.run(cmd, cwd=self.script_dir, env=env)
            return result.returncode
        except KeyboardInterrupt:
            print_status("Stopped by user")
            return 0
        except Exception as e:
            print_error(f"Failed to start: {e}")
            return 1
    
    def test_api(self, server_port: int) -> bool:
        """Test if API endpoints are responding"""
        base_url = f"http://127.0.0.1:{server_port}"
        
        print_status("Testing API endpoints...")
        
        endpoints = [
            ("/health", "Health"),
            ("/v1/models", "Models"),
            ("/api/info", "API Info")
        ]
        
        for endpoint, name in endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    print_status(f"✅ {name} endpoint responding")
                else:
                    print_error(f"❌ {name} endpoint returned status {response.status_code}")
                    return False
            except requests.exceptions.RequestException as e:
                print_error(f"❌ {name} endpoint not responding: {e}")
                return False
        
        print_status("All API endpoints are working!")
        print()
        print(f"API Base URL: {base_url}/v1")
        print(f"Health Check: {base_url}/health")
        print(f"Models List:  {base_url}/v1/models")
        print(f"API Info:     {base_url}/api/info")
        return True

def main():
    parser = argparse.ArgumentParser(
        description="AI Studio Proxy API Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 start.py                    # Auto mode (headless if auth available)
  python3 start.py headless           # Force headless mode
  python3 start.py debug              # Force debug mode with browser
  python3 start.py auth               # Setup authentication only
  python3 start.py test               # Test API endpoints
  python3 start.py headless --server-port 8080
        """
    )
    
    parser.add_argument(
        'mode',
        nargs='?',
        default='auto',
        choices=['auto', 'headless', 'debug', 'auth', 'test'],
        help='Launch mode (default: auto)'
    )
    
    parser.add_argument(
        '--server-port',
        type=int,
        default=2048,
        help='FastAPI server port (default: 2048)'
    )
    
    parser.add_argument(
        '--stream-port',
        type=int,
        default=3120,
        help='Stream proxy port (default: 3120)'
    )
    
    args = parser.parse_args()
    
    print_header()
    
    launcher = AIStudioLauncher()
    
    # Check environment
    if not launcher.check_environment():
        return 1
    
    # Handle different modes
    if args.mode == 'auto':
        if launcher.check_authentication():
            print_status("Auto mode: Running in headless mode")
            return launcher.run_command('headless', args.server_port, args.stream_port)
        else:
            print_status("Auto mode: No authentication found, running debug mode for setup")
            return launcher.run_command('debug', args.server_port, args.stream_port)
    
    elif args.mode == 'headless':
        if launcher.check_authentication():
            return launcher.run_command('headless', args.server_port, args.stream_port)
        else:
            print_error("No authentication found. Run 'python3 start.py auth' first or use debug mode.")
            return 1
    
    elif args.mode == 'debug':
        return launcher.run_command('debug', args.server_port, args.stream_port)
    
    elif args.mode == 'auth':
        return launcher.run_command('debug', args.server_port, args.stream_port)
    
    elif args.mode == 'test':
        if launcher.test_api(args.server_port):
            return 0
        else:
            return 1
    
    else:
        print_error(f"Invalid mode: {args.mode}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
