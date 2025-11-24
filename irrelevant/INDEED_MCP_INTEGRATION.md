# 🎯 Indeed MCP Integration - How It Works

**Status:** ✅ Indeed MCP is WORKING in Claude Desktop  
**Date:** November 10, 2025

---

## 🔍 What We Discovered

Indeed MCP is **already active** in Claude Desktop! 

**Test Results:**
- ✅ `Indeed:search_jobs` - Works perfectly
- ✅ `Indeed:get_job_details` - Returns full job descriptions
- ✅ Returns: Company, location, salary, job type, URL

**Sample Search:**
```
Search: "data engineer"
Location: "Los Angeles, CA"
Results: 10 jobs including Scribd, Disney, Google, SpaceX, Sweetgreen
```

---

## 🏗️ Architecture

```
User asks Claude Desktop for jobs
        ↓
Claude calls Indeed:search_jobs MCP
        ↓
Claude processes each job:
   - Extract company domain
   - Call Hunter.io API (Python requests)
   - Call Google Maps API (Python requests)
   - Format as CSV row
        ↓
Claude writes CSV to /Users/anixlynch/dev/5miles-job-search/data/raw/
```

---

## 📊 Data Flow

### Indeed MCP Returns:
```
**Job Title:** Staff Data Engineer
**Job Id:** 5-cmh1-0-1j9o8u7p2goij806-8665eb2f707f1045
**Company:** Scribd
**Location:** Los Angeles, CA  
**Posted on:** October 23, 2025
**Job Type:** Fulltime
**Compensation:** $137,500 - $247,500 a year
**View Job URL:** https://to.indeed.com/nzzwk3c4vc4sh
```

### We Transform To:
```csv
company,title,location,google_maps_link,remote_option,salary_min,salary_max,...
Scribd,Staff Data Engineer,"Los Angeles, CA",https://maps.google.com/...,Onsite,137500,247500,...
```

---

## 🎯 How To Use (Through Claude Desktop Chat)

**Step 1: Ask Claude Desktop**
```
"Search Indeed for data engineer jobs in Los Angeles, 
then enrich with Hunter.io contacts and Google Maps commute,  
export to CSV matching Built In LA format"
```

**Step 2: Claude Desktop Will:**
1. Call Indeed MCP to get jobs
2. For each job:
   - Extract company domain
   - Call Hunter.io for contacts
   - Call Google Maps for commute
   - Format as CSV row
3. Write CSV to data/raw/

**Step 3: Result**
```
data/raw/indeed_jobs_20251110_HHMMSS.csv
```

---

## 🔧 Technical Details

### APIs Used:
1. **Indeed MCP** (Anthropic Official)
   - No API key needed
   - Native Claude Desktop integration
   
2. **Hunter.io API**
   - Key: `REDACTED_HUNTER_KEY`
   - Free tier: 25 requests/month
   
3. **Google Maps Distance Matrix**
   - Key: `REDACTED_MAPS_KEY`
   - Cost: $0.005 per request

### CSV Format (Matches Built In LA):
```
company, title, location, google_maps_link, remote_option,
salary_min, salary_max, posted_date,
department, department_head, department_head_email,
transit_routes, transit_duration, transit_changes, bike_duration,
nearest_metro, commute_rating, top_skills, url
```

---

## 🚀 Example Commands for Claude Desktop

### Basic Search:
```
Search Indeed for "data engineer" jobs in Los Angeles
```

### Full Pipeline:
```
Search Indeed for data engineer and AI engineer jobs in Los Angeles, 
get Hunter.io contacts and Google Maps commute for each, 
export to CSV in data/raw/ folder
```

### Filtered Search:
```
Search Indeed for remote data engineer jobs paying $150k+,
get contacts via Hunter.io, export to CSV
```

---

## 📁 File Locations

**Output CSV:**
```
/Users/anixlynch/dev/5miles-job-search/data/raw/indeed_jobs_TIMESTAMP.csv
```

**This Guide:**
```
/Users/anixlynch/dev/5miles-job-search/INDEED_MCP_INTEGRATION.md
```

---

## ⚡ Quick Start

Just tell Claude Desktop:

> "Use Indeed MCP to find 20 data engineer jobs in LA, 
> enrich with Hunter.io and Google Maps, save CSV"

Claude will handle everything! 🎉

---

**Last Updated:** November 10, 2025  
**Branch:** indeed-claude-desktop  
**Status:** ✅ Tested and Working
