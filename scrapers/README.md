# 🤖 Scrapers Directory

This folder contains job scrapers for different platforms, all using the same APIs and output format.

---

## 📋 Current Scrapers

### ✅ Built In LA

| File | Purpose | Status |
|------|---------|--------|
| `builtin_la_ultimate.py` | **MAIN SCRAPER** - Full featured with Hunter.io + Google Maps | ✅ Ready |
| `builtin_la.py` | Full page scraper (all listings) | ✅ Ready |
| `builtin_la_focused.py` | Pre-filtered job URLs | ✅ Ready |
| `builtin_la_json_parser.py` | JSON-LD data extractor | ✅ Ready |
| `builtin_la_single_test.py` | Test single job extraction | ✅ Ready |

---

## 🔜 Coming Soon

### Indeed
- **File**: `indeed.py`
- **Status**: Waiting for Indeed MCP
- **Strategy**: Use MCP for scraping, add Hunter.io + Google Maps

### LinkedIn  
- **File**: `linkedin.py`
- **Status**: Planned
- **Bonus**: Direct profile links for networking

### AngelList
- **File**: `angellist.py`
- **Status**: Planned
- **Focus**: Startup/early-stage companies

---

## 🏗️ Scraper Template

Copy this pattern for new job boards:

```python
#!/usr/bin/env python3
"""
JOBBOARD_NAME scraper with Hunter.io + Google Maps integration
"""

import json
import csv
import time
from datetime import datetime
from bs4 import BeautifulSoup
import requests

# ============================================================================
# CONFIGURATION (Shared across all scrapers)
# ============================================================================

HOME_ADDRESS = os.getenv("HOME_ADDRESS", "YOUR_HOME_ADDRESS")
MAX_DISTANCE_MILES = 10
HUNTER_API_KEY = "YOUR_HUNTER_API_KEY"
GOOGLE_MAPS_API_KEY = YOUR_GOOGLE_MAPS_API_KEY

TECH_KEYWORDS = [
    'aws', 'gcp', 'snowflake', 'bigquery', 'dbt', 'airflow',
    'dataflow', 'pub/sub', 'elasticsearch', 'alloydb',
    'rag', 'semantic search', 'vector database'
]

# ============================================================================
# STEP 1: Scrape Job Listings
# ============================================================================

def scrape_job_listings(url):
    """
    Extract job listings from JOBBOARD_NAME
    Return list of job URLs
    """
    # YOUR CUSTOM SCRAPING LOGIC HERE
    pass

# ============================================================================
# STEP 2: Extract Job Details
# ============================================================================

def extract_job_data(job_url):
    """
    Extract detailed job data from single listing
    """
    # Parse job page
    # Extract: company, title, location, salary, skills, etc.
    pass

# ============================================================================
# STEP 3: Get Contacts (Hunter.io) - SHARED
# ============================================================================

def get_company_contacts(company_name, company_domain):
    """
    Use Hunter.io to find hiring managers
    COPY FROM builtin_la_ultimate.py
    """
    pass

# ============================================================================
# STEP 4: Calculate Commute (Google Maps) - SHARED
# ============================================================================

def calculate_commute(origin, destination, api_key):
    """
    Calculate drive/transit/bike times
    COPY FROM builtin_la_ultimate.py
    """
    pass

# ============================================================================
# STEP 5: Export to CSV - SHARED FORMAT
# ============================================================================

def export_to_csv(jobs, filename):
    """
    Export to: data/raw/JOBBOARD_jobs_TIMESTAMP.csv
    """
    fieldnames = [
        'company', 'title', 'location', 'address', 'remote_option',
        'salary_min', 'salary_max', 'posted_date',
        'contact_1_name', 'contact_1_email', 'contact_1_position', 'contact_1_phone',
        'contact_2_name', 'contact_2_email', 'contact_2_position',
        'email_pattern',
        'distance_miles', 'drive_duration', 'transit_duration', 
        'transit_changes', 'bike_duration', 'commute_rating',
        'top_skills', 'benefits', 'url'
    ]
    
    # Write CSV
    pass

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("🚀 JOBBOARD_NAME Scraper")
    
    # 1. Get job listings
    # 2. Extract details for each
    # 3. Get contacts via Hunter.io
    # 4. Calculate commute via Google Maps
    # 5. Export to CSV
    
    pass

if __name__ == '__main__':
    main()
```

---

## 🔑 Shared Resources

### APIs (Already Configured)

**Hunter.io:**
- Key: `YOUR_HUNTER_API_KEY`
- Function: `get_company_contacts()` from `builtin_la_ultimate.py`

**Google Maps:**
- Key: `os.getenv("GOOGLE_MAPS_API_KEY")`  
- Function: `calculate_commute()` from `builtin_la_ultimate.py`

### Common Code

Copy these functions from `builtin_la_ultimate.py`:
- `get_company_contacts()` - Hunter.io integration
- `calculate_commute()` - Google Maps integration
- `export_to_csv()` - Consistent CSV format

---

## 📊 Output Format

All scrapers must export to: `data/raw/JOBBOARD_jobs_TIMESTAMP.csv`

**Required columns** (same order):
1. company, title, location, address, remote_option
2. salary_min, salary_max, posted_date
3. contact_1_name, contact_1_email, contact_1_position, contact_1_phone
4. contact_2_name, contact_2_email, contact_2_position
5. email_pattern
6. distance_miles, drive_duration, transit_duration, transit_changes
7. bike_duration, commute_rating
8. top_skills, benefits, url

---

## ✅ Testing New Scrapers

1. **Create test script**: `JOBBOARD_single_test.py`
2. **Test with 1 job** first
3. **Verify all fields** are populated
4. **Check CSV output** format
5. **Run on 5-10 jobs** for validation
6. **Then run full scrape**

---

## 💡 Tips for AI Agents

If you're building a new scraper:

1. **Start from `builtin_la_ultimate.py`** - It has everything
2. **Only change the scraping logic** - Keep Hunter.io + Maps integration
3. **Test incrementally** - Don't scrape 100 jobs on first run
4. **Follow naming**: `JOBBOARD_NAME.py` (lowercase, underscores)
5. **Document in this README** when complete

### What NOT to Change:
- ❌ API keys (use existing)
- ❌ CSV column names (keep consistent)
- ❌ Home address constant
- ❌ Tech keywords list
- ❌ Commute rating logic

### What TO Change:
- ✅ Job listing URLs
- ✅ HTML/JSON parsing logic
- ✅ Company domain extraction
- ✅ Custom job board features

---

## 🎯 Current Priority

1. **Run Built In LA** (ready now!)
2. **Add Indeed** (when MCP available)
3. **Add LinkedIn** (after Indeed works)
4. **Add AngelList** (after LinkedIn works)

---

**Last Updated:** November 10, 2025  
**Maintainer:** Built In LA scraper (active)  
**Contributors**: Indeed scraper (coming soon)

