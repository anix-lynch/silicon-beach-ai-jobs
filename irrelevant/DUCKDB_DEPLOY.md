# 🦆 Deploy with DuckDB (No Snowflake Needed!)

**Perfect solution:** Use `app_duckdb.py` - free forever, no credentials needed!

## Why DuckDB?

✅ **Free forever** - no cloud costs  
✅ **No credentials** - no password issues  
✅ **Fast** - in-memory analytics database  
✅ **Portfolio-ready** - works long-term  
✅ **Same features** - all functionality preserved

## Quick Deploy Steps

### 1. **Verify DuckDB File Has Data**

```bash
cd /Users/anixlynch/dev/5miles-job-search
python3 -c "
import duckdb
conn = duckdb.connect('data/silicon_beach.duckdb')
tables = conn.execute('SHOW TABLES').fetchall()
print('Tables:', tables)
for table in tables:
    count = conn.execute(f'SELECT COUNT(*) FROM {table[0]}').fetchone()[0]
    print(f'  {table[0]}: {count} rows')
conn.close()
"
```

### 2. **Deploy to Streamlit Cloud**

1. Go to: https://share.streamlit.io/
2. Click **"New app"** (or edit existing)
3. Settings:
   - **Repository:** `anix-lynch/silicon-beach-ai-jobs`
   - **Branch:** `clean-deploy`
   - **Main file:** `app_duckdb.py` ⬅️ **CHANGE THIS!**
   - **App URL:** (auto-generated)

4. **No secrets needed!** DuckDB uses local file.

5. **Important:** Make sure `data/silicon_beach.duckdb` is committed to Git (or use file upload)

### 3. **If DuckDB File is Missing Data**

If the database is empty, load data from CSV:

```bash
cd /Users/anixlynch/dev/5miles-job-search
python3 -c "
import duckdb
import pandas as pd

# Connect
conn = duckdb.connect('data/silicon_beach.duckdb')

# Load from CSV if needed
df = pd.read_csv('data/la_vcs_20251111_083756_enriched.csv')
conn.execute('CREATE TABLE IF NOT EXISTS jobs_cleaned AS SELECT * FROM df')

# Or use the migration script
# python3 migrate_to_duckdb.py

conn.close()
print('✅ Data loaded!')
"
```

### 4. **Update Portfolio Link**

Already updated! The portfolio now shows "DuckDB" instead of "Snowflake".

## File Structure

```
5miles-job-search/
├── app_duckdb.py          ← Use this for deployment
├── data/
│   └── silicon_beach.duckdb  ← Local database (no cloud!)
└── requirements.txt       ← Already has duckdb
```

## Benefits

- ✅ **No Snowflake password issues**
- ✅ **No monthly costs**
- ✅ **Works offline**
- ✅ **Fast queries**
- ✅ **Perfect for portfolio**

## Migration from Snowflake

If you had data in Snowflake, export it first:

```bash
# Run migration script (if you have Snowflake access)
python3 migrate_to_duckdb.py
```

Otherwise, just use the CSV files you already have!

## ✅ Deployment Checklist

- [ ] DuckDB file has data (`data/silicon_beach.duckdb`)
- [ ] Streamlit Cloud app uses `app_duckdb.py`
- [ ] No secrets needed in Streamlit Cloud
- [ ] App loads successfully
- [ ] Portfolio link updated

**Ready to deploy!** 🚀

