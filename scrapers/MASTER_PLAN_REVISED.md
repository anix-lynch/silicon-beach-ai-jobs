# 🎯 REVISED MASTER PLAN: YOUR Job + VC Map

## ✅ What You Just Realized
1. **OpenVC.app map HAS addresses** - we can extract them (save $5 Google Maps API!)
2. **Phase 3 should be FILTERED** - only jobs matching YOUR criteria, not all 3,352!

---

## 📋 NEW PHASED APPROACH

### **PHASE 1: VCs (50-70 firms within 1 hour)** 🟠
**Goal**: Get all LA VCs WITH addresses, filter by <60 min commute

**Sources**:
1. ✅ Papermark list (21 VCs) - DONE
2. OpenVC.app individual VC pages (has addresses in "Global HQ" field)
3. LA Business Journal PDF (has addresses)

**Action Plan**:
1. Scrape OpenVC profiles for ~50 LA VCs (each profile page has address)
2. Combine with Papermark data
3. Run through `validate_and_enrich.py` (Google Maps API for commute)
4. Keep only VCs <60 min transit
5. Load to DuckDB + Snowflake

**Cost**: ~$3 for 50 VCs (Google Maps Distance Matrix API)

---

### **PHASE 2: Enrich Existing Data**
**Goal**: Get full addresses for the 32 VCs you're finding manually

**Action**: You're handling this! Just give me the CSV when ready.

---

### **PHASE 3: Tech Jobs (YOUR Criteria Only!)** 🟢
**Goal**: 200-500 jobs that match YOUR profile within <60 min commute

**Your Criteria** (from original request):
- **Roles**: Data Engineer, AI Engineer, Data Analyst, BI Analyst
- **Tech Stack**:
  - Cloud: AWS, GCP
  - Data Warehouses: Snowflake, BigQuery
  - ETL: dbt, Dataflow, Airflow
  - Vector DBs: ElasticSearch, AlloyDB, Pinecone
  - RAG/Semantic Search experience
  - Light BI: Tableau, Looker, PowerBI
- **Work Mode**: Remote > Hybrid > On-site (within 5 miles or easy bus/bike)
- **Commute**: <60 min transit from Culver City

**Scraping Strategy**:

#### **Option A: Built In LA (Filtered Smart Scrape)** 
```
URL Pattern:
https://www.builtinla.com/jobs?page={N}&search=data+engineer

Filters to Apply:
✅ Job Title: "Data Engineer", "Data Analyst", "AI Engineer", "BI Analyst"
✅ Office Type: Remote, Hybrid (skip full on-site unless <5 miles)
✅ Location: Los Angeles County
✅ Tech Keywords: AWS, GCP, Snowflake, BigQuery, dbt, Python, SQL
```

**Scrape Plan**:
1. Use MCP Firecrawl to scrape BuiltInLA search results
2. Filter by job title (Data Eng/Analyst/AI Eng/BI)
3. Extract:
   - Company name
   - Job title
   - Job URL
   - Company address (from company page)
   - Remote/Hybrid/Onsite status
4. For each company: Check if they have open data roles
5. Run through Google Maps API (filter <60 min commute)
6. **Expected**: 200-500 matching jobs (vs 3,352 total)

#### **Option B: LinkedIn Jobs (Public Search)**
```
https://www.linkedin.com/jobs/search/?keywords=data%20engineer&location=Los%20Angeles&f_WT=2

Could scrape LinkedIn job search with Firecrawl (no login needed for job listings)
```

---

## 💰 TOTAL COST ESTIMATE

| Phase | Tool | Cost |
|-------|------|------|
| Phase 1: VCs | Google Maps API (50 VCs) | $3 |
| Phase 2: Manual | You're doing it! | $0 |
| Phase 3: Jobs | Firecrawl (FREE MCP) | $0 |
| Phase 3: Jobs | Google Maps API (500 companies) | $15 |
| **TOTAL** | | **$18** |

---

## 🎯 FINAL RESULT

**Your Interactive Map Will Have**:
- 🟠 **50-70 VCs** (orange pins) - all <60 min commute
- 🟢 **200-500 Data Jobs** (green pins) - all matching YOUR skills + <60 min commute

**NOT 3,352 random tech jobs!** 😎

---

## 🚀 NEXT STEPS

**Right now, you have 3 options:**

### Option 1: Let me scrape OpenVC profiles for addresses (save $ on Google Maps)
I'll scrape the individual VC profile pages from OpenVC, which DO have addresses listed.

### Option 2: Wait for you to finish the 32 VC addresses manually
Then we enrich + load them.

### Option 3: Start Phase 3 NOW - scrape BuiltInLA for ONLY data jobs matching your criteria
Filter smart, not scrape-all-3352!

**Which option do you want to do first?**

