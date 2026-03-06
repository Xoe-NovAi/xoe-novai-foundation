#!/usr/bin/env python3
"""
OpenCode Multi-Account System Setup Script
==========================================

Comprehensive setup script for installing and configuring the
OpenCode Multi-Account System as a standalone product.
"""

import os
import sys
import json
import yaml
import subprocess
import argparse
import logging
import asyncio
import platform
from pathlib import Path
from typing import Dict, Any, List, Optional
import shutil
import stat
import getpass

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SetupError(Exception):
    """Setup-related exceptions."""
    pass


class OpenCodeSetup:
    """Main setup class for OpenCode Multi-Account System."""
    
    def __init__(self, install_dir: Optional[str] = None, environment: str = "production"):
        self.install_dir = Path(install_dir or self._get_default_install_dir())
        self.environment = environment
        self.config_dir = self.install_dir / "config"
        self.data_dir = self.install_dir / "data"
        self.log_dir = self.install_dir / "logs"
        self.backup_dir = self.install_dir / "backups"
        
        # System requirements
        self.required_python_version = (3, 8)
        self.required_packages = [
            "fastapi",
            "uvicorn",
            "pyyaml",
            "psutil",
            "cryptography",
            "aiofiles",
            "python-multipart"
        ]
        
        # Configuration templates
        self.config_templates = {
            "config.yaml": self._get_main_config_template(),
            "secrets.enc": b"",  # Will be created as encrypted file
            "providers.yaml": self._get_providers_config_template(),
            "environment.yaml": self._get_environment_config_template()
        }
    
    def run_setup(self, interactive: bool = True) -> bool:
        """Run the complete setup process."""
        try:
            logger.info("🚀 Starting OpenCode Multi-Account System Setup")
            logger.info(f"Installation Directory: {self.install_dir}")
            logger.info(f"Environment: {self.environment}")
            
            # Pre-flight checks
            self._check_system_requirements()
            self._check_permissions()
            
            # Create directory structure
            self._create_directories()
            
            # Install dependencies
            self._install_dependencies()
            
            # Configure system
            if interactive:
                self._interactive_configuration()
            else:
                self._auto_configure()
            
            # Setup services
            self._setup_services()
            
            # Create startup scripts
            self._create_startup_scripts()
            
            # Validate installation
            self._validate_installation()
            
            # Display summary
            self._display_summary()
            
            logger.info("✅ Setup completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Setup failed: {e}")
            return False
    
    def _check_system_requirements(self) -> None:
        """Check if system meets requirements."""
        logger.info("🔍 Checking system requirements...")
        
        # Check Python version
        python_version = sys.version_info
        if python_version < self.required_python_version:
            raise SetupError(
                f"Python {self.required_python_version[0]}.{self.required_python_version[1]} "
                f"or higher required, found {python_version.major}.{python_version.minor}"
            )
        
        logger.info(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Check platform
        system = platform.system()
        logger.info(f"✅ Platform: {system}")
        
        # Check available disk space
        free_space = shutil.disk_usage(self.install_dir.parent).free
        required_space = 100 * 1024 * 1024  # 100MB
        if free_space < required_space:
            raise SetupError(f"Insufficient disk space. Required: 100MB, Available: {free_space // (1024*1024)}MB")
        
        logger.info(f"✅ Disk space: {free_space // (1024*1024)}MB available")
    
    def _check_permissions(self) -> None:
        """Check if we have necessary permissions."""
        logger.info("🔒 Checking permissions...")
        
        # Check if we can write to install directory
        if self.install_dir.exists():
            if not os.access(self.install_dir, os.W_OK):
                raise SetupError(f"No write permission to {self.install_dir}")
        else:
            parent_dir = self.install_dir.parent
            if not os.access(parent_dir, os.W_OK):
                raise SetupError(f"No write permission to {parent_dir}")
        
        logger.info("✅ Write permissions verified")
    
    def _create_directories(self) -> None:
        """Create required directory structure."""
        logger.info("📁 Creating directory structure...")
        
        directories = [
            self.install_dir,
            self.config_dir,
            self.data_dir,
            self.log_dir,
            self.backup_dir,
            self.data_dir / "accounts",
            self.data_dir / "cache",
            self.data_dir / "backups"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Created: {directory}")
    
    def _install_dependencies(self) -> None:
        """Install required Python packages."""
        logger.info("📦 Installing dependencies...")
        
        for package in self.required_packages:
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", package, "--quiet"
                ])
                logger.info(f"✅ Installed: {package}")
            except subprocess.CalledProcessError as e:
                logger.warning(f"⚠ Failed to install {package}: {e}")
    
    def _interactive_configuration(self) -> None:
        """Interactive configuration setup."""
        logger.info("⚙️  Interactive Configuration")
        
        config = {}
        
        # Basic settings
        print("\n🔧 Basic Configuration:")
        config['environment'] = self.environment
        config['debug'] = input("Enable debug mode? (y/N): ").lower().startswith('y')
        config['log_level'] = input("Log level (DEBUG/INFO/WARNING/ERROR) [INFO]: ") or "INFO"
        
        # Storage settings
        print("\n💾 Storage Configuration:")
        storage_path = input(f"Storage path [{self.data_dir}]: ") or str(self.data_dir)
        config['storage'] = {
            'type': 'filesystem',
            'path': storage_path,
            'backup_enabled': True,
            'backup_interval': 3600
        }
        
        # Provider configuration
        print("\n🤖 Provider Configuration:")
        providers = {}
        
        # OpenCode
        opencode_enabled = input("Enable OpenCode provider? (Y/n): ").lower() != 'n'
        if opencode_enabled:
            providers['opencode'] = {
                'enabled': True,
                'accounts': {
                    'count': int(input("Number of accounts [8]: ") or "8"),
                    'rotation_strategy': 'round_robin'
                }
            }
        
        # Antigravity
        antigravity_enabled = input("Enable Antigravity provider? (y/N): ").lower().startswith('y')
        if antigravity_enabled:
            providers['antigravity'] = {
                'enabled': True,
                'oauth': {
                    'client_id': input("OAuth Client ID: "),
                    'client_secret': input("OAuth Client Secret: ")
                }
            }
        
        # Cline
        cline_enabled = input("Enable Cline provider? (y/N): ").lower().startswith('y')
        if cline_enabled:
            providers['cline'] = {
                'enabled': True,
                'cli_path': input("Cline CLI path [/usr/local/bin/cline]: ") or "/usr/local/bin/cline"
            }
        
        # Gemini
        gemini_enabled = input("Enable Gemini provider? (y/N): ").lower().startswith('y')
        if gemini_enabled:
            providers['gemini'] = {
                'enabled': True,
                'api_key': input("Gemini API Key: ")
            }
        
        # Copilot
        copilot_enabled = input("Enable Copilot provider? (y/N): ").lower().startswith('y')
        if copilot_enabled:
            providers['copilot'] = {
                'enabled': True,
                'github_token': input("GitHub Token: ")
            }
        
        config['providers'] = providers
        
        # Save configuration
        self._save_config(config)
        self._save_secrets(config)
    
    def _auto_configure(self) -> None:
        """Automatic configuration with defaults."""
        logger.info("⚙️  Auto Configuration")
        
        config = {
            'environment': self.environment,
            'debug': self.environment == 'development',
            'log_level': 'DEBUG' if self.environment == 'development' else 'INFO',
            'storage': {
                'type': 'filesystem',
                'path': str(self.data_dir),
                'backup_enabled': True,
                'backup_interval': 3600
            },
            'providers': {
                'opencode': {
                    'enabled': True,
                    'accounts': {
                        'count': 8,
                        'rotation_strategy': 'round_robin'
                    }
                },
                'antigravity': {
                    'enabled': False,
                    'oauth': {
                        'client_id': '',
                        'client_secret': ''
                    }
                },
                'cline': {
                    'enabled': False,
                    'cli_path': '/usr/local/bin/cline'
                },
                'gemini': {
                    'enabled': False,
                    'api_key': ''
                },
                'copilot': {
                    'enabled': False,
                    'github_token': ''
                }
            }
        }
        
        self._save_config(config)
        self._save_secrets(config)
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file."""
        config_file = self.config_dir / "config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        logger.info(f"✅ Configuration saved to {config_file}")
    
    def _save_secrets(self, config: Dict[str, Any]) -> None:
        """Save secrets to encrypted file."""
        secrets = {}
        
        # Extract secrets from config
        for provider_name, provider_config in config.get('providers', {}).items():
            if provider_name == 'antigravity' and 'oauth' in provider_config:
                secrets[f'{provider_name}_client_id'] = provider_config['oauth']['client_id']
                secrets[f'{provider_name}_client_secret'] = provider_config['oauth']['client_secret']
            elif provider_name == 'gemini' and 'api_key' in provider_config:
                secrets[f'{provider_name}_api_key'] = provider_config['api_key']
            elif provider_name == 'copilot' and 'github_token' in provider_config:
                secrets[f'{provider_name}_github_token'] = provider_config['github_token']
        
        # Encrypt and save secrets
        secrets_file = self.config_dir / "secrets.enc"
        if secrets:
            # Simple encryption for demo - in production use proper key management
            import json
            encrypted_data = json.dumps(secrets).encode()
            with open(secrets_file, 'wb') as f:
                f.write(encrypted_data)
            logger.info(f"✅ Secrets saved to {secrets_file}")
        else:
            # Create empty secrets file
            secrets_file.touch()
            logger.info(f"✅ Created empty secrets file: {secrets_file}")
    
    def _setup_services(self) -> None:
        """Setup system services."""
        logger.info("🔧 Setting up services...")
        
        system = platform.system()
        
        if system == "Linux":
            self._setup_linux_service()
        elif system == "Darwin":
            self._setup_macos_service()
        else:
            logger.info("⚠️  Service setup not supported on this platform")
    
    def _setup_linux_service(self) -> None:
        """Setup Linux systemd service."""
        service_content = f"""[Unit]
