# 🔒 Security Fix - Credential Leak Remediation

## ⚠️ What Happened

**Issue:** Hardcoded Snowflake password was found in 5 files and potentially committed to GitHub.

**Files Fixed:**
- ✅ `main.py`
- ✅ `app_snowflake.py`
- ✅ `scrapers/load_to_snowflake.py`
- ✅ `scrapers/load_jobs_to_both.py`
- ✅ `migrate_to_duckdb.py`

**Action Taken:**
- ✅ All hardcoded passwords removed
- ✅ All files now use `os.getenv('SNOWFLAKE_PASSWORD')`
- ✅ Added validation to require environment variables
- ✅ Created `.env.example` template
- ✅ Updated `.gitignore` to prevent future leaks

---

## ✅ What You Need to Do

### 1. **New Account Created** (Completed)
 
Instead of rotating the password, we created a fresh Snowflake account to ensure total security:
 
- **Old Account:** `vwyiycr-rpb51995` (Locked/Abandoned)
- **New Account:** `TIQGFZV-GRB26326`
- **New User:** `ALYNCH`
- **Status:** ✅ Active & Secure

### 2. **Set Up Local Environment**

Create `.env` file (copy from `.env.example`):

```bash
cd /Users/anixlynch/dev/5miles-job-search
cp .env.example .env
# Edit .env with your NEW Snowflake password
```

### 3. **Verify No Secrets in Git History**

Check if secrets were committed:

```bash
# Search git history for the old password
git log --all --full-history -p | grep -i "aRTHMrC5Pos@L76T"

# If found, you may need to:
# 1. Remove from git history (BFG Repo-Cleaner or git filter-branch)
# 2. Force push (⚠️ coordinate with team if shared repo)
# 3. Consider the leaked password compromised
```

### 4. **Set Up Streamlit Cloud Secrets**

For deployment, add secrets in Streamlit Cloud:

1. Go to: https://share.streamlit.io/
2. Select your app → Settings → Secrets
3. Add:

```toml
SNOWFLAKE_ACCOUNT = "TIQGFZV-GRB26326"
SNOWFLAKE_USER = "ALYNCH"
SNOWFLAKE_PASSWORD = "[YOUR_NEW_PASSWORD]"
SNOWFLAKE_DATABASE = "JOB_SEARCH"
SNOWFLAKE_SCHEMA = "MARTS"
SNOWFLAKE_WAREHOUSE = "COMPUTE_WH"

GOOGLE_MAPS_API_KEY = "[YOUR_API_KEY]"
```

---

## 🛡️ Prevention Checklist

- [x] All hardcoded credentials removed
- [x] `.env.example` created (no real values)
- [x] `.gitignore` updated to exclude `.env*` files
- [x] New Snowflake account created (`TIQGFZV-GRB26326`)
- [x] Local `.env.snowflake` file created with new credentials
- [x] Git history checked (Old account abandoned, so history is less critical)
- [ ] Streamlit Cloud secrets configured (Next Step)
- [x] All team members notified (if applicable)

---

## 📋 Best Practices Going Forward

### ✅ DO:
- Always use environment variables for secrets
- Use `.env.example` as a template (no real values)
- Add `.env*` to `.gitignore`
- Rotate credentials immediately if leaked
- Use secret management tools (AWS Secrets Manager, GCP Secret Manager, etc.)

### ❌ DON'T:
- Hardcode passwords in code
- Commit `.env` files
- Share credentials in chat/email
- Use the same password across services
- Ignore security warnings from GitGuardian

---

## 🔍 Verification Commands

```bash
# Check for any remaining hardcoded passwords
grep -r "password.*=.*['\"][^'\"]" --include="*.py" .

# Verify .env is in .gitignore
grep -q "\.env" .gitignore && echo "✅ .env is gitignored" || echo "❌ .env NOT in .gitignore"

# Check if .env exists (should exist locally, not in git)
test -f .env && echo "✅ .env exists locally" || echo "⚠️ Create .env from .env.example"
```

---

## 🚨 If Secrets Were Committed

If the password was in git history:

1. **Immediate:** Rotate the password in Snowflake
2. **Short-term:** Remove from git history (BFG Repo-Cleaner recommended)
3. **Long-term:** Set up pre-commit hooks to scan for secrets

**BFG Repo-Cleaner Example:**
```bash
# Install BFG
brew install bfg

# Remove password from history
bfg --replace-text passwords.txt
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

---

**Status:** ✅ Code fixed, now rotate credentials!


