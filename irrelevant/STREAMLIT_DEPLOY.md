# 🚀 Streamlit Cloud Deployment Guide

## Quick Deploy Steps

### 1. **Verify Code is Secure** ✅

All hardcoded credentials have been removed. Code now uses environment variables.

### 2. **Push to GitHub**

```bash
cd /Users/anixlynch/dev/5miles-job-search

# Check what branch you're on
git branch

# If on clean-deploy branch, you're good
# Otherwise, create/switch to clean-deploy
git checkout -b clean-deploy

# Add all changes (except .env)
git add .
git commit -m "Security fix: Remove hardcoded credentials, use env vars"

# Push to GitHub
git push origin clean-deploy
```

### 3. **Deploy on Streamlit Cloud**

1. Go to: https://share.streamlit.io/
2. Click **"New app"** (or edit existing app)
3. Fill in:
   - **Repository:** `anix-lynch/silicon-beach-ai-jobs`
   - **Branch:** `clean-deploy`
   - **Main file:** `app_duckdb.py` ⬅️ **Use DuckDB (no Snowflake needed!)**
   - **App URL:** (auto-generated)

4. Click **"Deploy"**

### 4. **Add Secrets** (OPTIONAL - Only if using Snowflake)

After deployment, go to **Settings → Secrets** and add:

```toml
# Snowflake Configuration
SNOWFLAKE_ACCOUNT = "TIQGFZV-GRB26326"
SNOWFLAKE_USER = "ALYNCH"
SNOWFLAKE_PASSWORD = "[YOUR_NEW_PASSWORD]"  # ⚠️ Use NEW password after rotation!
SNOWFLAKE_DATABASE = "JOB_SEARCH"
SNOWFLAKE_SCHEMA = "MARTS"
SNOWFLAKE_WAREHOUSE = "COMPUTE_WH"

# Google Maps API
GOOGLE_MAPS_API_KEY = "[YOUR_API_KEY]"

# Optional APIs
HUNTER_API_KEY = "[YOUR_API_KEY]"
PERPLEXITY_API_KEY = "[YOUR_API_KEY]"
```

**⚠️ IMPORTANT:** Use your **NEW** Snowflake password (after rotation from security leak).

### 5. **Restart App**

After adding secrets, click **"Restart app"** in Streamlit Cloud.

---

## 🎯 Which App File to Deploy?

### Option A: `app_snowflake_cortex.py` (Recommended)
- **Features:** Full Snowflake Cortex AI + Vector Search
- **Cost:** Uses Snowflake credits ($400 trial)
- **Best for:** Showcasing ML/AI capabilities

### Option B: `app_snowflake.py`
- **Features:** Basic Snowflake connection
- **Cost:** Uses Snowflake credits
- **Best for:** Simple data warehouse demo

### Option C: `app_duckdb.py` (Free Forever)
- **Features:** Local DuckDB, no cloud costs
- **Cost:** $0 (runs locally in Streamlit Cloud)
- **Best for:** Long-term demo after Snowflake trial expires

### Option D: `app.py` or `main.py`
- **Features:** Fallback mode (tries Snowflake, falls back to DuckDB)
- **Cost:** Variable
- **Best for:** Production with graceful degradation

---

## 🔍 Troubleshooting

### App Won't Start

**Error:** "SNOWFLAKE_PASSWORD environment variable is required"

**Fix:** Add secrets in Streamlit Cloud Settings → Secrets

### Connection Failed

**Error:** "Failed to connect to Snowflake"

**Possible causes:**
1. Wrong password (use NEW password after rotation)
2. Account/user incorrect
3. Warehouse not running (auto-suspend)
4. Network/firewall issue

**Fix:**
- Verify credentials in Streamlit Cloud secrets
- Check Snowflake account is active
- Try running warehouse manually in Snowflake UI

### High Costs

**Solution:** Switch to `app_duckdb.py` (free forever)

---

## 📊 Monitoring

### Check App Status
- Streamlit Cloud dashboard shows logs and errors
- Check "Manage app" → "Logs" for detailed errors

### Check Snowflake Usage
```sql
-- Run in Snowflake UI
SELECT SUM(CREDITS_USED) as total_credits
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE START_TIME >= DATEADD(day, -1, CURRENT_TIMESTAMP());
```

---

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub (`clean-deploy` branch)
- [ ] Streamlit Cloud app created
- [ ] Secrets added (with NEW Snowflake password)
- [ ] App restarted after adding secrets
- [ ] App loads successfully
- [ ] Snowflake connection works
- [ ] Cost monitoring set up

---

**Ready to deploy!** 🚀