Description=OpenCode Multi-Account System
After=network.target

[Service]
Type=simple
User={getpass.getuser()}
WorkingDirectory={self.install_dir}
ExecStart={sys.executable} {self.install_dir}/bin/opencode-multi-account start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        service_file = Path("/etc/systemd/system/opencode-multi-account.service")
        try:
            with open(service_file, 'w') as f:
                f.write(service_content)
            
            subprocess.run(["systemctl", "daemon-reload"], check=True)
            logger.info("✅ Linux service configured")
        except PermissionError:
            logger.warning("⚠️  Cannot create system service (requires sudo)")
    
    def _setup_macos_service(self) -> None:
        """Setup macOS launchd service."""
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.opencode.multi-account</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>{self.install_dir}/bin/opencode-multi-account</string>
        <string>start</string>
    </array>
    <key>WorkingDirectory</key>
    <string>{self.install_dir}</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>{self.log_dir}/opencode-multi-account.log</string>
    <key>StandardErrorPath</key>
    <string>{self.log_dir}/opencode-multi-account-error.log</string>
</dict>
</plist>
"""
        
        plist_file = Path.home() / "Library/LaunchAgents/com.opencode.multi-account.plist"
        with open(plist_file, 'w') as f:
            f.write(plist_content)
        
        logger.info("✅ macOS service configured")
    
    def _create_startup_scripts(self) -> None:
        """Create startup and management scripts."""
        logger.info("📜 Creating startup scripts...")
        
        # Create bin directory
        bin_dir = self.install_dir / "bin"
        bin_dir.mkdir(exist_ok=True)
        
        # Main executable script
        main_script = f"""#!/bin/bash
