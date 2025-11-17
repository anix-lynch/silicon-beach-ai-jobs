# 🏔️ SNOWFLAKE CORTEX + SNOWPARK SPEEDRUN GUIDE

**Goal:** Add AI/ML layers to Silicon Beach job search in 2-3 hours
**Budget:** ~$10-15 total cost
**Result:** Portfolio-ready Snowflake Cortex + Vector Search demo

---

## 🚀 EXECUTION PLAN (2-3 hours)

### ⏰ HOUR 1: Set Up Cortex SQL (30-45 min)

**Step 1: Open Snowflake Web UI**
- Go to: https://app.snowflake.com/
- Login with your account: `vwyiycr-rpb51995`

**Step 2: Run Cost Protection First!**
```sql
-- Copy from snowflake/cortex_setup.sql lines 1-30
-- This sets XS warehouse + 1-min auto-suspend
```

**Step 3: Create AI Views**
```sql
-- Run STEP 2 from cortex_setup.sql
-- Creates MARTS.JOBS_AI_ENRICHED view with Cortex functions
-- Test with: SELECT * FROM MARTS.JOBS_AI_ENRICHED LIMIT 5;
```

**Step 4: Create Vector Search**
```sql
-- Run STEP 3 from cortex_setup.sql  
-- Creates MARTS.JOB_SIMILARITY view
-- Test with: SELECT * FROM MARTS.JOB_SIMILARITY LIMIT 10;
```

**Step 5: Create Recommendations**
```sql
-- Run STEP 4 from cortex_setup.sql
-- Creates MARTS.JOB_RECOMMENDATIONS view
```

**✅ Checkpoint:** You should have 3 new views in MARTS schema
**💰 Cost so far:** ~$3-5

---

### ⏰ HOUR 2: Test Streamlit App (30-45 min)

**Step 1: Install Dependencies**
```bash
cd /Users/anixlynch/dev/5miles-job-search

# Activate venv
source venv/bin/activate

# Install snowpark if needed
pip install snowflake-snowpark-python
```

**Step 2: Run Cortex-Powered App**
```bash
streamlit run app_snowflake_cortex.py
```

**Step 3: Test All Features**
- ✅ Tab 1: Job Map (basic functionality)
- ✅ Tab 2: AI Insights (Cortex summaries, skill extraction)
- ✅ Tab 3: Semantic Search (vector similarity)
- ✅ Tab 4: Analytics (AI recommendations)

**✅ Checkpoint:** All 4 tabs working with Cortex features
**💰 Cost so far:** ~$5-8

---

### ⏰ HOUR 3: Record Demo + Export (45-60 min)

**Step 1: Record GIF (15 min)**
Use CleanShot or similar to capture:
1. Snowflake Web UI showing CORTEX functions in SQL
2. Streamlit app Tab 2 (AI Insights)
3. Streamlit app Tab 3 (Semantic Search)
4. Show cost dashboard (prove you spent <$15!)

**Step 2: Take Screenshots (10 min)**
- Snowflake console with your MARTS.JOBS_AI_ENRICHED view
- SQL query with SNOWFLAKE.CORTEX.COMPLETE() 
- Streamlit app showing AI summaries
- Cost monitoring query results

**Step 3: Export to DuckDB (15 min)**
```bash
# Run migration script
python migrate_to_duckdb.py

# This exports ALL data including AI-enriched fields
```

**Step 4: Suspend Warehouse (5 min)**
```sql
-- In Snowflake Web UI:
ALTER WAREHOUSE COMPUTE_WH SUSPEND;

-- Verify it's suspended:
SHOW WAREHOUSES;
```

**✅ Checkpoint:** You have GIF, screenshots, and DuckDB export
**💰 Final Cost:** ~$10-15 total

---

## 📋 VERIFICATION CHECKLIST

Before you retire Snowflake, verify you have:

- [ ] ✅ `cortex_setup.sql` - All SQL queries documented
- [ ] ✅ `app_snowflake_cortex.py` - Working Streamlit app
- [ ] ✅ Screenshots of Snowflake console with Cortex queries
- [ ] ✅ GIF of app running with AI features
- [ ] ✅ DuckDB export (`data/silicon_beach.duckdb`)
- [ ] ✅ Cost monitoring screenshot showing <$15 spend
- [ ] ✅ Warehouse suspended

---

## 🎯 WHAT YOU'LL HAVE

### Portfolio Assets:
1. **GitHub Repo** with BOTH versions:
   - `app_snowflake_cortex.py` (Cortex AI version)
   - `app_duckdb.py` (Forever-free version)

2. **Demo Materials:**
   - 5-min Loom video walking through architecture
   - GIF for gozeroshot.dev portfolio card
   - Screenshots for LinkedIn/resume

