# 💰 API Costs & Setup Guide

## 📊 Current Status

### ✅ Hunter.io API
- **API Key**: `REDACTED_HUNTER_KEY`
- **Plan**: Free  
- **Status**: ⚠️ **0 requests available** (may be maxed out for month)
- **What it does**: Finds emails, names, positions, phone numbers of hiring managers

### ❓ Google Maps API  
- **Status**: **NOT SET UP YET**
- **Need**: Your API key
- **What it does**: Calculates drive/transit/bike times + commute rating

---

## 💰 Cost Breakdown

### Hunter.io Costs

| Operation | Cost | What You Get |
|-----------|------|--------------|
| Domain Search | 1 credit | All emails at company (e.g., aloyoga.com) |
| Email Finder | 1 credit | Find specific person's email |
| Email Verifier | 0.1 credit | Check if email is valid |

**For our use case**: 1 credit per company
- **30 jobs**: ~30 credits (if all different companies)
- **Reality**: Maybe 15-20 companies (some companies have multiple jobs)

**Free Plan**: Usually 25-50 requests/month
**Paid Plans**:
- Starter: $49/mo = 500 requests
- Growth: $99/mo = 2,500 requests

### Google Maps API Costs

| API | Cost per Request | What We Use It For |
|-----|-----------------|-------------------|
| Distance Matrix | $0.005 (half a cent) | Get distance + time |
| Directions | $0.005 | Get detailed transit route |

**For our use case**: 3 requests per job (drive, transit, bike)
- **30 jobs**: 90 requests = **$0.45**
- **Your $300 credit**: Can do **60,000 requests** = 20,000 jobs!

**Free Tier**: $200/month credit (40,000 requests)

---

## 🎯 What The Scraper Gets You

### From Built In LA (Free):
✅ Company name  
✅ Job title  
✅ Full address (for commute calc)  
✅ Salary range  
✅ Posted date  
✅ Tech skills (AWS, dbt, Snowflake, etc.)  
✅ Benefits list  
✅ Remote/Hybrid/Onsite  

### From Hunter.io (1 credit per company):
✅ **Contact names** (e.g., "Jennifer Saul")  
✅ **Email addresses** (e.g., jennifer.saul@aloyoga.com)  
✅ **Job titles** (e.g., "Director of Engineering")  
✅ **Phone numbers** (if available)  
✅ **Email pattern** (e.g., {first}.{last}@company.com)  
✅ **Up to 10 relevant contacts** per company

Filters for: Engineers, Data people, CTOs, VPs, Directors, Managers, Recruiters, HR

### From Google Maps ($0.015 per job):
✅ **Exact distance** in miles  
✅ **Drive time** (e.g., "18 mins")  
✅ **Transit time** (e.g., "32 mins")  
✅ **Estimated bus/train transfers**  
✅ **Bike time** (e.g., "22 mins")  
✅ **Commute rating**: ⭐⭐⭐ Excellent / ⭐⭐ Good / ⭐ Poor  

Rating based on YOUR criteria: <40 mins, minimal transfers

---

## 📋 CSV Output Format

Your final CSV will have these columns:

### Job Info:
- `company` - Company name
- `title` - Job title  
- `location` - City, State
- `address` - Full street address
- `remote_option` - Remote/Hybrid/Onsite
- `salary_min` - Min salary
- `salary_max` - Max salary  
- `posted_date` - When posted

### Stalking Info (Hunter.io):
- `contact_1_name` - Top contact name
- `contact_1_email` - Their email
- `contact_1_position` - Their job title
- `contact_1_phone` - Phone (if available)
- `contact_2_name` - 2nd contact name
- `contact_2_email` - Their email
- `contact_2_position` - Their title
- `email_pattern` - Company email format

### Commute Info (Google Maps):
- `distance_miles` - Miles from your place
- `drive_duration` - Drive time
- `transit_duration` - Bus/train time  
- `transit_changes` - Number of transfers
- `bike_duration` - Bike time
- `commute_rating` - ⭐⭐⭐ rating

### Other:
- `top_skills` - Matched tech skills
- `benefits` - Top 5 benefits
- `url` - Job listing URL

---

## 🚀 Setup Steps

### Step 1: Hunter.io (Current Status)

Your key seems maxed out on free tier. Options:

**Option A: Wait** - Resets monthly  
**Option B: Upgrade** - $49/mo for 500 requests  
**Option C: Skip for now** - Scraper still works, just no contact info

### Step 2: Google Maps API (REQUIRED for commute)

1. Go to: https://console.cloud.google.com/
2. Enable these APIs:
   - ✅ **Distance Matrix API** 
   - ✅ **Directions API** (optional, for detailed routes)
3. Create API Key
4. Copy the key
5. Provide it to the scraper

**Cost**: ~$0.45 for 30 jobs (uses your $300 credit)

---

## 💡 Recommended Strategy

### Phase 1: Test Run (Low Cost)
- **Jobs**: 5 test jobs
- **Hunter.io**: Skip or use if resets
- **Google Maps**: ~$0.08
- **Goal**: Verify everything works

### Phase 2: Full Run (Main Search)
- **Jobs**: 30-50 jobs  
- **Hunter.io**: 15-20 companies = 15-20 credits
- **Google Maps**: ~$0.45-0.75
- **Total cost**: < $1 (just Google Maps)

### Phase 3: Weekly Updates
- **Jobs**: 10-15 new postings per week
- **Cost**: ~$0.15/week
- **Sustainable**: Can run for years with $300 credit

---

## 🎯 What You Get in the End

A spreadsheet with:

1. **All data engineering jobs** within 10 miles
2. **Exact commute times** via car/bus/bike
3. **⭐⭐⭐ Commute rating** (your 40-min criteria)
4. **Names and emails** of hiring managers/recruiters
5. **Phone numbers** (when available)
6. **Email patterns** to guess other contacts
7. **Tech stack match** to your skills
8. **Salary ranges** for negotiation

**Result**: You can:
- ✅ Email hiring managers directly (bypass HR)
- ✅ Call them on the phone
- ✅ See which jobs have easy commutes
- ✅ Focus on best-fit opportunities
- ✅ Get ahead of other applicants

---

## 🔑 Next Steps

**PROVIDE YOUR GOOGLE MAPS API KEY and we'll run the full scraper!**

Or tell me if you want to:
1. Set up Google Maps API first
2. Upgrade Hunter.io plan  
3. Run without contact info for now
4. Something else?

The scraper is ready to go! 🚀