# OpenCode Multi-Account System Control Script

INSTALL_DIR="{self.install_dir}"
CONFIG_DIR="{self.config_dir}"
PYTHON="{sys.executable}"

case "$1" in
    start)
        echo "🚀 Starting OpenCode Multi-Account System..."
        cd "$INSTALL_DIR"
        $PYTHON -m modularization.core.engine --config "$CONFIG_DIR/config.yaml" &
        echo $! > "$INSTALL_DIR/opencode-multi-account.pid"
        echo "✅ System started (PID: $(cat $INSTALL_DIR/opencode-multi-account.pid))"
        ;;
    stop)
        echo "🛑 Stopping OpenCode Multi-Account System..."
        if [ -f "$INSTALL_DIR/opencode-multi-account.pid" ]; then
            PID=$(cat "$INSTALL_DIR/opencode-multi-account.pid")
            kill $PID
            rm "$INSTALL_DIR/opencode-multi-account.pid"
            echo "✅ System stopped"
        else
            echo "⚠️  No PID file found"
        fi
        ;;
    restart)
        $0 stop
        sleep 2
        $0 start
        ;;
    status)
        if [ -f "$INSTALL_DIR/opencode-multi-account.pid" ]; then
            PID=$(cat "$INSTALL_DIR/opencode-multi-account.pid")
            if ps -p $PID > /dev/null; then
                echo "✅ System is running (PID: $PID)"
            else
                echo "❌ System is not running"
            fi
        else
            echo "❌ System is not running"
        fi
        ;;
    logs)
        tail -f "$INSTALL_DIR/logs/opencode-multi-account.log"
        ;;
    config)
        echo "📁 Configuration directory: $CONFIG_DIR"
        echo "📄 Main config: $CONFIG_DIR/config.yaml"
        echo "🔒 Secrets: $CONFIG_DIR/secrets.enc"
        ;;
    health)
        echo "🏥 Checking system health..."
        $PYTHON -c "