3. **Resume Bullets:**
```
• Architected ML-powered job matching platform on Snowflake with 
  Cortex AI for semantic search and automated skill extraction

• Implemented vector similarity search using SNOWFLAKE.CORTEX.SIMILARITY() 
  to intelligently recommend jobs based on semantic meaning

• Developed cost-optimized data pipeline processing 100+ job listings 
  with <$15 compute spend on $400 credit (96% cost savings)

• Engineered database abstraction layer enabling seamless migration 
  from Snowflake to DuckDB, demonstrating architectural flexibility
```

---

## 🎤 INTERVIEW TALKING POINTS

**Q: Tell me about a data engineering project you're proud of.**

**A:** "I built an AI-powered job matching platform on Snowflake with a 
$400 trial credit. Instead of just storing job data, I used Snowflake 
Cortex to add intelligence layers - automatic skill extraction, semantic 
search, and resume matching.

The interesting part was the architecture decision: I built it to work with 
BOTH Snowflake and DuckDB. This way, I could demo enterprise Cortex features 
during the trial, then migrate to DuckDB for permanent hosting.

I completed the full implementation in one weekend for under $15, leaving 
$385 for other experiments. This shows I can use enterprise tools effectively 
AND make fiscally responsible engineering decisions."

**Q: What's an example of your cost optimization skills?**

**A:** "For my Snowflake project, I optimized in several ways:
1. Used XS warehouse (smallest size)
2. Set 1-minute auto-suspend 
3. Limited all queries to 100 rows during development
4. Used mistral-7b (cheaper) instead of mistral-large where possible
5. Built speedrun strategy: implement in 3 hours, record, export, retire

Result: $10-15 spend vs. $400 budget. That's 96% cost savings while still 
getting full portfolio value. Same principle applies to production systems."

---

## 💰 COST BREAKDOWN

| Activity | Warehouse Time | LLM Calls | Cost |
|----------|----------------|-----------|------|
| SQL Setup | 30 min | 0 | $1 |
| Create Views | 30 min | 100 | $1 + $0.20 |
| Test Queries | 30 min | 50 | $1 + $0.10 |
| Streamlit Testing | 1 hour | 200 | $2 + $0.40 |
| Recording | 30 min | 0 | $1 |
| Export | 30 min | 0 | $1 |
| **TOTAL** | **3.5 hours** | **350** | **$10-15** |

**Remaining Credit:** $385-390 (for future projects!)

---

## 🔥 NEXT STEPS (After Retirement)

### Deploy Both Versions to Streamlit Cloud

**Version A: "Snowflake Demo" (Temp)**
- Deploy `app_snowflake_cortex.py`
- Use until $400 expires
- Screenshot for portfolio

**Version B: "DuckDB Forever" (Permanent)**
- Deploy `app_duckdb.py`
- Works forever (free!)
- Primary portfolio link

### Add to gozeroshot.dev

**Project Card:**
```
Title: Silicon Beach AI Job Matcher: Snowflake Cortex + Vector Search

Description: Production data warehouse on Snowflake with Cortex AI for 
semantic job matching and automated skill extraction. Showcases modern 
ML-powered data engineering with intelligent migration to DuckDB for 
cost optimization.

Badges: Snowflake, Cortex AI, Vector Search, Snowpark, DuckDB, Python, 
Streamlit, Google Maps API

Links:
- 🚀 Live Demo → DuckDB version
- 📹 Video → Loom demo with Snowflake Cortex
- 💻 Code → GitHub repo
```

---

## 🆘 TROUBLESHOOTING

### "CORTEX functions not available"
- Check your Snowflake edition (need Enterprise+)
- Verify region supports Cortex (most US regions do)
- Try `SELECT SNOWFLAKE.CORTEX.COMPLETE('mistral-7b', 'test');`

### "Warehouse suspended unexpectedly"
- This is GOOD! It means auto-suspend is working
- Click "Resume" when you need it
- Saves you money!

### "Query taking too long"
- Add `LIMIT 10` to your queries
- Check warehouse is running: `SHOW WAREHOUSES;`
- Consider using smaller dataset for initial tests

### "Cost higher than expected"
- Run cost monitoring query (Step 5 in cortex_setup.sql)
- Suspend warehouse: `ALTER WAREHOUSE COMPUTE_WH SUSPEND;`
- Check for runaway queries in History tab

---

## ✅ SUCCESS METRICS

You've succeeded when:
- ✅ All 3 Cortex views created and tested
- ✅ Streamlit app shows AI features working
- ✅ Total cost < $15
- ✅ GIF and screenshots captured
- ✅ DuckDB export completed
- ✅ Warehouse suspended
- ✅ Portfolio-ready materials prepared

**TIME TO BRAG:** You just built a production-grade ML-powered data 
platform on Snowflake for less than the cost of a pizza! 🍕🎉

---

**Created:** 2025-11-15
**Status:** Ready to execute
**Estimated Time:** 2-3 hours
**Estimated Cost:** $10-15

