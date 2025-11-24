# 🧹 Clean Repo Plan - DuckDB Only

**Problem:** Current repo has Snowflake traces, cache issues, and legacy code.

**Solution:** Create a fresh, clean repo with ONLY DuckDB support.

## Steps to Create Clean Repo

### 1. **Create New Repo**
```bash
# New clean repo
cd /Users/anixlynch/dev
mkdir silicon-beach-jobs-clean
cd silicon-beach-jobs-clean
git init
```

### 2. **Copy Only DuckDB Files**
```bash
# From old repo, copy only:
- app_duckdb.py (rename to app.py)
- data/silicon_beach.duckdb
- requirements.txt (remove snowflake packages)
- scripts/get_secret.py
- scripts/load_secrets.sh
- .cursorrules
```

### 3. **Clean Requirements**
```txt
streamlit>=1.28.0
folium>=0.14.0
streamlit-folium>=0.15.0
pandas>=2.0.0
duckdb>=0.9.0
```

### 4. **Remove All Snowflake References**
- No `app_snowflake.py`
- No `migrate_to_duckdb.py`
- No Snowflake docs
- No Snowflake secrets

### 5. **Simple Structure**
```
silicon-beach-jobs-clean/
├── app.py              # Main Streamlit app (DuckDB only)
├── data/
│   └── silicon_beach.duckdb
├── requirements.txt
├── scripts/
│   ├── get_secret.py
│   └── load_secrets.sh
├── .cursorrules
└── README.md
```

## Benefits

✅ **No Snowflake dependencies**
✅ **No cache conflicts**
✅ **Simpler codebase**
✅ **Faster deployment**
✅ **Easier to maintain**

## Quick Start

1. Create new repo on GitHub: `silicon-beach-jobs-clean`
2. Copy files above
3. Deploy to Streamlit Cloud with `app.py`
4. No secrets needed!

**Want me to create this clean repo now?**