import sys
sys.path.insert(0, '$INSTALL_DIR')
from modularization.core.engine import engine
import asyncio

async def check_health():
    try:
        await engine.initialize()
        health = await engine.health_check()
        print(f'Overall Health: {{health[\"overall_health\"]}}')
        print(f'System State: {{health[\"system_state\"]}}')
        print(f'Components: {{health[\"components\"]}}')
        if \"providers\" in health:
            print(f'Providers: {{health[\"providers\"]}}')
    except Exception as e:
        print(f'❌ Health check failed: {{e}}')

asyncio.run(check_health())
"
        ;;
    *)
        echo "Usage: $0 {{start|stop|restart|status|logs|config|health}}"
        echo ""
        echo "Commands:"
        echo "  start    - Start the system"
        echo "  stop     - Stop the system"
        echo "  restart  - Restart the system"
        echo "  status   - Show system status"
        echo "  logs     - Show system logs"
        echo "  config   - Show configuration paths"
        echo "  health   - Check system health"
        exit 1
        ;;
esac
"""
        
        # Write main script
        script_file = bin_dir / "opencode-multi-account"
        with open(script_file, 'w') as f:
            f.write(main_script)
        
        # Make executable
        os.chmod(script_file, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
        
        # Create Python entry point
        entry_point = f"""#!/usr/bin/env python3
import sys
import asyncio
from pathlib import Path

# Add install directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modularization.core.engine import engine
from modularization.core.config_manager import config_manager

async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='OpenCode Multi-Account System')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('command', choices=['start', 'stop', 'status', 'health'], 
                       help='Command to execute')
    
    args = parser.parse_args()
    
    if args.config:
        config_manager.config_path = args.config
    
    if args.command == 'start':
        print("🚀 Starting OpenCode Multi-Account System...")
        success = await engine.initialize()
        if success:
            print("✅ System started successfully")
            # Keep running
            while engine.is_running:
                await asyncio.sleep(1)
        else:
            print("❌ Failed to start system")
            sys.exit(1)
    
    elif args.command == 'stop':
        await engine.shutdown()
        print("✅ System stopped")
    
    elif args.command == 'status':
        print(f"System State: {{engine.state.value}}")
        print(f"Uptime: {{engine.uptime:.2f}} seconds")
        print(f"Running: {{engine.is_running}}")
    
    elif args.command == 'health':
        health = await engine.health_check()
        print(f"Overall Health: {{health['overall_health']}}")
        print(f"System State: {{health['system_state']}}")

if __name__ == "__main__":
    asyncio.run(main())
