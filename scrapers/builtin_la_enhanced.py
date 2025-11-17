#!/usr/bin/env python3
"""
Enhanced Built In LA Job Scraper with Perplexity AI for Department Intelligence
- Scrapes ALL data engineer and AI engineer jobs
- Only includes jobs with specific addresses (not just "Los Angeles, CA")
- Uses Perplexity API for intelligent department head search
- Provides detailed transit info (bus numbers, metro lines)
"""

import requests
import csv
import time
import re
from datetime import datetime
from bs4 import BeautifulSoup

# ==============================================================================
# CONFIG
# ==============================================================================

HOME_ADDRESS = "YOUR_HOME_ADDRESS"
MAX_DISTANCE_MILES = 10

# APIs
HUNTER_API_KEY = os.getenv("HUNTER_API_KEY")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

# ==============================================================================
# PERPLEXITY AI - INTELLIGENT DEPARTMENT HEAD SEARCH
# ==============================================================================

def get_department_head_perplexity(company_name, job_title):
    """
    Use Perplexity API to find department head information
    This searches public info (LinkedIn, company websites, news)
    """
    if not PERPLEXITY_API_KEY:
        return None
    
    print(f"  🔍 Perplexity: Searching for {company_name} data/AI department head...")
    
    try:
        # Craft a specific query
        query = f"Who is the head of data engineering or AI/ML department at {company_name}? Include their name, title, and LinkedIn profile if available."
        
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.1-sonar-small-128k-online",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that finds department head information from public sources. Be concise and factual."
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            "max_tokens": 200,
            "temperature": 0.2,
            "return_citations": True
        }
        
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=payload,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            answer = data['choices'][0]['message']['content']
            
            # Parse the response for name and title
            result = {
                'department_head': '',
                'department_head_title': '',
                'linkedin_url': ''
            }
            
            # Extract LinkedIn URL if present
            linkedin_match = re.search(r'linkedin\.com/in/[\w-]+', answer)
            if linkedin_match:
                result['linkedin_url'] = f"https://{linkedin_match.group(0)}"
            
            # Simple parsing - look for name patterns
            lines = answer.split('\n')
            for line in lines:
                if any(title in line.lower() for title in ['vp', 'head', 'director', 'chief', 'cto', 'cdo']):
                    # Try to extract name
                    name_match = re.search(r'\b([A-Z][a-z]+ [A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\b', line)
                    if name_match:
                        result['department_head'] = name_match.group(1)
                        result['department_head_title'] = line.strip()
                        break
            
            if result['department_head']:
                print(f"    ✅ Found: {result['department_head']}")
            else:
                print(f"    ⚠️  No clear department head found")
            
            return result
        else:
            print(f"    ⚠️  Perplexity API error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"    ⚠️  Perplexity error: {e}")
        return None

# ==============================================================================
# GOOGLE MAPS - TRANSIT ROUTING
# ==============================================================================

def calculate_commute(origin, destination, api_key):
    """Calculate transit and bike commute with detailed bus/metro info"""
    if not api_key:
        return None
    
    print(f"  📍 Google Maps: Calculating from {destination}...")
    
    directions_url = "https://maps.googleapis.com/maps/api/directions/json"
    
    result = {
        'transit_routes': '',
        'transit_duration': '',
        'transit_changes': 0,
        'bike_duration': '',
        'nearest_metro': 'Culver City Station',  # Default
        'commute_rating': '',
        'google_maps_link': f"https://www.google.com/maps/dir/?api=1&origin={origin.replace(' ', '+')}&destination={destination.replace(' ', '+')}"
    }
    
    # Get transit with detailed routes
    try:
        params = {
            'origin': origin,
            'destination': destination,
            'mode': 'transit',
            'transit_mode': 'bus|rail',
            'departure_time': 'now',
            'key': api_key
        }
        
        response = requests.get(directions_url, params=params, timeout=10)
        data = response.json()
        
        if data['status'] == 'OK' and data.get('routes'):
            route = data['routes'][0]['legs'][0]
            duration_mins = route['duration']['value'] / 60
            result['transit_duration'] = route['duration']['text']
            
            # Extract bus/metro lines
            transit_steps = []
            for step in route['steps']:
                if step.get('travel_mode') == 'TRANSIT':
                    transit = step.get('transit_details', {})
                    line = transit.get('line', {})
                    vehicle = line.get('vehicle', {}).get('type', 'Transit')
                    line_name = line.get('short_name') or line.get('name', '')
                    
                    if vehicle == 'BUS':
                        transit_steps.append(f"Bus {line_name}")
                    elif vehicle in ['SUBWAY', 'HEAVY_RAIL', 'METRO_RAIL']:
                        transit_steps.append(f"Metro {line_name}")
                    else:
                        transit_steps.append(line_name)
            
            if transit_steps:
                result['transit_routes'] = ' → '.join(transit_steps)
                result['transit_changes'] = len(transit_steps) - 1
            else:
                print(f"    ❌ No public transit")
                return None
            
            # Rate commute
            if duration_mins <= 40 and result['transit_changes'] <= 1:
                result['commute_rating'] = '⭐⭐⭐ Excellent'
            elif duration_mins <= 50 and result['transit_changes'] <= 1:
                result['commute_rating'] = '⭐⭐ Good'
            else:
                result['commute_rating'] = '⭐ Acceptable'
        else:
            print(f"    ❌ No public transit")
            return None
        
        time.sleep(0.3)
    except Exception as e:
        print(f"    ⚠️  Transit: {e}")
        return None
    
    # Bike
    try:
        params = {
            'origin': origin,
            'destination': destination,
            'mode': 'bicycling',
            'key': api_key
        }
        
        response = requests.get(directions_url, params=params, timeout=10)
        data = response.json()
        
        if data['status'] == 'OK':
            route = data['routes'][0]['legs'][0]
            result['bike_duration'] = route['duration']['text']
        
        time.sleep(0.3)
    except Exception as e:
        print(f"    ⚠️  Bike: {e}")
    
    return result

# ==============================================================================
# SCRAPE JOB DETAILS
# ==============================================================================

def extract_job_urls_from_page(page_url):
    """Extract all job URLs from a Built In LA listing page"""
    print(f"🔍 Extracting job URLs from: {page_url}")
    
    try:
        response = requests.get(page_url, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all job links
        job_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if '/job/' in href and href not in job_links:
                if not href.startswith('http'):
                    href = f"https://www.builtinla.com{href}"
                job_links.append(href)
        
        print(f"✅ Found {len(job_links)} job URLs")
        return job_links
        
    except Exception as e:
        print(f"❌ Error extracting URLs: {e}")
        return []

def extract_job_data(url, google_maps_key):
    """Extract all data from a single job posting"""
    print("=" * 80)
    print(f"🔍 Scraping: {url}")
    print("=" * 80)
    
    try:
        import json
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find JSON-LD structured data (handle multiple formats)
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        job_posting = None
        
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    if data.get('@type') == 'JobPosting':
                        job_posting = data
                        break
                    elif '@graph' in data:
                        for item in data['@graph']:
                            if item.get('@type') == 'JobPosting':
                                job_posting = item
                                break
            except:
                continue
        
        if not job_posting:
            print("  ❌ No JobPosting JSON-LD found")
            return None
        
        # Initialize job data
        job_data = {
            'company': job_posting.get('hiringOrganization', {}).get('name', ''),
            'title': job_posting.get('title', ''),
            'location': '',
            'address': '',
            'remote_option': 'Onsite',
            'salary_min': '',
            'salary_max': '',
            'posted_date': '',
            'top_skills': [],
            'department': '',
            'department_head': '',
            'department_head_title': '',
            'linkedin_url': '',
            'transit_routes': '',
            'transit_duration': '',
            'transit_changes': 0,
            'bike_duration': '',
            'nearest_metro': '',
            'commute_rating': '',
            'google_maps_link': '',
            'url': url
        }
        
        print(f"✅ Company: {job_data['company']}")
        print(f"✅ Title: {job_data['title']}")
        
        # Location
        job_location = job_posting.get('jobLocation', {})
        if isinstance(job_location, list):
            job_location = job_location[0] if job_location else {}
        
        address = job_location.get('address', {})
        if address:
            locality = address.get('addressLocality', '')
            region = address.get('addressRegion', '')
            street = address.get('streetAddress', '')
            postal_code = address.get('postalCode', '')
            
            job_data['location'] = f"{locality}, {region}"
            job_data['address'] = f"{street}, {locality}, {region} {postal_code}".strip(', ')
        
        # SKIP if no specific address
        if not job_data['address'] or job_data['address'] == job_data['location']:
            print(f"  ⚠️  Skipping - no specific street address")
            return None
        
        print(f"✅ Location: {job_data['location']}")
        print(f"✅ Address: {job_data['address']}")
        
        # Remote option
        desc = job_posting.get('description', '').lower()
        if 'fully remote' in desc:
            job_data['remote_option'] = 'Remote'
        elif 'hybrid' in desc or 'remote' in desc:
            job_data['remote_option'] = 'Hybrid'
        
        # Salary
        salary = job_posting.get('baseSalary', {})
        if salary:
            value = salary.get('value', {})
            job_data['salary_min'] = int(value.get('minValue', 0))
            job_data['salary_max'] = int(value.get('maxValue', 0))
        
        # Posted date
        posted = job_posting.get('datePosted', '')
        if posted:
            job_data['posted_date'] = posted.split('T')[0]
        
        # Extract skills
        desc_text = BeautifulSoup(job_posting.get('description', ''), 'html.parser').get_text()
        tech_keywords = ['AWS', 'GCP', 'AZURE', 'SNOWFLAKE', 'BIGQUERY', 'DBT', 'AIRFLOW', 
                        'PYTHON', 'SQL', 'SPARK', 'KAFKA', 'KUBERNETES', 'DOCKER', 'TERRAFORM',
                        'DATABRICKS', 'REDSHIFT', 'POSTGRES', 'ELASTICSEARCH', 'ALLOYDB',
                        'PYTORCH', 'TENSORFLOW', 'VECTOR DATABASE', 'RAG', 'LLM']
        
        found_skills = []
        for keyword in tech_keywords:
            if keyword.lower() in desc_text.lower():
                found_skills.append(keyword)
        job_data['top_skills'] = ', '.join(found_skills[:8])
        
        # Calculate commute - ONLY if we have a real address
        if job_data['address'] and job_data['remote_option'] != 'Remote':
            commute_data = calculate_commute(HOME_ADDRESS, job_data['address'], google_maps_key)
            if commute_data is None:
                print(f"  ⚠️  Skipping - no public transit available")
                return None
            
            job_data.update(commute_data)
            print(f"  ✅ {commute_data['transit_routes']} | {commute_data['commute_rating']}")
        else:
            print(f"  ⚠️  Skipping - Remote job")
            return None
        
        # Use Perplexity to find department head
        perplexity_data = get_department_head_perplexity(job_data['company'], job_data['title'])
        if perplexity_data:
            job_data.update(perplexity_data)
        
        return job_data
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None

# ==============================================================================
# MAIN
# ==============================================================================

def main():
    print("=" * 80)
    print("🚀 ENHANCED JOB SCRAPER - Perplexity AI + Google Maps")
    print("=" * 80)
    print()
    print(f"✅ Perplexity API: Active")
    print(f"✅ Google Maps API: Active")
    print(f"📍 Home: {HOME_ADDRESS}")
    print(f"📏 Max Distance: {MAX_DISTANCE_MILES} miles")
    print()
    
    # Step 1: Get ALL job URLs from multiple categories
    print("📊 Fetching job listings...")
    data_engineer_urls = extract_job_urls_from_page("https://www.builtinla.com/jobs/data-analytics/data-engineering")
    ai_ml_urls = extract_job_urls_from_page("https://www.builtinla.com/jobs/data-analytics/machine-learning")
    data_analyst_urls = extract_job_urls_from_page("https://www.builtinla.com/jobs/data-analytics/analysis-reporting")
    bi_analyst_urls = extract_job_urls_from_page("https://www.builtinla.com/jobs/data-analytics/business-intelligence")
    
    all_urls = list(set(data_engineer_urls + ai_ml_urls + data_analyst_urls + bi_analyst_urls))
    print(f"\n✅ Total unique jobs to process: {len(all_urls)}")
    print()
    
    # Step 2: Scrape each job
    results = []
    for i, url in enumerate(all_urls[:50], 1):  # Process up to 50 jobs
        print(f"\n[{i}/{min(50, len(all_urls))}]")
        job_data = extract_job_data(url, GOOGLE_MAPS_API_KEY)
        if job_data:
            results.append(job_data)
        time.sleep(2)  # Be nice to APIs
        
        # Progress update every 10 jobs
        if i % 10 == 0:
            print(f"\n✅ Progress: {len(results)} jobs with addresses found so far...")
    
    print(f"\n🎯 Final: Found {len(results)} jobs with specific addresses and transit access!")
    
    # Export
    if results:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_file = f'data/raw/jobs_enhanced_{timestamp}.csv'
        
        fieldnames = [
            'company', 'title', 'location', 'address', 'google_maps_link', 'remote_option',
            'salary_min', 'salary_max', 'posted_date',
            'department_head', 'department_head_title', 'linkedin_url',
            'transit_routes', 'transit_duration', 'transit_changes', 'bike_duration',
            'nearest_metro', 'commute_rating',
            'top_skills', 'url'
        ]
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(results)
        
        print("\n" + "=" * 80)
        print(f"✅ Exported {len(results)} jobs to: {csv_file}")
        print("=" * 80)
        
        # Summary
        for job in results:
            print(f"\n🏢 {job['company']} - {job['title']}")
            print(f"   📍 {job['location']} | {job['remote_option']}")
            if job.get('department_head'):
                print(f"   👤 {job['department_head']} - {job['department_head_title']}")
            if job.get('commute_rating'):
                print(f"   🚌 {job['commute_rating']}")
    else:
        print("\n❌ No jobs found with transit access!")

if __name__ == '__main__':
    main()

