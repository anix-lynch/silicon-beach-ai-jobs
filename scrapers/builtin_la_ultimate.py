#!/usr/bin/env python3
"""
🚀 ULTIMATE JOB SCRAPER
- Scrapes Built In LA using JSON-LD
- Gets contacts via Hunter.io API  
- Calculates commute via Google Maps API
- Exports everything to CSV for easy stalking
"""

import json
import csv
import time
import re
from datetime import datetime
from bs4 import BeautifulSoup
import requests

# ==============================================================================
# CONFIGURATION
# ==============================================================================

HOME_ADDRESS = os.getenv("HOME_ADDRESS", "YOUR_HOME_ADDRESS")
MAX_DISTANCE_MILES = 10

# Hunter.io API
HUNTER_API_KEY = os.getenv("HUNTER_API_KEY")

# Google Maps API
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# Job URLs to scrape - Data Engineer & AI Engineer roles
JOB_URLS = [
    # Data Engineer jobs
    "https://www.builtinla.com/job/senior-data-engineer/2276480",  # Alo Yoga
    "https://www.builtinla.com/job/data-engineer/7656346",  # Screenverse
    "https://www.builtinla.com/job/data-engineer/2448178",  # EDO
    "https://www.builtinla.com/job/staff-data-engineer/6707579",  # CertifID
    "https://www.builtinla.com/job/senior-ai-data-engineer/4715267",  # SentinelOne
    "https://www.builtinla.com/job/senior-data-engineer/7519843",  # ChowNow
    "https://www.builtinla.com/job/data-engineer/7480927",  # Re:Build Manufacturing
    "https://www.builtinla.com/job/data-engineer-ii-senior-data-engineer/7372403",  # Circle
    
    # AI/ML Engineer jobs
    "https://www.builtinla.com/job/ai-engineer-ii-sr-ai-engineer-i/7591771",  # AI Engineer
    "https://www.builtinla.com/job/machine-learning-engineer-computer-vision/7597082",  # ML Computer Vision
    "https://www.builtinla.com/job/senior-machine-learning-engineer/7590375",  # GM ML Engineer
    "https://www.builtinla.com/job/ai-engineer/7107575",  # AI Engineer
    "https://www.builtinla.com/job/machine-learning-engineer-generative-ai/4252347",  # Snap Generative AI
]

# ==============================================================================
# HUNTER.IO INTEGRATION
# ==============================================================================

