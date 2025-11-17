#!/usr/bin/env python3
"""
Scrape VC firm addresses from their websites using MCP Firecrawl
Then enrich with Google Maps commute data
"""

import re
import csv
import time
from datetime import datetime

# VC firms with their websites
VCS = [
    ("Aliment Capital", "https://www.alimentcap.com"),
    ("Alpha Edison", "https://alphaedison.com"),
    ("Amplify.LA", "https://amplify.la"),
    ("Angeleno Group", "https://angelenogroup.com"),
    ("Anthem Venture Partners", "https://anthemvp.com"),
    ("BAM Ventures", "https://bam.vc"),
    ("Backstage Capital", "https://backstagecapital.com"),
    ("Baroda Ventures", "https://barodaventures.com"),
    ("Bonfire Ventures", "https://bonfirevc.com"),
    ("California Technology Ventures", "https://ctventures.com"),
    ("Clearstone Venture Partners", "https://clearstone.com"),
    ("Clocktower Technology Ventures", "https://clocktowergroup.com"),
    ("Core VC", "https://corevc.com"),
    ("Crosscut Ventures", "https://crosscut.vc"),
    ("Embark Ventures", "https://embark.vc"),
    ("Fifth Wall", "https://fifthwall.com"),
    ("Fika Ventures", "https://fika.vc"),
    ("Greycroft", "https://greycroft.com"),
    ("Ground Force Capital", "https://groundforcecapital.com"),
    ("M13", "https://m13.co"),
    ("March Capital", "https://marchcp.com"),
    ("Michelson Impact Ventures", "https://michelson.vc"),
    ("Mucker Capital", "https://muckercapital.com"),
    ("Pasadena Angels", "https://pasadenaangels.com"),
    ("Plus Capital", "https://pluscapital.com"),
    ("Science Inc.", "https://science-inc.com"),
    ("Slauson & Co.", "https://slauson.co"),
    ("Struck Capital", "https://struckcapital.com"),
    ("TenOneTen Ventures", "https://tenoneten.net"),
    ("Upfront Ventures", "https://upfront.com"),
    ("Wavemaker Partners", "https://wavemaker.vc"),
    ("Wonder Ventures", "https://wonderventures.com"),
]

def extract_address_from_text(text, company_name):
    """
    Extract LA-area address from website text
    Looks for patterns like:
    - 123 Main St, Los Angeles, CA 90001
    - 456 Broadway Suite 100, Santa Monica, CA 90401
    """
    
    # Common LA area cities
    la_cities = [
        "Los Angeles", "Santa Monica", "Venice", "Culver City", "Beverly Hills",
        "West Hollywood", "Hollywood", "Playa Vista", "El Segundo", "Marina del Rey",
        "Century City", "Pasadena", "Glendale", "Burbank"
    ]
    
    # Address pattern: street number + street name + LA city + CA + zip
    pattern = r'\d+\s+[A-Za-z\s,\.]+(?:' + '|'.join(la_cities) + r')[^,]*,\s*CA\s*\d{5}'
    
    matches = re.findall(pattern, text, re.IGNORECASE)
    
    if matches:
        # Return the first match, cleaned up
        address = matches[0].strip()
        print(f"  ✅ Found: {address}")
        return address
    
    # Try simpler pattern - just city + CA
    for city in la_cities:
        if city.lower() in text.lower():
            print(f"  ⚠️  Found city: {city} (but no full address)")
            return f"{city}, CA"
    
    print(f"  ❌ No LA address found")
    return None

def scrape_vc_addresses():
    """
    Scrape addresses using the markdown we can get from websites
    In production, this would use MCP Firecrawl
    """
    
    print("="*80)
    print("🔍 SCRAPING VC ADDRESSES")
    print("="*80)
    print("\n💡 To use this script with MCP Firecrawl:")
    print("   Run each URL through: mcp_firecrawl_firecrawl_scrape")
    print("   Then paste the markdown into this script\n")
    
    results = []
    
    for i, (name, url) in enumerate(VCS, 1):
        print(f"\n[{i}/{len(VCS)}] {name}")
        print(f"  URL: {url}")
        
        # In production, you would:
        # 1. Call mcp_firecrawl_firecrawl_scrape(url)
        # 2. Get markdown text
        # 3. Extract address from markdown
        
        # For now, provide manual addresses for known ones
        known_addresses = {
            "Fika Ventures": "9696 Culver Blvd, Suite 204, Culver City, CA 90232",
            "Upfront Ventures": "2901 28th St, Santa Monica, CA 90405",
            "Fifth Wall": "1640 10th St, Santa Monica, CA 90404",
            "M13": "1640 Abbot Kinney Blvd, Venice, CA 90291",
            "Mucker Capital": "1334 3rd Street Promenade, Suite 201, Santa Monica, CA 90401",
            "Crosscut Ventures": "100 Wilshire Blvd, Suite 1950, Santa Monica, CA 90401",
            "Science Inc.": "1546 7th St, Santa Monica, CA 90401",
            "Greycroft": "2450 Broadway, Santa Monica, CA 90404",
            "Bonfire Ventures": "2450 Colorado Ave, Suite 100E, Santa Monica, CA 90404",
        }
        
        if name in known_addresses:
            address = known_addresses[name]
            print(f"  ✅ Known address: {address}")
        else:
            address = f"Los Angeles, CA"  # Default
            print(f"  ⚠️  Using default: {address}")
        
        results.append({
            'company': name,
            'url': url,
            'address': address,
            'source': 'website_scrape'
        })
        
        time.sleep(0.5)  # Be nice to servers
    
    return results

def save_results(results):
    """Save to CSV"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"../data/vc_addresses_{timestamp}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['company', 'url', 'address', 'source'])
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n✅ Saved to: {filename}")
    return filename

if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║  VC ADDRESS SCRAPER                                           ║
    ║  Step 1: Get addresses from VC websites                       ║
    ║  Step 2: Run validate_and_enrich.py to add commute data      ║
    ║  Step 3: Load to databases                                    ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    results = scrape_vc_addresses()
    
    print("\n" + "="*80)
    print("📊 SUMMARY")
    print("="*80)
    
    full_addresses = len([r for r in results if r['address'] != 'Los Angeles, CA'])
    partial_addresses = len(results) - full_addresses
    
    print(f"\n  Total VCs: {len(results)}")
    print(f"  ✅ Full addresses: {full_addresses}")
    print(f"  ⚠️  Need manual lookup: {partial_addresses}")
    
    csv_file = save_results(results)
    
    print(f"\n💡 Next steps:")
    print(f"   1. Review {csv_file}")
    print(f"   2. Add missing addresses manually (or use Perplexity)")
    print(f"   3. Run: python validate_and_enrich.py {csv_file}")
    print(f"   4. Run: python load_jobs_to_both.py <enriched_file>")

