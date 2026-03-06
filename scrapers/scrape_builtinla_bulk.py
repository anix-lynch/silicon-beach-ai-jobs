#!/usr/bin/env python3
"""
Scrape ALL Built In LA companies (3,352+) with Hybrid/On-site filter
Then filter by commute and data job availability
"""

import requests
import os
import json
import csv
import time
from datetime import datetime
from bs4 import BeautifulSoup
import re

# API Keys
FIRECRAWL_API_KEY = os.getenv('FIRECRAWL_API_KEY', 'fc-86fdf55a646d4c009e2f09b7e3c8b929')
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
HOME_ADDRESS = os.getenv("HOME_ADDRESS", "YOUR_HOME_ADDRESS")

# Built In LA URLs (paginated)
BASE_URL = "https://www.builtinla.com/companies/office-type/OnSite/Hybrid?city=Los+Angeles&state=California&country=USA&longitude=-117.518005&latitude=34.572168&page={}"

def scrape_company_list_page(page_num):
    """Scrape one page of Built In LA companies using Firecrawl"""
    url = BASE_URL.format(page_num)
    
    print(f"\n📄 Scraping page {page_num}...")
    print(f"  URL: {url}")
    
    try:
        # Use Firecrawl to scrape the page
        firecrawl_url = "https://api.firecrawl.dev/v1/scrape"
        headers = {
            "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "url": url,
            "formats": ["markdown", "html"]
        }
        
        response = requests.post(firecrawl_url, headers=headers, json=payload, timeout=60)
        
        if response.status_code != 200:
            print(f"  ❌ Firecrawl error: {response.status_code}")
            return []
        
        data = response.json()
        html_content = data.get('data', {}).get('html', '')
        
        if not html_content:
            print(f"  ❌ No HTML content returned")
            return []
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        companies = []
        
        # Find company cards (adjust selector based on Built In's HTML structure)
        company_cards = soup.find_all('div', {'class': lambda x: x and 'company-card' in x.lower()})
        
        if not company_cards:
            # Try alternative selectors
            company_cards = soup.find_all('a', href=re.compile(r'/company/'))
        
        print(f"  Found {len(company_cards)} company elements")
        
        for card in company_cards:
            try:
                # Extract company name
                name_elem = card.find(['h2', 'h3', 'h4']) or card
                company_name = name_elem.get_text(strip=True)
                
                # Extract company URL
                company_url = card.get('href', '')
                if not company_url.startswith('http'):
                    company_url = f"https://www.builtinla.com{company_url}"
                
                # Extract location if available
                location_elem = card.find(string=re.compile(r'Los Angeles|California|CA'))
                location = location_elem.strip() if location_elem else "Los Angeles, CA"
                
                if company_name and len(company_name) > 2:
                    companies.append({
                        'name': company_name,
                        'url': company_url,
                        'location': location,
                        'source_page': page_num
                    })
            except Exception as e:
                continue
        
        print(f"  ✅ Extracted {len(companies)} companies")
        return companies
        
    except Exception as e:
        print(f"  ❌ Error scraping page {page_num}: {e}")
        return []

def get_company_address(company_url, company_name):
    """Get full address from company page using Firecrawl"""
    print(f"    🔍 Getting address for {company_name}...")
    
    try:
        firecrawl_url = "https://api.firecrawl.dev/v1/scrape"
        headers = {
            "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "url": company_url,
            "formats": ["markdown"]
        }
        
        response = requests.post(firecrawl_url, headers=headers, json=payload, timeout=30)
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        markdown = data.get('data', {}).get('markdown', '')
        
        # Extract address using regex
        # Look for patterns like "123 Main St, Los Angeles, CA 90001"
        address_pattern = r'\d+\s+[A-Za-z\s,]+(?:Los Angeles|Santa Monica|Venice|Culver City|Playa Vista)[^,]*,\s*CA\s*\d{5}'
        match = re.search(address_pattern, markdown)
        
        if match:
            address = match.group(0)
            print(f"    ✅ Found: {address}")
            return address
        
        # Try to extract from structured data
        if 'address' in markdown.lower():
            lines = markdown.split('\n')
            for i, line in enumerate(lines):
                if 'address' in line.lower() and i + 1 < len(lines):
                    potential_address = lines[i + 1].strip()
                    if 'CA' in potential_address or 'California' in potential_address:
                        print(f"    ✅ Found: {potential_address}")
                        return potential_address
        
        print(f"    ⚠️  No address found")
        return None
        
    except Exception as e:
        print(f"    ❌ Error getting address: {e}")
        return None

