# 🚀 Run Your LA Tech Job Map

## Quick Start (2 commands)

```bash
cd /Users/anixlynch/dev/5miles-job-search
source venv/bin/activate && streamlit run app.py
```

**Then open:** http://localhost:8501 in your browser

---

## What You'll See

### 📍 Interactive Map
- **Green pins** 🟢 = Excellent commute (<40 mins)
- **Orange pins** 🟠 = Good commute
- **Gray pins** ⚫ = Acceptable
- **Red pin** 🔴 = Your home

Click any pin to see:
- Company details
- Transit routes (actual bus numbers!)
- Direct links to career page, Google Maps, LinkedIn

### 🔗 Network Tracker
- Record warm intro paths
- Example: "TikTok → David Shi ← Elise Sha ← ME"
- Track: name, relationship, notes

---

## Features

1. **Filter by commute** - see only Excellent jobs
2. **Filter by area** - focus on Culver City/Santa Monica
3. **Add referrals** - track your network connections
4. **Export data** - all stored in DuckDB locally

---

## Your Top Targets

1. **Scopely** - 27 mins, Bus 33, Culver City
2. **TikTok** - 30 mins, Bus 3, Culver City  
3. **Hyperion** - 33 mins, Bus 3+17, West LA
4. **Snap** - 34 mins, Bus 3+8, Santa Monica
5. **Headspace** - 36 mins, Transit, Santa Monica
6. **Amazon** - 37 mins, Transit, Santa Monica

---

## Troubleshooting

**If streamlit won't start:**
```bash
# Re-create venv
cd /Users/anixlynch/dev/5miles-job-search
rm -rf venv
/usr/bin/python3 -m venv venv
source venv/bin/activate
pip install streamlit folium streamlit-folium pandas duckdb
streamlit run app.py
```

**If port 8501 is busy:**
```bash
streamlit run app.py --server.port 8502
```

---

## Privacy

✅ **100% LOCAL** - runs only on your Mac
✅ **No data uploaded** - everything stays private
✅ **DuckDB file** - stored at `data/network.duckdb`

---

**Need help?** The CSV is already perfect and works without Streamlit:
`data/raw/silicon_beach_contacts_20251110_174236.csv`

