# 🔐 Google Cloud Authentication - THE DEFINITIVE GUIDE

**Last Updated:** November 11, 2025  
**Status:** ✅ WORKING  
**Project:** Job Search + VC Mapping (5miles-job-search)

---

## 📋 Quick Reference

### Your Current Working Setup

```bash
# Account
alynch@gozeroshot.dev

# Project
maps-platform-20251011-140544

# Working API Key (with Distance Matrix, Directions, Geocoding)
REDACTED_MAPS_KEY

# Key Location
~/.config/secrets/global.env
export GOOGLE_MAPS_API_KEY="REDACTED_MAPS_KEY"

# Enabled APIs
✅ distance-matrix-backend.googleapis.com
✅ directions-backend.googleapis.com  
✅ geocoding-backend.googleapis.com
✅ maps-backend.googleapis.com
```

---

## 🚨 The #1 Rule

**ALWAYS USE BROWSER POPUP FOR AUTH - NEVER PASSWORD IN TERMINAL**

```bash
# ✅ CORRECT - Opens browser
gcloud auth login --update-adc

# ❌ WRONG - Will fail in AI/non-interactive shells
gcloud auth login --no-launch-browser
```

---

## 🔧 When Things Break

### Problem: "REQUEST_DENIED" or "This API key is not authorized"

**Root Cause:** Wrong API key in environment

**Fix:**
```bash
# 1. Check which key you're using
source ~/.config/secrets/global.env
echo $GOOGLE_MAPS_API_KEY

# 2. Get the correct key
gcloud alpha services api-keys list --project=maps-platform-20251011-140544

# 3. Look for "Job Search Distance Matrix" key
# Should have these restrictions:
#   - distance-matrix-backend.googleapis.com
#   - directions-backend.googleapis.com
#   - geocoding-backend.googleapis.com

# 4. Get the key string
gcloud alpha services api-keys get-key-string \
  projects/835005185815/locations/global/keys/fdf37373-a79c-4edd-af98-5cc5db38cd17 \
  --project=maps-platform-20251011-140544

# 5. Update your secrets file
# Open ~/.config/secrets/global.env
# Replace line 13 with the correct key
```

### Problem: "Reauthentication required" or stale tokens

**Fix:**
```bash
gcloud auth login --update-adc
```

This solves 80% of auth problems.

### Problem: Can't enable API in browser console

**Why:** Permission issues with OAuth consent screen

**Fix:** Use CLI instead
```bash
# 1. Find correct API name
gcloud services list --available | grep -i "distance"

# 2. Enable it
gcloud services enable distance-matrix-backend.googleapis.com \
  --project=maps-platform-20251011-140544
```

---

## 🎯 Enabling a New API (Step-by-Step)

### Example: Adding BigQuery API

```bash
# Step 1: Fresh auth
gcloud auth login --update-adc

# Step 2: Set project
gcloud config set project maps-platform-20251011-140544

# Step 3: Find exact API service name
gcloud services list --available | grep -i "bigquery"
# Output: bigquery.googleapis.com

# Step 4: Enable it
gcloud services enable bigquery.googleapis.com --project=maps-platform-20251011-140544

# Step 5: Wait 1-2 minutes for propagation

# Step 6: Update API key to allow BigQuery (if using API key)
gcloud alpha services api-keys update \
  projects/835005185815/locations/global/keys/fdf37373-a79c-4edd-af98-5cc5db38cd17 \
  --add-api-target=service=bigquery.googleapis.com \
  --project=maps-platform-20251011-140544
```

---

## 🔑 API Key Management

### When to Create a NEW Key vs Update Existing

**Create NEW when:**
- Old key has complex restrictions you don't understand
- You want to test without breaking existing code
- Starting a fresh project

**Update EXISTING when:**
- You know exactly what APIs are needed
- Key is already in use across codebase
- Just adding 1-2 APIs to existing set

### How to Create New API Key

```bash
# Create unrestricted key first
gcloud alpha services api-keys create \
  --display-name="My Project API Key" \
  --project=maps-platform-20251011-140544

# Output will show keyString: AIzaSy...
# Copy this immediately!

# Then add restrictions
gcloud alpha services api-keys update \
  projects/835005185815/locations/global/keys/YOUR-KEY-UID \
  --clear-restrictions \
  --add-api-target=service=distance-matrix-backend.googleapis.com \
  --add-api-target=service=directions-backend.googleapis.com \
  --project=maps-platform-20251011-140544
```

### How to Update Existing Key

```bash
# Add an API to existing key
gcloud alpha services api-keys update \
  projects/835005185815/locations/global/keys/fdf37373-a79c-4edd-af98-5cc5db38cd17 \
  --add-api-target=service=NEW-API.googleapis.com \
  --project=maps-platform-20251011-140544
```

---

## 🎓 Understanding Google Auth Types

| Type | Command | What It's For | Where Credentials Live |
|------|---------|---------------|------------------------|
| **User Auth** | `gcloud auth login` | Running `gcloud` CLI commands | `~/.config/gcloud/credentials.db` |
| **Application Default** | `gcloud auth application-default login` | Python/Node SDKs (google-cloud libraries) | `~/.config/gcloud/application_default_credentials.json` |
| **API Keys** | Created in console or CLI | Public REST APIs (Maps, Geocoding) | Wherever you store them |
| **Service Account** | JSON key file | Production servers, CI/CD | Wherever you put the JSON |