def calculate_commute(destination_address, company_name):
    """Get transit commute info from Google Maps"""
    if not GOOGLE_MAPS_API_KEY or GOOGLE_MAPS_API_KEY == 'YOUR_KEY_HERE':
        return None
    
    try:
        # Directions API for transit
        transit_url = f"https://maps.googleapis.com/maps/api/directions/json"
        transit_params = {
            'origin': HOME_ADDRESS,
            'destination': destination_address,
            'mode': 'transit',
            'key': GOOGLE_MAPS_API_KEY
        }
        transit_resp = requests.get(transit_url, params=transit_params, timeout=10)
        transit_data = transit_resp.json()
        
        if transit_data['status'] != 'OK':
            return None
        
        route = transit_data['routes'][0]['legs'][0]
        duration_mins = route['duration']['value'] // 60
        
        # Extract transit routes
        transit_routes = []
        nearest_metro = "N/A"
        
        for step in route['steps']:
            if step['travel_mode'] == 'TRANSIT':
                transit_details = step.get('transit_details', {})
                line = transit_details.get('line', {})
                vehicle_type = line.get('vehicle', {}).get('type', 'TRANSIT')
                line_name = line.get('short_name') or line.get('name', 'Transit')
                
                if vehicle_type in ['SUBWAY', 'HEAVY_RAIL']:
                    departure_stop = transit_details.get('departure_stop', {}).get('name', '')
                    if nearest_metro == "N/A":
                        nearest_metro = departure_stop
                
                transit_routes.append(f"{line_name} ({vehicle_type.lower()})")
        
        transit_routes_str = " → ".join(transit_routes) if transit_routes else "Walking only"
        transit_changes = max(0, len(transit_routes) - 1)
        
        # Commute rating
        if duration_mins <= 40 and transit_changes <= 1:
            rating = "⭐⭐⭐ Excellent"
            score = 100
        elif duration_mins <= 50:
            rating = "⭐⭐ Good"
            score = 75
        elif duration_mins <= 60:
            rating = "⭐ Acceptable"
            score = 50
        else:
            return None  # Filter out >60 min commutes
        
        google_maps_link = f"https://www.google.com/maps/dir/?api=1&origin={HOME_ADDRESS.replace(' ', '+')}&destination={destination_address.replace(' ', '+')}&travelmode=transit"
        
        print(f"    🚇 {duration_mins} min | {transit_routes_str} | {rating}")
        
        return {
            'transit_duration': f"{duration_mins} min",
            'transit_routes': transit_routes_str,
            'transit_changes': transit_changes,
            'commute_rating': rating,
            'commute_score': score,
            'nearest_metro': nearest_metro,
            'google_maps_link': google_maps_link
        }
        
    except Exception as e:
        print(f"    ❌ Commute error: {e}")
        return None

def has_data_jobs(company_url):
    """Check if company has data engineer/analyst jobs"""
    try:
        # Search for job listings on company page
        firecrawl_url = "https://api.firecrawl.dev/v1/scrape"
        headers = {
            "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "url": company_url,
            "formats": ["markdown"]
        }
        
        response = requests.post(firecrawl_url, headers=headers, json=payload, timeout=30)
        
        if response.status_code != 200:
            return False, []
        
        data = response.json()
        markdown = data.get('data', {}).get('markdown', '').lower()
        
        # Look for data-related job titles
        data_keywords = [
            'data engineer', 'data analyst', 'data scientist',
            'machine learning engineer', 'ml engineer',
            'ai engineer', 'analytics engineer',
            'business intelligence', 'bi analyst'
        ]
        
        found_roles = []
        for keyword in data_keywords:
            if keyword in markdown:
                found_roles.append(keyword)
        
        has_jobs = len(found_roles) > 0
        
        if has_jobs:
            print(f"    💼 Has data jobs: {', '.join(set(found_roles))}")
        
        return has_jobs, list(set(found_roles))
        
    except Exception as e:
        return False, []

def scrape_all_companies(max_pages=168):
    """Scrape all companies from Built In LA"""
    all_companies = []
    
    print(f"\n🚀 Starting bulk scrape of Built In LA (up to {max_pages} pages)...")
    print(f"   Filtering: <60 min commute + data jobs only")
    print(f"   Expected: 500-1000 companies\n")
    
    for page in range(1, max_pages + 1):
        companies = scrape_company_list_page(page)
        
        if not companies:
            print(f"\n⚠️  No companies found on page {page}, stopping...")
            break
        
        all_companies.extend(companies)
        
        # Rate limiting
        time.sleep(2)
        
        # Progress update every 10 pages
        if page % 10 == 0:
            print(f"\n📊 Progress: {len(all_companies)} companies scraped from {page} pages")
            print(f"   Continuing...\n")
    
    print(f"\n✅ Scraped {len(all_companies)} companies total")
    return all_companies

