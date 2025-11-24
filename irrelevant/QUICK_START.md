# ⚡ Quick Start Guide

## 🎯 Goal
Find data engineering jobs within 40-min commute from Culver City with your tech stack (AWS, GCP, Snowflake, BigQuery, dbt, RAG).

---

## 🚀 Run in 3 Steps

### Step 1: Setup (one time)
```bash
cd /Users/anixlynch/dev/project5miles_builtinLA
./setup.sh
```

### Step 2: Get Google Maps API Key
1. Go to: https://console.cloud.google.com/
2. Enable **"Distance Matrix API"**
3. Create API Key
4. Copy it

### Step 3: Run the Scraper
```bash
python3 scrape_all_builtinla.py
```

When prompted:
- **API Key**: Paste your key
- **Pages to scrape**: Enter `2` (for testing)

**Wait 5-10 minutes** ☕

---

## 📊 What You Get

CSV file in `data/raw/` with:

✅ **Company name**  
✅ **Job title**  
✅ **Distance from your place**  
✅ **Driving time**  
✅ **Transit time + number of transfers**  
✅ **Bike time**  
✅ **Commute rating** (⭐⭐⭐ = Excellent!)  
✅ **Tech stack match score**  
✅ **Job URL to apply**

---

## 🎯 Commute Ratings Explained

| Rating | Meaning |
|--------|---------|
| ⭐⭐⭐ Excellent | ≤40 mins, max 1 transfer |
| ⭐⭐ Good | ≤40 mins with 2 transfers |
| ⭐ Poor | >50 mins or >2 transfers |

**Focus on ⭐⭐⭐ rated jobs!**

---

## 💰 Cost

- **Per run**: $0.20 - $0.40
- **Your credit**: $300
- **Total runs possible**: 600+

**Extremely cheap!**

---

## 🏙️ Your Perfect Location

You're opposite Sony Entertainment in Culver City = Silicon Beach hub!

**Within easy commute:**
- Beverly Hills (4 mi) - Alo Yoga hiring!
- Santa Monica (5 mi) - 1 bus on Big Blue Bus
- Playa Vista (3 mi) - Bikeable
- Venice Beach (4 mi) - 1 bus

---

## 🎯 Pre-Found Job Leads

**Alo Yoga - Beverly Hills** ⭐⭐⭐  
→ 4 miles, bikeable, perfect tech stack!  
→ https://www.builtinla.com/job/senior-data-engineer/2276480

**Circle - Remote**  
→ AWS, GCP, dbt, Airflow  
→ https://www.builtinla.com/job/staff-data-engineer/6763507

---

## ❓ Troubleshooting

**"Module not found"**  
→ Run: `pip3 install requests beautifulsoup4`

**"API key invalid"**  
→ Check you enabled Distance Matrix API  
→ Check key is copied correctly

**"No jobs found"**  
→ Try more pages (3-4 instead of 2)  
→ Built In LA updates jobs weekly

---

## 🎉 You're All Set!

Your location is PERFECT for LA tech jobs. You're literally in the center of Silicon Beach! 🌊

**Ready to find your next role!** 🚀

