# 🎯 Indeed Scraper - Claude Desktop Branch

**Branch:** `indeed-claude-desktop`  
**Author:** Claude Desktop (Anthropic)  
**Date:** November 10, 2025

---

## 🌟 What's Different

This branch uses **Anthropic's Official Indeed MCP** instead of web scraping.

### Built In LA (Cursor) vs Indeed (Claude Desktop)

| Feature | Built In LA | Indeed (This Branch) |
|---------|------------|---------------------|
| Data Source | Web scraping | Official Indeed MCP ✅ |
| API | None needed | Indeed MCP via Claude |
| Hunter.io | ✅ Same | ✅ Same |
| Google Maps | ✅ Same | ✅ Same |
| CSV Format | ✅ | ✅ Identical |

---

## 📂 Files in This Branch

```
scrapers/
├── indeed_claude_desktop.py    ← NEW - Indeed MCP scraper
├── builtin_la_ultimate.py      ← Original (unchanged)
└── ...other scrapers
```

---

## 🚀 How to Use

### Prerequisites

1. **Claude Desktop** with Indeed MCP enabled
2. **API Keys** (hardcoded in script):
   - Hunter.io: `REDACTED_HUNTER_KEY`
   - Google Maps: `REDACTED_MAPS_KEY`

### Run the Scraper

```bash
cd /Users/anixlynch/dev/5miles-job-search
git checkout indeed-claude-desktop
source venv/bin/activate
python3 scrapers/indeed_claude_desktop.py
```

---

## 🔧 Configuration

Edit these in `scrapers/indeed_claude_desktop.py`:

```python
HOME_ADDRESS = "YOUR_HOME_ADDRESS"
MAX_DISTANCE_MILES = 10

SEARCH_PARAMS = {
    'search': 'data engineer OR AI engineer',
    'location': 'Los Angeles, CA',
    'country_code': 'US'
}
```

---

## 📊 CSV Output

**File:** `data/raw/indeed_jobs_TIMESTAMP.csv`

**Format:** Identical to Built In LA output

**Columns:**
- company, title, location, google_maps_link
- remote_option, salary_min, salary_max, posted_date
- department, department_head, department_head_email
- transit_routes, transit_duration, transit_changes
- bike_duration, nearest_metro, commute_rating
- top_skills, url

---

## 🔀 Branch Management

### Switch to Built In LA (Cursor)
```bash
git checkout builtin-la-cursor
```

### Switch to Indeed (Claude Desktop)
```bash
git checkout indeed-claude-desktop
```

### See all branches
```bash
git branch
```

---

## ⚠️ Important Notes

1. **Don't modify `builtin-la-cursor` branch** - That's Cursor's territory
2. **This branch is Claude Desktop only** - Uses Indeed MCP
3. **API keys are hardcoded** - No .env needed (for now)
4. **CSV format matches** - Can merge results from both branches

---

## 🎯 Next Steps

1. Claude Desktop executes Indeed MCP calls
2. Populate `search_indeed_jobs()` with actual MCP results
3. Test with a few jobs
4. Scale up to full search

---

## 📞 Questions?

- Built In LA issues → Ask Cursor
- Indeed MCP issues → Ask Claude Desktop
- API issues → Check API_COSTS_AND_SETUP.md

---

**Last Updated:** November 10, 2025  
**Status:** Template ready, needs Claude Desktop to populate Indeed MCP calls
