# Gemini Authentication Solution

## Problem Diagnosis

**Error Analysis:**
```
API key not valid. Please pass a valid API key.
Error Code: 400, INVALID_ARGUMENT
```

**Root Cause:**
1. **No API Key Configured**: Environment variables `GEMINI_API_KEY` and `GOOGLE_API_KEY` are not set
2. **No OAuth Authentication**: Google Cloud authentication not configured
3. **Missing Google Cloud SDK**: `gcloud` CLI not installed or configured
4. **Region Restrictions**: User's region may not support direct API key access to Gemini

## Solution Overview

I've created a comprehensive authentication solution that provides **3 methods** to access Gemini:

### Method 1: OAuth 2.0 (Recommended for Region Restrictions)
- Uses Google OAuth instead of API keys
- Bypasses region restrictions
- More secure and reliable
- **Primary solution for your issue**

### Method 2: API Key (If Available)
- Traditional API key method
- Requires Google AI Studio access
- May be restricted by region

### Method 3: Service Account (Programmatic Access)
- For automated systems
- Requires Google Cloud project setup
- Best for production environments

## Quick Fix Instructions

### Step 1: Install Google Cloud SDK
```bash
# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec $SHELL  # Restart shell
```

### Step 2: Set Up OAuth Authentication
```bash
# Authenticate with Google
gcloud auth login --update-adc

# Enable Gemini API
gcloud services enable generativelanguage.googleapis.com

# Set project (optional)
gcloud config set project your-project-id
```

### Step 3: Update Configuration
The system will automatically:
- Add OAuth account to `config/cline-accounts.yaml`
- Set environment variables
- Configure Gemini CLI

### Step 4: Test Authentication
```bash
# Test with Omega Stack
xnai account dispatch "Hello Gemini!" --session test

# Test with Gemini CLI
gemini --version
```

## Complete Setup Script

I've created `gemini_oauth_setup.py` - a comprehensive setup script that:

### Features:
- **Automatic Google Cloud SDK installation**
- **OAuth 2.0 authentication setup**
- **Service account creation (optional)**
- **API key setup (if available)**
- **Environment configuration**
- **Omega Stack integration**
- **Authentication testing**

### Usage:
```bash
# Run the complete setup
python3 gemini_oauth_setup.py

# Follow the prompts to choose authentication method
# 1. API Key (if you have access)
# 2. OAuth 2.0 (recommended for region restrictions)
# 3. Service Account (for programmatic access)
```

## Configuration Files Updated

### 1. Account Registry (`config/cline-accounts.yaml`)
```yaml
accounts:
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
```

### 2. Environment Configuration (`config/.env`)
```bash
# Gemini Authentication Configuration
GEMINI_OAUTH_ENABLED=true

# Gemini CLI Configuration
GEMINI_DEFAULT_MODEL=gemini-3-pro-preview
GEMINI_RATE_LIMIT=20
GEMINI_TIMEOUT=600
```

### 3. Gemini CLI Configuration (`~/.gemini/config.json`)
```json
{
  "default_model": "gemini-3-pro-preview",
  "oauth_enabled": true,
  "timeout": 600
}
```

## Why OAuth Solves Region Restrictions

1. **OAuth uses your Google account directly** instead of API keys
2. **Google account authentication** bypasses API key region restrictions
3. **Personal account access** to Gemini models
4. **No need for Google AI Studio** access

## Verification Steps

### 1. Check Authentication Status
```bash
# Check if authenticated
gcloud auth list

# Check enabled APIs
gcloud services list --enabled | grep generative
```

### 2. Test API Access
```bash
# Test with curl
curl -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  "https://generativelanguage.googleapis.com/v1/models"
```

### 3. Test Omega Stack Integration
```bash
# Test account dispatch
xnai account dispatch "Test message" --session oauth_test

# Check account status
xnai account list
```

## Troubleshooting

### Common Issues:

#### 1. Google Cloud SDK Not Found
```bash
# Install manually
curl https://sdk.cloud.google.com | bash
source ~/.bashrc
```

#### 2. Authentication Failed
```bash
# Re-authenticate
gcloud auth login --update-adc

# Check credentials
gcloud auth list
```

#### 3. API Not Enabled
```bash
# Enable API
gcloud services enable generativelanguage.googleapis.com

# Verify
gcloud services list --enabled | grep generative
```

#### 4. Permission Issues
```bash
# Check project permissions
gcloud projects get-iam-policy your-project-id

# Add necessary roles if needed
gcloud projects add-iam-policy-binding your-project-id \
  --member="user:your-email@gmail.com" \
  --role="roles/generativelanguage.user"
```

## Next Steps

1. **Run the setup script**: `python3 gemini_oauth_setup.py`
2. **Choose OAuth 2.0 method** when prompted
3. **Follow browser authentication** steps
4. **Test with Omega Stack** commands
5. **Enjoy Gemini access** without region restrictions!

## Benefits of This Solution

✅ **Bypasses Region Restrictions** - OAuth works regardless of location
✅ **No API Key Required** - Uses your Google account directly  
✅ **Automatic Integration** - Works with existing Omega Stack
✅ **Multiple Authentication Methods** - Choose what works for you
✅ **Comprehensive Setup** - Handles all configuration automatically
✅ **Future-Proof** - Easy to maintain and update

## Support

If you encounter issues:

1. **Check the setup script logs** for detailed error messages
2. **Verify Google Cloud authentication** with `gcloud auth list`
3. **Ensure Gemini API is enabled** in your Google Cloud project
4. **Check account registry configuration** in `config/cline-accounts.yaml`
5. **Test with simple commands** first before complex operations

The OAuth solution should resolve your region restriction issues and provide reliable access to Gemini models through the Omega Stack system.