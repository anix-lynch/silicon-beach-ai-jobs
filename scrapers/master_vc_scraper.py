#!/usr/bin/env python3
"""
MASTER VC SCRAPER - Get ALL LA VCs from multiple sources
Then filter by <1 hour commute from Culver City
"""

import sys
print("""
╔══════════════════════════════════════════════════════════════════╗
║  MASTER VC SCRAPER FOR LA                                        ║
║  Sources: Papermark, OpenVC, AngelMatch, LA Business Journal     ║
║  Output: All VCs within 1 hour commute from Culver City          ║
╚══════════════════════════════════════════════════════════════════╝

📋 PLAN:
  1. Scrape Papermark (21 VCs) ✅ DONE
  2. Scrape OpenVC.app (~50 VCs)
  3. Scrape AngelMatch.io (~30 VCs)
  4. Combine & deduplicate (expect ~80-100 unique VCs)
  5. Enrich with Google Maps (filter to <60 min commute)
  6. Load to DuckDB + Snowflake

💰 COST ESTIMATE:
  - Firecrawl scraping: FREE (MCP)
  - Google Maps API: ~$5 for 100 VCs (one-time)
  - Result: 50-70 VCs within 1 hour

🎯 TARGET: Get you 50-70 VCs + 500+ jobs ALL within 1 hour!
""")

print("\n" + "="*80)
print("STEP 1: Papermark VCs")
print("="*80)
print("✅ Already scraped - 21 VCs")
print("   File: /Users/anixlynch/dev/5miles-job-search/data/vc_addresses_from_papermark.csv")

print("\n" + "="*80)
print("STEP 2: OpenVC.app")
print("="*80)
print("📍 URL: https://www.openvc.app/investor-lists/venture-capital-firms-investors-los-angeles")
print("💡 Action: Use MCP Firecrawl to scrape")
print("   Expected: ~50 additional VCs")

print("\n" + "="*80)
print("STEP 3: AngelMatch.io")
print("="*80)
print("📍 URL: https://angelmatch.io/investors/by-location/culver-city")
print("📍 URL: https://angelmatch.io/investors/by-location/santa-monica")
print("📍 URL: https://angelmatch.io/investors/by-location/venice")
print("💡 Action: Use MCP Firecrawl to scrape each location")
print("   Expected: ~30 additional VCs")

print("\n" + "="*80)
print("STEP 4: Combine & Deduplicate")
print("="*80)
print("💡 Merge all sources, remove duplicates by company name")
print("   Expected: 80-100 unique VCs total")

print("\n" + "="*80)
print("STEP 5: Enrich & Filter by Commute")
print("="*80)
print("💡 Use validate_and_enrich.py with Google Maps API")
print("   Filter: Keep only VCs with <60 min transit commute")
print("   Expected: 50-70 VCs within 1 hour")

print("\n" + "="*80)
print("STEP 6: Load to Databases")
print("="*80)
print("💡 Use load_jobs_to_both.py")
print("   Load to: DuckDB (free) + Snowflake (learning)")

print("\n" + "="*80)
print("🚀 NEXT ACTION")
print("="*80)
print("""
I'll now scrape OpenVC.app and AngelMatch.io using MCP Firecrawl.

This will give you:
  • 🟠 50-70 VCs (orange pins) - all <1 hour away
  • 🟢 500+ Jobs (green pins) - all <1 hour away

Total cost: ~$20 (one-time) for Google Maps API

Ready to proceed? Type 'yes' to start scraping!
""")

