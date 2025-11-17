# Deployment Checklist - Silicon Beach AI Jobs

## ✅ Pre-Deployment (Cost Safety)

### 1. **Snowflake Cost Controls** (DO THIS FIRST!)

Run in Snowflake UI:
```sql
-- Set to cheapest warehouse
ALTER WAREHOUSE COMPUTE_WH SET WAREHOUSE_SIZE = 'X-SMALL';

-- Auto-suspend after 1 minute
ALTER WAREHOUSE COMPUTE_WH SET AUTO_SUSPEND = 60;

-- Create $50 budget alert
CREATE RESOURCE MONITOR portfolio_budget WITH 
  CREDIT_QUOTA = 25 
  TRIGGERS ON 80 PERCENT DO NOTIFY ON 100 PERCENT DO SUSPEND;
ALTER WAREHOUSE COMPUTE_WH SET RESOURCE_MONITOR = portfolio_budget;
```

### 2. **Update ~/.config/secrets/global.env**

Add these lines:
```bash
# Snowflake
export SNOWFLAKE_ACCOUNT="vwyiycr-rpb51995"
export SNOWFLAKE_USER="ANIXLYNCH"
export SNOWFLAKE_PASSWORD="[YOUR_PASSWORD]"
export SNOWFLAKE_DATABASE="JOB_SEARCH"
export SNOWFLAKE_SCHEMA="MARTS"
export SNOWFLAKE_WAREHOUSE="COMPUTE_WH"
```

---

## 🚀 Streamlit Cloud Deployment

### 1. **GitHub** ✅ DONE
- Branch: `clean-deploy`
- URL: https://github.com/anix-lynch/silicon-beach-ai-jobs/tree/clean-deploy

### 2. **Streamlit Cloud Settings**

Go to: https://share.streamlit.io/

**Deploy new app:**
- Repository: `anix-lynch/silicon-beach-ai-jobs`
- Branch: `clean-deploy`
- Main file: `app_snowflake_cortex.py`

**Add secrets** (in Streamlit Cloud → Settings → Secrets):
```toml
SNOWFLAKE_ACCOUNT = "vwyiycr-rpb51995"
SNOWFLAKE_USER = "ANIXLYNCH"
SNOWFLAKE_PASSWORD = "[YOUR_PASSWORD]"
SNOWFLAKE_DATABASE = "JOB_SEARCH"
SNOWFLAKE_SCHEMA = "MARTS"
SNOWFLAKE_WAREHOUSE = "COMPUTE_WH"

GOOGLE_MAPS_API_KEY = "[FROM global.env]"
```

---

## 💰 Cost Estimate

**For portfolio demo (1 month):**
- Warehouse runtime: 5 hours × $4 = $20
- Cortex AI queries: 500 × $0.002 = $1
- Storage: < 1GB = $0
- **TOTAL: ~$21** (you have $400 credit!)

---

## 📊 Monitoring (Check Daily)

### Snowflake UI:
1. **Admin** → **Cost Management** → **Budgets**
2. Check credit usage (should be < $1/day for demo)

### SQL Query:
```sql
SELECT SUM(CREDITS_USED) as total_credits
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE START_TIME >= DATEADD(day, -1, CURRENT_TIMESTAMP());
```

---

## 🎯 What You're Showcasing

**For Recruiters:**
- ✅ Snowflake Cortex AI (LLM integration)
- ✅ Vector embeddings for job matching
- ✅ Real-time transit data (Google Maps API)
- ✅ Streamlit dashboard (production-ready)
- ✅ Cost optimization (X-SMALL warehouse, auto-suspend)
- ✅ Secure credential management (env vars)

**ATS Keywords:**
Snowflake, Cortex AI, LLM, Vector Search, Embeddings, Streamlit, Python, SQL, API Integration, Cost Optimization, Cloud Data Warehouse

---

## 🛑 Emergency Stop

If costs spike:
```sql
ALTER WAREHOUSE COMPUTE_WH SUSPEND;
```

Or switch to free DuckDB version:
- Change Streamlit main file to: `app_duckdb.py`
- 100% free, no credits needed

---

**Ready to deploy!** 🚀