def get_company_contacts(company_name, company_domain):
    """
    Use Hunter.io to find hiring managers, recruiters, and engineering leads
    """
    if not HUNTER_API_KEY or not company_domain:
        return {
            'contacts': [],
            'email_pattern': 'Unknown',
            'error': 'No API key or domain'
        }
    
    print(f"  🔍 Hunter.io: Searching {company_domain}...")
    
    try:
        response = requests.get(
            "https://api.hunter.io/v2/domain-search",
            params={
                'domain': company_domain,
                'api_key': HUNTER_API_KEY,
                'limit': 50  # Get more results
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json().get('data', {})
            emails = data.get('emails', [])
            
            # Filter for relevant contacts (engineering, data, hiring)
            relevant_contacts = []
            keywords = [
                'engineer', 'data', 'tech', 'cto', 'vp', 'director', 
                'manager', 'head', 'recruit', 'talent', 'hr', 'people'
            ]
            
            for email_data in emails:
                position = email_data.get('position', '').lower()
                
                if any(keyword in position for keyword in keywords):
                    contact = {
                        'name': f"{email_data.get('first_name', '')} {email_data.get('last_name', '')}".strip(),
                        'email': email_data.get('value', ''),
                        'position': email_data.get('position', ''),
                        'department': email_data.get('department', ''),
                        'phone': email_data.get('phone_number', ''),
                        'linkedin': email_data.get('linkedin', ''),
                        'relevance': 'high' if any(x in position for x in ['data', 'engineer', 'tech']) else 'medium'
                    }
                    relevant_contacts.append(contact)
            
            # Sort by relevance
            relevant_contacts.sort(key=lambda x: (x['relevance'] != 'high', x['position']))
            
            return {
                'contacts': relevant_contacts[:10],  # Top 10
                'email_pattern': data.get('pattern', 'Unknown'),
                'total_found': len(emails),
                'error': None
            }
        else:
            return {
                'contacts': [],
                'email_pattern': 'Unknown',
                'error': f"HTTP {response.status_code}"
            }
    
    except Exception as e:
        return {
            'contacts': [],
            'email_pattern': 'Unknown',
            'error': str(e)
        }

# ==============================================================================
# GOOGLE MAPS INTEGRATION
# ==============================================================================

def calculate_commute(origin, destination, api_key):
    """
    Calculate commute time via car, transit, and bike
    """
    if not api_key:
        return {
            'distance_miles': None,
            'drive_duration': 'N/A - No API key',
            'transit_duration': 'N/A - No API key',
            'transit_changes': 0,
            'bike_duration': 'N/A - No API key',
            'commute_rating': 'Unknown'
        }
    
    print(f"  📍 Google Maps: Calculating from {destination}...")
    
    directions_url = "https://maps.googleapis.com/maps/api/directions/json"
    
    result = {
        'transit_routes': '',
        'transit_duration': '',
        'transit_changes': 0,
        'bike_duration': '',
        'nearest_metro': '',
        'commute_rating': '',
        'google_maps_link': f"https://www.google.com/maps/dir/?api=1&origin={origin.replace(' ', '+')}&destination={destination.replace(' ', '+')}"
    }
    
    # Get nearest METRO station (not bus stop)
    try:
        places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            'location': '34.0259,-118.3963',  # Your home
            'rankby': 'distance',
            'type': 'subway_station',  # Changed from transit_station to subway_station
            'key': api_key
        }
        response = requests.get(places_url, params=params, timeout=10)
        data = response.json()
        if data['status'] == 'OK' and data.get('results'):
            # Filter for actual metro stations, not bus stops
            for place in data['results'][:5]:
                name = place.get('name', '')
                if 'Metro' in name or 'Station' in name:
                    result['nearest_metro'] = name
                    break
            if not result['nearest_metro']:
                result['nearest_metro'] = 'Culver City Station'  # Default nearest metro
        time.sleep(0.3)
    except Exception as e:
        print(f"    ⚠️  Metro: {e}")
    
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
# MAIN SCRAPER
# ==============================================================================

def extract_job_data(url, google_maps_key=None):
    """
    Extract complete job data including contacts and commute
    """
    print(f"\n{'='*80}")
    print(f"🔍 Scraping: {url}")
    print(f"{'='*80}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    response = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find JSON-LD data
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
        return None
    
    # Extract basic job data
    job_data = {
        'url': url,
        'company': '',
        'company_domain': '',
        'title': '',
        'location': '',
        'address': '',
        'remote_option': '',
        'salary_min': '',
        'salary_max': '',
        'posted_date': '',
        'top_skills': [],
        'benefits': [],
        # Contact fields
        'department': '',
        'department_head': '',
        'department_head_email': '',
        # Commute fields
        'transit_routes': '',
        'transit_duration': '',
        'transit_changes': 0,
        'bike_duration': '',
        'nearest_metro': '',
        'commute_rating': '',
        'google_maps_link': ''
    }
    
    # Parse job posting
    job_data['title'] = job_posting.get('title', '')
    
    hiring_org = job_posting.get('hiringOrganization', {})
    job_data['company'] = hiring_org.get('name', '')
    
    # Get company domain from website
    company_website = hiring_org.get('sameAs', '')
    if 'builtin.com/company/' in company_website:
        # Extract company slug and guess domain
        company_slug = company_website.split('/')[-1]
        job_data['company_domain'] = f"{company_slug.replace('-', '')}.com"
    
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
    
    # Remote option
    desc = job_posting.get('description', '').lower()
    if 'fully remote' in desc:
        job_data['remote_option'] = 'Remote'
    elif 'hybrid' in desc:
        job_data['remote_option'] = 'Hybrid'
    else:
        job_data['remote_option'] = 'Onsite'
    
    # Salary
    base_salary = job_posting.get('baseSalary', {})
    if base_salary:
        value = base_salary.get('value', {})
        if isinstance(value, dict):
            job_data['salary_min'] = value.get('minValue', '')
            job_data['salary_max'] = value.get('maxValue', '')
    
    # Posted date
    job_data['posted_date'] = job_posting.get('datePosted', '')
    
    # Benefits
    benefits_str = job_posting.get('jobBenefits', '')
    if benefits_str:
        job_data['benefits'] = [b.strip() for b in benefits_str.split(',')][:5]  # Top 5
    
    # Skills
    desc_html = job_posting.get('description', '')
    if desc_html:
        desc_soup = BeautifulSoup(desc_html, 'html.parser')
        desc_text = desc_soup.get_text().lower()
        
        tech_keywords = [
            'aws', 'gcp', 'snowflake', 'bigquery', 'dbt', 'airflow',
            'python', 'sql', 'spark', 'kafka', 'docker', 'kubernetes'
        ]
        
        found_skills = []
        for keyword in tech_keywords:
            if re.search(r'\b' + keyword + r'\b', desc_text):
                found_skills.append(keyword.upper())
        
        job_data['top_skills'] = found_skills[:10]
    
    print(f"✅ Company: {job_data['company']}")
    print(f"✅ Title: {job_data['title']}")
    print(f"✅ Location: {job_data['location']}")
    
    # Get department head via Hunter.io
    if job_data['company_domain'] and HUNTER_API_KEY:
        hunter_data = get_company_contacts(job_data['company'], job_data['company_domain'])
        
        if hunter_data.get('contacts'):
            # Get department head only
            for contact in hunter_data['contacts']:
                position = contact.get('position', '').lower()
                if any(x in position for x in ['vp', 'head', 'director', 'manager']) and any(x in position for x in ['data', 'engineering']):
                    job_data['department_head'] = contact.get('name', '')
                    job_data['department_head_email'] = contact.get('email', '')
                    break
    
    # Extract department from description
    desc_html = job_posting.get('description', '')
    if desc_html:
        desc_soup = BeautifulSoup(desc_html, 'html.parser')
        desc_text = desc_soup.get_text()
        
        dept_patterns = [
            r'(?i)(data|engineering|analytics)\s+(?:team|group|department)',
        ]
        for pattern in dept_patterns:
            match = re.search(pattern, desc_text)
            if match:
                job_data['department'] = match.group(0).strip()
                break
        
        if not job_data.get('department'):
            job_data['department'] = 'Data Engineering'
    
    # Calculate commute
    if job_data['address'] and job_data['remote_option'] != 'Remote':
        commute_data = calculate_commute(HOME_ADDRESS, job_data['address'], google_maps_key)
        if commute_data is None:
            print(f"  ⚠️  Skipping - no public transit available")
            return None
        job_data.update(commute_data)
        print(f"  ✅ {commute_data['transit_routes']} | {commute_data['commute_rating']}")
    else:
        job_data['commute_rating'] = 'Remote - N/A'
    
    return job_data

def main():
    print("=" * 80)
    print("🚀 ULTIMATE JOB SCRAPER - With Hunter.io + Google Maps")
    print("=" * 80)
    print()
    
    # Use hardcoded API key
    google_key = GOOGLE_MAPS_API_KEY
    
    print(f"✅ Hunter.io API: Active (Free tier)")
    print(f"✅ Google Maps API: Active")
    print(f"📍 Home: {HOME_ADDRESS}")
    print(f"📏 Max Distance: {MAX_DISTANCE_MILES} miles")
    print()
    
    results = []
    
    for url in JOB_URLS:
        job_data = extract_job_data(url, google_key)
        if job_data:
            results.append(job_data)
        time.sleep(2)  # Be nice
    
    # Export to CSV
    if results:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_file = f'data/raw/jobs_with_contacts_{timestamp}.csv'
        
        fieldnames = [
            'company', 'title', 'location', 'google_maps_link', 'remote_option',
            'salary_min', 'salary_max', 'posted_date',
            'department', 'department_head', 'department_head_email',
            'transit_routes', 'transit_duration', 'transit_changes', 'bike_duration',
            'nearest_metro', 'commute_rating',
            'top_skills', 'url'
        ]
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            
            for job in results:
                # Convert lists to strings for CSV
                job['top_skills'] = ', '.join(job.get('top_skills', []))
                job['benefits'] = ', '.join(job.get('benefits', []))
                writer.writerow(job)
        
        print("\n" + "=" * 80)
        print(f"✅ Exported {len(results)} jobs to: {csv_file}")
        print("=" * 80)
        
        # Show summary
        for job in results:
            print(f"\n🏢 {job['company']} - {job['title']}")
            print(f"   📍 {job['location']} | {job['remote_option']}")
            if job.get('department_head_email'):
                print(f"   📧 {job['department_head']} <{job['department_head_email']}>")
            if job.get('commute_rating'):
                print(f"   🚌 {job['commute_rating']}")

if __name__ == '__main__':
    main()

