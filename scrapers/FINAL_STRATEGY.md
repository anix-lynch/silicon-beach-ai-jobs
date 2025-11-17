# 🎯 FINAL EXECUTION STRATEGY

## ✅ What We've Learned
1. **OpenVC scraping works** - but it's slow (38 VCs = ~15 min)
2. **Some VCs aren't in LA** (e.g., Fifth Wall HQ is in NY)
3. **Your $300 Google Maps credit** covers everything we need

---

## 🚀 OPTIMIZED 3-PHASE PLAN

### **PHASE 1: VC Data Collection** 🟠
**Option A (Recommended): Use what you have + selective scraping**
- ✅ 21 VCs from Papermark (you're manually finding addresses)
- ✅ 5 VCs from OpenVC (scraped above)
- ⏳ Top 10-15 more VCs from OpenVC (high-value targets only)
- **Total: ~40 VCs**
- **Cost**: $0 (scraping) + $2 (Google Maps for 40 VCs)

**Option B: Scrape all 38 from OpenVC**
- Takes ~20 minutes
- Some won't be in LA (waste of API calls)
- **Cost**: $0 (scraping) + $3 (Google Maps for 38 VCs)

---

### **PHASE 2: Enrich & Filter VCs** 
Once we have the 40 VCs with addresses:

```bash
# Run validation & enrichment
cd /Users/anixlynch/dev/5miles-job-search/scrapers
python validate_and_enrich.py ../data/la_vcs_combined.csv

# This will:
# - Calculate commute from Culver City
# - Filter to <60 min transit
# - Add transit routes, closest metro
# - Expected: 25-30 VCs within 1 hour
```

**Cost**: $2 Google Maps API (40 VCs × $0.05)

---

### **PHASE 3: Data Jobs (THE BIG ONE)** 🟢
**Goal**: 200-500 jobs matching YOUR criteria

**Scraping Strategy**:

#### Step 1: Use Built In LA with FILTERS
```
URLs to scrape:
1. https://www.builtinla.com/jobs?search=data+engineer&location=Los+Angeles
2. https://www.builtinla.com/jobs?search=data+analyst&location=Los+Angeles
3. https://www.builtinla.com/jobs?search=AI+engineer&location=Los+Angeles
4. https://www.builtinla.com/jobs?search=BI+analyst&location=Los+Angeles

Apply filters:
✅ Remote or Hybrid preferred
✅ Tech keywords: AWS, GCP, Snowflake, BigQuery, dbt, Python
```

#### Step 2: Extract Company Data
For each job:
- Company name
- Job title
- Office location/address
- Remote/Hybrid status
- Job URL
- Tech stack (from description)

#### Step 3: Deduplicate by Company
- 500 jobs → ~200-300 unique companies

#### Step 4: Enrich with Google Maps API
```bash
python validate_and_enrich.py ../data/builtinla_data_jobs.csv

# Filter to:
# - <60 min transit OR
# - <5 miles (bikeable) OR
# - Remote/Hybrid
```

**Expected Result**: 150-250 companies with data jobs
**Cost**: $10-12 Google Maps API (250 companies × $0.05)

---

## 💰 TOTAL COST BREAKDOWN

| Phase | Task | Tool | Cost |
|-------|------|------|------|
| 1 | Scrape VCs | Firecrawl (FREE) | $0 |
| 1 | Enrich 40 VCs | Google Maps API | $2 |
| 2 | Filter <60 min | (local processing) | $0 |
| 3 | Scrape jobs | Firecrawl (FREE) | $0 |
| 3 | Enrich 250 companies | Google Maps API | $12 |
| **TOTAL** | | **$14** |

✅ **Well within your $300 credit!**

---

## 📊 FINAL MAP RESULT

**Your Interactive Map**:
- 🟠 **25-30 VCs** (orange pins) - all <60 min transit
- 🟢 **150-250 Data Jobs** (green pins) - matching YOUR skills + <60 min commute
- **NOT** 3,352 random tech companies!
- **Smart filtering** = targeted opportunities

---

## 🎯 IMMEDIATE NEXT STEP

**Which do you want to do?**

1. **Continue OpenVC scraping** (get more VCs with addresses)
2. **Wait for your 32 manual addresses** (then enrich everything at once)
3. **Start Phase 3 NOW** (scrape BuiltInLA for data jobs while you finish VCs)

**My recommendation**: **Option 3** - Start scraping data jobs NOW. We can run VC and Job enrichment in parallel since they're independent!

Type `1`, `2`, or `3` to proceed! 🚀