**For this project:**
- ✅ User Auth: For running `gcloud` commands
- ✅ API Keys: For Google Maps API in Python scripts
- ❌ Application Default: Not needed (we use API keys, not google-cloud-python SDK)

---

## 💰 Cost Tracking

### Your Credits
- **Google Cloud:** $300 free credit
- **Expires:** Check at https://console.cloud.google.com/billing

### Current Usage (Job Search Project)
```
Distance Matrix API: 24 calls × $0.005 = $0.12
Directions API: 24 calls × $0.005 = $0.12
Total spent: ~$0.24

Remaining: $299.76 🎉
```

### Check Your Usage
```bash
# View credit usage
gcloud billing accounts list

# View API usage (last 7 days)
# Go to: https://console.cloud.google.com/billing/projects/maps-platform-20251011-140544
```

---

## 🧪 Testing API Keys

### Quick Test: Distance Matrix API

```bash
cd /Users/anixlynch/dev/5miles-job-search
source ~/.config/secrets/global.env

python3 << 'EOF'
import requests
import os

api_key = os.getenv('GOOGLE_MAPS_API_KEY')
print(f"Testing key: {api_key[:20]}...")

url = "https://maps.googleapis.com/maps/api/directions/json"
params = {
    'origin': 'YOUR_HOME_ADDRESS',
    'destination': '9696 Culver Blvd, Culver City, CA 90232',
    'mode': 'transit',
    'key': api_key
}

resp = requests.get(url, params=params)
data = resp.json()

if data['status'] == 'OK':
    print("✅ SUCCESS! API key works!")
    route = data['routes'][0]['legs'][0]
    print(f"Duration: {route['duration']['text']}")
else:
    print(f"❌ Error: {data['status']}")
    print(f"Message: {data.get('error_message', 'No error message')}")
EOF
```

---

## 🚫 Common Gotchas

### 1. **Environment Variable Override**

```bash
# This OVERRIDES everything else!
echo $GOOGLE_APPLICATION_CREDENTIALS

# If it shows a path, unset it:
unset GOOGLE_APPLICATION_CREDENTIALS
```

### 2. **Multiple Google Accounts**

```bash
# See who's logged in
gcloud auth list

# Switch accounts
gcloud config set account alynch@gozeroshot.dev
```

### 3. **API Service Names Are Not Obvious**

Don't guess! Use grep:

```bash
# ❌ WRONG
gcloud services enable distancematrix.googleapis.com

# ✅ CORRECT - Found via grep
gcloud services list --available | grep -i "distance"
# → distance-matrix-backend.googleapis.com
```

### 4. **Propagation Delay**

After enabling an API or creating a key:
- **Wait 1-2 minutes** before testing
- If it fails immediately, try again in 60 seconds

---

## 📚 Common Commands

### Check Status
```bash
# Who am I?
gcloud config get-value account

# What project?
gcloud config get-value project

# What's enabled?
gcloud services list --enabled

# List my API keys
gcloud alpha services api-keys list --project=maps-platform-20251011-140544
```

### Switch Projects
```bash
gcloud config set project maps-platform-20251011-140544
```

### Nuclear Option (Fresh Start)
```bash
# Clear everything
gcloud auth revoke --all
rm -rf ~/.config/gcloud/

# Start over
gcloud auth login --update-adc
gcloud config set project maps-platform-20251011-140544
```

---

## 🎯 For Other AI Assistants

If you're an AI reading this guide, here's the pattern:

### User says: "Enable [API_NAME]"

```bash
# 1. Auth first
gcloud auth login --update-adc

# 2. Set project
gcloud config set project maps-platform-20251011-140544

# 3. Find exact name
gcloud services list --available | grep -i "API_NAME"

# 4. Enable it (use exact name from step 3)
gcloud services enable EXACT-NAME.googleapis.com --project=maps-platform-20251011-140544

# 5. Wait 1-2 min, then test
```

### User says: "Google Maps API not working"

```bash
# Check if they're using the right key
source ~/.config/secrets/global.env
echo "Key: ${GOOGLE_MAPS_API_KEY:0:20}..."

# Should be: REDACTED_MAPS_KEY_PREFIX...

# If wrong, show them how to fix ~/.config/secrets/global.env line 13
```

---

## ✅ Verification Checklist

Before starting any Google Cloud API work:

- [ ] `gcloud auth login --update-adc` completed
- [ ] `gcloud config get-value project` shows correct project
- [ ] API is enabled: `gcloud services list --enabled | grep API_NAME`
- [ ] API key is in `~/.config/secrets/global.env`
- [ ] API key has correct restrictions (check with `gcloud alpha services api-keys list`)
- [ ] Waited 1-2 minutes after any changes

---

## 📖 Further Reading

- **Official gcloud docs:** https://cloud.google.com/sdk/gcloud/reference
- **Maps API pricing:** https://developers.google.com/maps/billing-and-pricing/pricing
- **API key best practices:** https://cloud.google.com/docs/authentication/api-keys

---

**Last Tested:** November 11, 2025  
**Status:** ✅ All APIs working  
**Test Command:** See "Testing API Keys" section above


