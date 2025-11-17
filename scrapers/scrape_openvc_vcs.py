#!/usr/bin/env python3
"""
Scrape OpenVC.app for LA VC firms with full addresses
Each VC profile page has address in "Global HQ" field
"""

import time
import sys
import os

# List of LA VC firms from OpenVC (from the scraped list)
LA_VCS = [
    "Upfront Ventures",
    "Greycroft",
    "Crosscut Ventures",
    "Fifth Wall",
    "March Capital",
    "M13",
    "Bonfire Ventures",
    "Amplify LA",
    "Mucker Capital",
    "Science Inc",
    "TenOneTen Ventures",
    "Slauson & Co",
    "Backstage Capital",
    "Alpha Edison",
    "BAM Ventures",
    "Wavemaker Partners",
    "Struck Capital",
    "Embark Ventures",
    "Wonder Ventures",
    "Act One Ventures",
    "75 & Sunny",
    "Gold House Ventures",
    "Palisades Growth",
    "Embedded Ventures",
    "Fortify Ventures",
    "LvlUp Ventures",
    "Undeterred Capital",
    "Thiel Capital",
    "Jovono",
    "Kalyna Capital",
    "Willow Growth Partners",
    "FootPrint Coalition",
    "Ethos Fund",
    "Regeneration.VC",
    "Root and Shoot Ventures",
    "Archer Venture Capital",
    "Valhalla Ventures",
    "Checkmate Capital",
]

print("""
╔══════════════════════════════════════════════════════════════════╗
║  OPENVC LA VC SCRAPER                                            ║
║  Scraping VC profile pages for addresses                        ║
╚══════════════════════════════════════════════════════════════════╝
""")

print(f"📋 Found {len(LA_VCS)} LA-based VCs to scrape from OpenVC")
print(f"🔗 Will scrape profile pages for addresses from 'Global HQ' field")
print(f"\n💡 Using MCP Firecrawl (FREE) to scrape VC profile pages")
print(f"💰 Cost: $0 (Firecrawl) + $3 (Google Maps API for {len(LA_VCS)} VCs)")

print("\n" + "="*80)
print("📊 VC LIST TO SCRAPE")
print("="*80)

for i, vc in enumerate(LA_VCS, 1):
    # Convert VC name to OpenVC URL format
    vc_slug = vc.replace(" ", "%20")
    profile_url = f"https://www.openvc.app/fund/{vc_slug}"
    print(f"  [{i:2d}] {vc}")
    print(f"       → {profile_url}")

print("\n" + "="*80)
print("🚀 NEXT STEPS")
print("="*80)
print("""
1. Use MCP Firecrawl to scrape each VC profile page
2. Extract:
   - Firm Name
   - Global HQ (full address)
   - Stage focus (Seed, Series A, etc.)
   - Investment focus (sectors)
   - Website URL
3. Save to CSV: la_vcs_openvc.csv
4. Run validate_and_enrich.py to add commute data
5. Filter to VCs <60 min from Culver City
6. Load to DuckDB + Snowflake

Ready to scrape? The MCP Firecrawl tool will handle the scraping!
""")

# For the actual scraping, we'll use MCP Firecrawl from Cursor
# This script just sets up the list and strategy

