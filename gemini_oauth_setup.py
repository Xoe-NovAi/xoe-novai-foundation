#!/usr/bin/env python3
"""
Gemini OAuth Setup and Authentication Manager

This script provides comprehensive solutions for setting up Gemini authentication
including both API key and OAuth 2.0 methods. It addresses region restrictions
by providing OAuth as an alternative to API keys.

Author: XNAi Foundation
Version: 1.0.0
"""

import os
import json
import subprocess
import webbrowser
import tempfile
import time
from pathlib import Path
from typing import Dict, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GeminiAuthManager:
    """Manage Gemini authentication including API keys and OAuth"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".xnai" / "auth"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.auth_config = self.config_dir / "gemini_auth.json"
        
    def load_auth_config(self) -> Dict:
        """Load existing authentication configuration"""
        if self.auth_config.exists():
            with open(self.auth_config, 'r') as f:
                return json.load(f)
        return {}
    
    def save_auth_config(self, config: Dict):
        """Save authentication configuration"""
        with open(self.auth_config, 'w') as f:
            json.dump(config, f, indent=2)
    
    def check_gcloud_installed(self) -> bool:
        """Check if gcloud CLI is installed"""
        try:
            result = subprocess.run(['gcloud', '--version'], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def install_gcloud(self):
        """Install gcloud CLI"""
        logger.info("Installing Google Cloud SDK...")
        
        # Download and install gcloud
        install_script = """
        export CLOUDSDK_CORE_DISABLE_PROMPTS=1
        curl https://sdk.cloud.google.com | bash
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            f.write(install_script)
            script_path = f.name
        
        try:
            subprocess.run(['bash', script_path], check=True)
            logger.info("Google Cloud SDK installed successfully")
        finally:
            os.unlink(script_path)
    
    def authenticate_with_gcloud(self) -> bool:
        """Authenticate using gcloud CLI"""
        logger.info("Setting up Google Cloud authentication...")
        
        try:
            # Check if already authenticated
            result = subprocess.run(['gcloud', 'auth', 'list'], capture_output=True, text=True)
            if result.returncode == 0 and 'ACTIVE' in result.stdout:
                logger.info("Already authenticated with gcloud")
                return True
            
            # Authenticate
            logger.info("Opening browser for Google authentication...")
            subprocess.run(['gcloud', 'auth', 'login', '--update-adc'], check=True)
            
            # Set project (optional)
            logger.info("Setting up Google Cloud project...")
            subprocess.run(['gcloud', 'config', 'set', 'project', 'your-project-id'], check=True)
            
            # Enable Gemini API
            logger.info("Enabling Gemini API...")
            subprocess.run(['gcloud', 'services', 'enable', 'generativelanguage.googleapis.com'], check=True)
            
            logger.info("Google Cloud authentication completed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    def setup_service_account(self) -> Optional[str]:
        """Set up a service account for programmatic access"""
        logger.info("Setting up service account...")
        
        try:
            # Create service account
            service_account_name = f"xnai-gemini-{int(time.time())}"
            display_name = "XNAi Gemini Service Account"
            
            # Create service account
            subprocess.run([
                'gcloud', 'iam', 'service-accounts', 'create', service_account_name,
                '--display-name', display_name
            ], check=True)
            
            # Grant necessary permissions
            project_id = subprocess.run(['gcloud', 'config', 'get-value', 'project'], 
                                      capture_output=True, text=True).stdout.strip()
            
            # Grant AI Platform permissions
            subprocess.run([
                'gcloud', 'projects', 'add-iam-policy-binding', project_id,
                '--member', f'serviceAccount:{service_account_name}@{project_id}.iam.gserviceaccount.com',
                '--role', 'roles/aiplatform.user'
            ], check=True)
            
            # Grant Generative Language API permissions
            subprocess.run([
                'gcloud', 'projects', 'add-iam-policy-binding', project_id,
                '--member', f'serviceAccount:{service_account_name}@{project_id}.iam.gserviceaccount.com',
                '--role', 'roles/generativelanguage.user'
            ], check=True)
            
            # Create key file
            key_file = self.config_dir / f"{service_account_name}.json"
            subprocess.run([
                'gcloud', 'iam', 'service-accounts', 'keys', 'create', str(key_file),
                '--iam-account', f'{service_account_name}@{project_id}.iam.gserviceaccount.com'
            ], check=True)
            
            logger.info(f"Service account created: {service_account_name}")
            logger.info(f"Key file saved to: {key_file}")
            
            return str(key_file)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Service account setup failed: {e}")
            return None
    
    def setup_oauth_credentials(self) -> bool:
        """Set up OAuth 2.0 credentials for user authentication"""
        logger.info("Setting up OAuth 2.0 credentials...")
        
        # This would typically involve:
        # 1. Creating OAuth credentials in Google Cloud Console
        # 2. Downloading client_secret.json
        # 3. Using Google Auth Library for OAuth flow
        
        logger.info("Please follow these steps to set up OAuth 2.0:")
        logger.info("1. Go to Google Cloud Console: https://console.cloud.google.com/")
        logger.info("2. Create a new project or select existing")
        logger.info("3. Enable Generative Language API")
        logger.info("4. Go to APIs & Services > Credentials")
        logger.info("5. Create OAuth 2.0 Client ID")
        logger.info("6. Download client_secret.json")
        logger.info("7. Save to: ~/.xnai/auth/client_secret.json")
        
        # Open browser to Google Cloud Console
        webbrowser.open("https://console.cloud.google.com/apis/credentials")
        
        return True
    
    def setup_api_key(self) -> Optional[str]:
        """Set up API key authentication"""
        logger.info("Setting up API key authentication...")
        
        logger.info("Please follow these steps to get your Gemini API key:")
        logger.info("1. Go to Google AI Studio: https://aistudio.google.com/")
        logger.info("2. Sign in with your Google account")
        logger.info("3. Navigate to 'API keys' section")
        logger.info("4. Create a new API key")
        logger.info("5. Copy the API key")
        
        # Open browser to AI Studio
        webbrowser.open("https://aistudio.google.com/")
        
        api_key = input("Enter your Gemini API key (or press Enter to skip): ").strip()
        
        if api_key:
            # Save API key securely
            api_key_file = self.config_dir / "gemini_api_key.txt"
            with open(api_key_file, 'w') as f:
                f.write(api_key)
            
            # Set environment variable
            os.environ['GEMINI_API_KEY'] = api_key
            
            logger.info(f"API key saved to: {api_key_file}")
            return api_key
        
        return None
    
    def configure_environment(self, auth_method: str, auth_data: Optional[str] = None):
        """Configure environment variables and system settings"""
        logger.info("Configuring environment variables...")
        
        if auth_method == "api_key" and auth_data:
            # Set API key environment variable
            env_file = Path.home() / ".bashrc"
            with open(env_file, 'a') as f:
                f.write(f'\nexport GEMINI_API_KEY="{auth_data}"\n')
            
            # Also set for current session
            os.environ['GEMINI_API_KEY'] = auth_data
            
        elif auth_method == "oauth":
            # Set OAuth environment variables
            env_file = Path.home() / ".bashrc"
            with open(env_file, 'a') as f:
                f.write('\nexport GEMINI_OAUTH_ENABLED="true"\n')
            
            os.environ['GEMINI_OAUTH_ENABLED'] = "true"
            
        elif auth_method == "service_account" and auth_data:
            # Set service account environment variable
            env_file = Path.home() / ".bashrc"
            with open(env_file, 'a') as f:
                f.write(f'\nexport GOOGLE_APPLICATION_CREDENTIALS="{auth_data}"\n')
            
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = auth_data
        
        logger.info("Environment configuration completed")
    
    def test_authentication(self, auth_method: str) -> bool:
        """Test the authentication method"""
        logger.info(f"Testing {auth_method} authentication...")
        
        try:
            if auth_method == "api_key":
                # Test with curl or direct API call
                import requests
                api_key = os.environ.get('GEMINI_API_KEY')
                if not api_key:
                    logger.error("API key not found in environment")
                    return False
                
                # Simple test request
                response = requests.get(
                    f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"
                )
                
                if response.status_code == 200:
                    logger.info("✅ API key authentication successful")
                    return True
                else:
                    logger.error(f"❌ API key authentication failed: {response.status_code}")
                    return False
                    
            elif auth_method in ["oauth", "service_account"]:
                # Test with gcloud
                result = subprocess.run(['gcloud', 'auth', 'list'], capture_output=True, text=True)
                if result.returncode == 0 and 'ACTIVE' in result.stdout:
                    logger.info("✅ OAuth authentication successful")
                    return True
                else:
                    logger.error("❌ OAuth authentication failed")
                    return False
                    
        except Exception as e:
            logger.error(f"Authentication test failed: {e}")
            return False
    
    def setup_gemini_cli(self):
        """Set up Gemini CLI with proper authentication"""
        logger.info("Configuring Gemini CLI...")
        
        # Update Gemini CLI configuration
        gemini_config = Path.home() / ".gemini" / "config.json"
        gemini_config.parent.mkdir(exist_ok=True)
        
        config = {
            "default_model": "gemini-3-pro-preview",
            "api_key_file": str(self.config_dir / "gemini_api_key.txt"),
            "oauth_enabled": True,
            "timeout": 600
        }
        
        with open(gemini_config, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info("Gemini CLI configuration updated")
    
    def update_omega_stack_config(self):
        """Update Omega Stack configuration files"""
        logger.info("Updating Omega Stack configuration...")
        
        # Update account registry
        account_registry = Path("config/cline-accounts.yaml")
        if account_registry.exists():
            with open(account_registry, 'r') as f:
                content = f.read()
            
            # Add or update Gemini account
            gemini_account = """
  - id: "gemini_oauth_01"
    name: "Gemini OAuth Account"
    provider: "gemini"
    quota_remaining: 1000000
    quota_limit: 1000000
    models_preferred: ["gemini-3-pro-preview", "gemini-3-flash-preview"]
    priority: 1
    auth_method: "oauth"
    rate_limit_config:
      max_retries: 3
      backoff_factor: 2
      max_backoff: 3600
"""
            
            if "gemini_oauth_01" not in content:
                # Add to accounts section
                if "accounts:" in content:
                    content = content.replace("accounts:", f"accounts:{gemini_account}")
                
                with open(account_registry, 'w') as f:
                    f.write(content)
                
                logger.info("Omega Stack account registry updated")
        
        # Update environment configuration
        env_config = Path("config/.env")
        env_config.parent.mkdir(exist_ok=True)
        
        env_content = """# Gemini Authentication Configuration
# Choose one of the following authentication methods:

# Method 1: API Key (if available)
# GEMINI_API_KEY=your-api-key-here

# Method 2: OAuth (recommended for region restrictions)
GEMINI_OAUTH_ENABLED=true

# Method 3: Service Account (for programmatic access)
# GOOGLE_APPLICATION_CREDENTIALS=~/.xnai/auth/your-service-account.json

# Gemini CLI Configuration
GEMINI_DEFAULT_MODEL=gemini-3-pro-preview
GEMINI_RATE_LIMIT=20
GEMINI_TIMEOUT=600
"""
        
        with open(env_config, 'w') as f:
            f.write(env_content)
        
        logger.info("Environment configuration updated")
    
    def run_complete_setup(self):
        """Run complete authentication setup"""
        logger.info("=== GEMINI AUTHENTICATION SETUP ===")
        
        # Check prerequisites
        if not self.check_gcloud_installed():
            logger.info("Google Cloud SDK not found. Installing...")
            self.install_gcloud()
        
        # Choose authentication method
        print("\nChoose authentication method:")
        print("1. API Key (requires Google AI Studio access)")
        print("2. OAuth 2.0 (recommended for region restrictions)")
        print("3. Service Account (for programmatic access)")
        
        choice = input("Enter choice (1-3): ").strip()
        
        auth_method = None
        auth_data = None
        
        if choice == "1":
            auth_method = "api_key"
            auth_data = self.setup_api_key()
            if not auth_data:
                logger.warning("API key setup skipped")
                return False
                
        elif choice == "2":
            auth_method = "oauth"
            if not self.authenticate_with_gcloud():
                logger.error("OAuth setup failed")
                return False
                
        elif choice == "3":
            auth_method = "service_account"
            auth_data = self.setup_service_account()
            if not auth_data:
                logger.error("Service account setup failed")
                return False
                
        else:
            logger.error("Invalid choice")
            return False
        
        # Configure environment
        self.configure_environment(auth_method, auth_data)
        
        # Test authentication
        if not self.test_authentication(auth_method):
            logger.error("Authentication test failed")
            return False
        
        # Update configurations
        self.setup_gemini_cli()
        self.update_omega_stack_config()
        
        # Save configuration
        config = {
            "auth_method": auth_method,
            "auth_data": auth_data,
            "last_updated": time.time()
        }
        self.save_auth_config(config)
        
        logger.info("✅ Gemini authentication setup completed successfully!")
        logger.info(f"Authentication method: {auth_method}")
        
        return True


def main():
    """Main function"""
    auth_manager = GeminiAuthManager()
    
    # Run complete setup
    success = auth_manager.run_complete_setup()
    
    if success:
        print("\n🎉 Gemini authentication setup completed!")
        print("You can now use Gemini models in your Omega Stack!")
        print("\nNext steps:")
        print("1. Restart your terminal to load new environment variables")
        print("2. Test with: gemini --version")
        print("3. Try: xnai account dispatch 'Hello Gemini!' --session test")
    else:
        print("\n❌ Setup failed. Please check the logs and try again.")
        print("Common issues:")
        print("- Region restrictions preventing API key access")
        print("- Google Cloud project not properly configured")
        print("- Missing permissions for Generative Language API")


if __name__ == "__main__":
    main()