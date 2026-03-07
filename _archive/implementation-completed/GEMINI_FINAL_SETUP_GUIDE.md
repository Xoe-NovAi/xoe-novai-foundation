# Gemini OAuth Final Setup Guide

## Current Status ✅

**What's Working:**
- ✅ Google Cloud SDK installed and configured
- ✅ OAuth authentication completed successfully
- ✅ You're logged in as `arcana.novai@gmail.com`
- ✅ Account registry updated with OAuth account
- ✅ Environment variables configured

**What's Needed:**
- ⚠️ Google Cloud project needs to be created
- ⚠️ Gemini API needs to be enabled

## Final Setup Steps

### Step 1: Create Google Cloud Project

You need to create a Google Cloud project in the Google Cloud Console:

1. **Open Google Cloud Console:**
   ```bash
   # This will open your browser
   xdg-open "https://console.cloud.google.com/"
   ```

2. **Create a New Project:**
   - Click the project dropdown (top-left)
   - Click "New Project"
   - Enter project name: `arcana-novai-gemini`
   - Click "Create"

3. **Note Your Project ID:**
   - After creation, note the Project ID (e.g., `arcana-novai-gemini-12345`)
   - You'll need this for the next step

### Step 2: Enable Gemini API

1. **In Google Cloud Console:**
   - Go to "APIs & Services" > "Library"
   - Search for "Generative Language API"
   - Click on "Generative Language API"
   - Click "Enable"

2. **Alternative via CLI:**
   ```bash
   # Replace PROJECT_ID with your actual project ID
   gcloud services enable generativelanguage.googleapis.com --project=PROJECT_ID
   ```

### Step 3: Update Project Configuration

```bash
# Set your actual project ID
gcloud config set project YOUR_PROJECT_ID

# Verify
gcloud config get-value project
```

### Step 4: Test Gemini Access

```bash
# Test with Omega Stack
xnai account dispatch "Hello Gemini! Test OAuth authentication" --session oauth_test

# Test with Gemini CLI
gemini --version
```

## Quick Commands

### If you know your project ID:
```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Enable API
gcloud services enable generativelanguage.googleapis.com

# Test
xnai account dispatch "Hello Gemini!" --session test
```

### If you need to find your project:
```bash
# List projects
gcloud projects list

# Set the first one (if you only have one)
gcloud config set project $(gcloud projects list --format="value(projectId)" | head -1)
```

## Verification

### Check Authentication Status:
```bash
# Check if authenticated
gcloud auth list

# Check project
gcloud config get-value project

# Check enabled APIs
gcloud services list --enabled | grep generative
```

### Test API Access:
```bash
# Test with curl
curl -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  "https://generativelanguage.googleapis.com/v1/models"
```

## Expected Results

After completing these steps, you should see:

```
✅ Google Cloud project: YOUR_PROJECT_ID
✅ OAuth authentication: Active
✅ Gemini API: Enabled
✅ Account registry: Updated
✅ Environment: Configured

🎉 Gemini OAuth authentication complete!

Test with: xnai account dispatch "Hello Gemini!" --session test
```

## Troubleshooting

### Project Not Found:
```bash
# List available projects
gcloud projects list

# Create new project if needed
gcloud projects create arcana-novai-gemini --name="Arcana Nova Gemini"
```

### API Not Enabled:
```bash
# Enable API
gcloud services enable generativelanguage.googleapis.com --project=YOUR_PROJECT_ID

# Verify
gcloud services list --enabled | grep generative
```

### Permission Issues:
- Ensure you're using the same Google account (`arcana.novai@gmail.com`)
- Check that the project is created under your account
- Verify billing is set up (required for Gemini API)

## Next Steps

Once setup is complete:

1. **Restart your terminal** to load environment variables
2. **Test with simple commands** first
3. **Use in Omega Stack** with `xnai account dispatch`
4. **Enjoy Gemini access** without region restrictions!

## Support

If you encounter issues:

1. **Check Google Cloud Console** for project and API status
2. **Verify OAuth authentication** with `gcloud auth list`
3. **Ensure project has billing** enabled
4. **Check account registry** in `config/cline-accounts.yaml`

The OAuth solution bypasses region restrictions and should provide reliable access to Gemini models through your Omega Stack system.