def enrich_and_filter_companies(companies, sample_size=None):
    """Get addresses, check commute, filter by data jobs"""
    enriched = []
    
    if sample_size:
        companies = companies[:sample_size]
        print(f"\n🔬 Testing with {sample_size} companies first...")
    
    print(f"\n🔍 Enriching {len(companies)} companies...")
    print(f"   Getting addresses → checking commute → checking data jobs\n")
    
    for i, company in enumerate(companies, 1):
        print(f"[{i}/{len(companies)}] {company['name']}")
        
        # Get full address
        address = get_company_address(company['url'], company['name'])
        
        if not address:
            # Try using the location from listing
            address = company.get('location', 'Los Angeles, CA')
        
        # Calculate commute
        commute_data = calculate_commute(address, company['name'])
        
        if not commute_data:
            print(f"    ❌ Commute >60 min or not accessible, skipping\n")
            continue
        
        # Check for data jobs
        has_jobs, job_types = has_data_jobs(company['url'])
        
        if not has_jobs:
            print(f"    ❌ No data jobs found, skipping\n")
            continue
        
        # Add to results
        enriched.append({
            'type': 'JOB',
            'company': company['name'],
            'title': ', '.join(job_types),
            'location': address,
            'address': address,
            'area': address.split(',')[-2].strip() if ',' in address else 'Los Angeles',
            'job_url': company['url'],
            'career_url': company['url'],
            **commute_data,
            'scraped_at': datetime.now().isoformat(),
            'source': 'builtinla_bulk'
        })
        
        print(f"    ✅ ADDED! ({len(enriched)} total so far)\n")
        
        # Rate limiting
        time.sleep(3)
        
        # Checkpoint save every 50 companies
        if len(enriched) % 50 == 0:
            save_checkpoint(enriched)
    
    return enriched

def save_checkpoint(companies):
    """Save progress checkpoint"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"../data/builtinla_checkpoint_{timestamp}.csv"
    save_to_csv(companies, filename)
    print(f"\n💾 Checkpoint saved: {len(companies)} companies\n")

def save_to_csv(results, filename=None):
    """Save to CSV"""
    if not filename:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"../data/builtinla_bulk_{timestamp}.csv"
    
    fieldnames = [
        'type', 'company', 'title', 'location', 'address', 'area',
        'job_url', 'career_url',
        'transit_duration', 'transit_routes', 'transit_changes',
        'commute_rating', 'commute_score', 'nearest_metro',
        'google_maps_link', 'scraped_at', 'source'
    ]
    
    os.makedirs('../data', exist_ok=True)
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n✅ Saved {len(results)} companies to: {filename}")
    return filename

if __name__ == '__main__':
    # Step 1: Scrape company list (fast, just listing pages)
    print("="*80)
    print("STEP 1: Scraping company list from Built In LA")
    print("="*80)
    
    # Start with just 5 pages to test (should give ~100 companies)
    companies = scrape_all_companies(max_pages=5)
    
    # Step 2: Enrich with addresses, commute, and job checks (slow)
    print("\n" + "="*80)
    print("STEP 2: Enriching companies (address + commute + job check)")
    print("="*80)
    
    # Test with first 20 companies
    enriched = enrich_and_filter_companies(companies, sample_size=20)
    
    # Step 3: Save results
    print("\n" + "="*80)
    print("STEP 3: Saving results")
    print("="*80)
    
    csv_file = save_to_csv(enriched)
    
    print("\n" + "="*80)
    print("📊 SUMMARY")
    print("="*80)
    
    excellent = len([r for r in enriched if r['commute_score'] >= 100])
    good = len([r for r in enriched if 75 <= r['commute_score'] < 100])
    
    print(f"  Total companies checked: {len(companies)}")
    print(f"  ✅ Passed filters: {len(enriched)}")
    print(f"  🟢 Excellent commute (<40 min): {excellent}")
    print(f"  🟠 Good commute (40-50 min): {good}")
    print(f"\n  Next: python load_vcs_to_duckdb.py {csv_file}")
    print(f"  Then refresh Streamlit to see {len(enriched)} new green pins! 🗺️")