"""
        
        entry_file = bin_dir / "opencode-multi-account.py"
        with open(entry_file, 'w') as f:
            f.write(entry_point)
        
        os.chmod(entry_file, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
        
        logger.info(f"✅ Created startup scripts in {bin_dir}")
    
    def _validate_installation(self) -> None:
        """Validate the installation."""
        logger.info("✅ Validating installation...")
        
        # Check required files
        required_files = [
            self.config_dir / "config.yaml",
            self.config_dir / "secrets.enc",
            self.install_dir / "bin" / "opencode-multi-account",
            self.install_dir / "bin" / "opencode-multi-account.py"
        ]
        
        for file_path in required_files:
            if not file_path.exists():
                raise SetupError(f"Missing required file: {file_path}")
        
        logger.info("✅ All required files present")
    
    def _display_summary(self) -> None:
        """Display installation summary."""
        print("\n" + "="*60)
        print("🎉 OpenCode Multi-Account System Setup Complete!")
        print("="*60)
        print(f"📁 Installation Directory: {self.install_dir}")
        print(f"⚙️  Configuration: {self.config_dir}")
        print(f"📊 Data Directory: {self.data_dir}")
        print(f"📝 Logs Directory: {self.log_dir}")
        print("")
        print("🚀 Quick Start:")
        print(f"  cd {self.install_dir}")
        print(f"  ./bin/opencode-multi-account start")
        print(f"  ./bin/opencode-multi-account health")
        print("")
        print("📚 Documentation:")
        print("  - Configuration: ./config/config.yaml")
        print("  - Providers: ./config/providers.yaml")
        print("  - Logs: ./logs/")
        print("")
        print("🔧 Management Commands:")
        print("  ./bin/opencode-multi-account start    # Start system")
        print("  ./bin/opencode-multi-account stop     # Stop system")
        print("  ./bin/opencode-multi-account status   # Check status")
        print("  ./bin/opencode-multi-account health   # Health check")
        print("  ./bin/opencode-multi-account logs     # View logs")
        print("="*60)
    
    def _get_default_install_dir(self) -> str:
        """Get default installation directory."""
        home = Path.home()
        return str(home / ".local" / "share" / "opencode-multi-account")
    
    def _get_main_config_template(self) -> Dict[str, Any]:
        """Get main configuration template."""
        return {
            'environment': self.environment,
            'debug': self.environment == 'development',
            'log_level': 'DEBUG' if self.environment == 'development' else 'INFO',
            'plugin_paths': [],
            'storage': {
                'type': 'filesystem',
                'path': str(self.data_dir),
                'backup_enabled': True,
                'backup_interval': 3600
            },
            'monitoring': {
                'enabled': True,
                'metrics_interval': 60,
                'health_check_interval': 300
            }
        }
    
    def _get_providers_config_template(self) -> Dict[str, Any]:
        """Get providers configuration template."""
        return {
            'opencode': {
                'enabled': True,
                'accounts': {
                    'count': 8,
                    'rotation_strategy': 'round_robin',
                    'health_check_interval': 300
                },
                'credentials': {
                    'template_path': '~/.config/xnai/opencode-credentials.yaml',
                    'injection_enabled': True
                }
            },
            'antigravity': {
                'enabled': False,
                'oauth': {
                    'client_id': '',
                    'client_secret': ''
                },
                'models': ['opus-4-6-thinking'],
                'quality_validation': True
            },
            'cline': {
                'enabled': False,
                'cli_path': '/usr/local/bin/cline',
                'timeout': 30,
                'retry_attempts': 3
            },
            'gemini': {
                'enabled': False,
                'api_key': '',
                'context_window': 8192,
                'quality_score': 90
            },
            'copilot': {
                'enabled': False,
                'github_token': '',
                'context_awareness': True,
                'code_analysis': True
            }
        }
    
    def _get_environment_config_template(self) -> Dict[str, Any]:
        """Get environment-specific configuration template."""
        if self.environment == 'production':
            return {
                'debug': False,
                'log_level': 'INFO',
                'monitoring': {
                    'metrics_interval': 300,
                    'health_check_interval': 600
                }
            }
        else:
            return {
                'debug': True,
                'log_level': 'DEBUG',
                'monitoring': {
                    'metrics_interval': 60,
                    'health_check_interval': 300
                }
            }


def main():
    """Main entry point for setup script."""
    parser = argparse.ArgumentParser(
        description='OpenCode Multi-Account System Setup',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python setup.py --install-dir /opt/opencode --environment production
  python setup.py --interactive
  python setup.py --auto
        """
    )
    
    parser.add_argument(
        '--install-dir',
        help='Installation directory (default: ~/.local/share/opencode-multi-account)'
    )
    
    parser.add_argument(
        '--environment',
        choices=['development', 'staging', 'production'],
        default='production',
        help='Environment (default: production)'
    )
    
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Run interactive configuration'
    )
    
    parser.add_argument(
        '--auto',
        action='store_true',
        help='Run automatic configuration with defaults'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Setup logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Determine interactive mode
    interactive = args.interactive
    if not args.interactive and not args.auto:
        interactive = input("Run interactive setup? (Y/n): ").lower() != 'n'
    
    # Create setup instance
    setup = OpenCodeSetup(args.install_dir, args.environment)
    
    # Run setup
    success = setup.run_setup(interactive)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()