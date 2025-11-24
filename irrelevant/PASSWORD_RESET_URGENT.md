# 🚨 URGENT: Snowflake Password Reset Required

**Date:** Today  
**Issue:** Snowflake disabled password sign-in due to compromised credentials  
**Account:** ITB97131  
**User:** ANIXLYNCH

## Immediate Actions Required

### 1. **Contact Account Admin** (FIRST STEP)
- Account admin must re-enable password sign-in for your account
- If you ARE the admin, follow Snowflake support instructions

### 2. **Reset Password in Snowflake**
1. Log into Snowflake: https://app.snowflake.com/
2. Go to: User Profile → Change Password
3. Set a **strong new password**

### 3. **Update All Secret Locations**

After resetting, update password in these locations:

#### A. Local Secret Files (Check all):
```bash
# Check these locations:
~/.config/secrets/global.env
~/.secrets/global.env
/Users/anixlynch/dev/5miles-job-search/.env
/Users/anixlynch/dev/5miles-job-search/.env.local
```

Update the line:
```
SNOWFLAKE_PASSWORD=your_new_password_here
```

#### B. Streamlit Cloud (if deployed):
1. Go to: https://share.streamlit.io/
2. Select your app
3. Settings → Secrets
4. Update `SNOWFLAKE_PASSWORD` value
5. Restart app

#### C. Any Other Deployment Platforms:
- Vercel (if used)
- Other cloud services
- CI/CD secrets

### 4. **Verify Connection**
```bash
cd /Users/anixlynch/dev/5miles-job-search
python3 -c "
from scripts.get_secret import get_secret
import snowflake.connector

config = {
    'account': get_secret('SNOWFLAKE_ACCOUNT', 'vwyiycr-rpb51995'),
    'user': get_secret('SNOWFLAKE_USER', 'ANIXLYNCH'),
    'password': get_secret('SNOWFLAKE_PASSWORD'),
    'database': get_secret('SNOWFLAKE_DATABASE', 'JOB_SEARCH'),
    'warehouse': get_secret('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
}

try:
    conn = snowflake.connector.connect(**config)
    print('✅ Connection successful!')
    conn.close()
except Exception as e:
    print(f'❌ Connection failed: {e}')
"
```

## Files That Use SNOWFLAKE_PASSWORD

All these files use `get_secret('SNOWFLAKE_PASSWORD')` - just update your secret files:
- `app_snowflake.py`
- `app_snowflake_cortex.py`
- `main.py`
- `migrate_to_duckdb.py`
- `scrapers/load_to_snowflake.py`
- `scrapers/load_jobs_to_both.py`

## ✅ Checklist

- [ ] Account admin re-enabled password sign-in
- [ ] Password reset in Snowflake
- [ ] Updated `~/.config/secrets/global.env` (or local `.env`)
- [ ] Updated Streamlit Cloud secrets (if deployed)
- [ ] Tested connection with new password
- [ ] All apps working with new password

## Security Notes

- ✅ Code already uses `get_secret()` - no hardcoded passwords
- ✅ Password stored in secret files (not in code)
- ⚠️ Make sure `.env` files are in `.gitignore`
- ⚠️ Never commit passwords to Git

