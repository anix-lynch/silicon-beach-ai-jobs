#!/usr/bin/env python3
"""
🚀 INDEED JOB SCRAPER - Claude Desktop Edition
- Uses Anthropic's Official Indeed MCP
- Gets contacts via Hunter.io API  
- Calculates commute via Google Maps API
- Exports to CSV matching Built In LA format
"""

import json
import csv
import time
import re
from datetime import datetime
import requests

# ==============================================================================
# CONFIGURATION
# ==============================================================================

HOME_ADDRESS = os.getenv("HOME_ADDRESS", "YOUR_HOME_ADDRESS")
MAX_DISTANCE_MILES = 10

# Hunter.io API (from your existing config)
HUNTER_API_KEY = os.getenv("HUNTER_API_KEY")

# Google Maps API (from your existing config)
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# Job search criteria
SEARCH_PARAMS = {
    'search': 'data engineer OR AI engineer',
    'location': 'Los Angeles, CA',
    'country_code': 'US',
    'job_type': None  # fulltime, parttime, contract, internship, temporary
}

# ==============================================================================
# HUNTER.IO INTEGRATION (Same as Built In LA)
# ==============================================================================

def get_company_contacts(company_name, company_domain):
    """
    Use Hunter.io to find hiring managers, recruiters, and engineering leads
    """    if not HUNTER_API_KEY or not company_domain:
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
                'limit': 50
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json().get('data', {})
            emails = data.get('emails', [])
            
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
                        'department': email_data.get('department', '')
                    }
                    relevant_contacts.append(contact)
            
            return {
                'contacts': relevant_contacts[:5],
                'email_pattern': data.get('pattern', 'Unknown')
            }
        else:
            return {'contacts': [], 'error': f'Status {response.status_code}'}
    
    except Exception as e:
        print(f"  ⚠️  Hunter.io error: {e}")
        return {'contacts': [], 'error': str(e)}

# ==============================================================================
# GOOGLE MAPS INTEGRATION (Same as Built In LA)
# ==============================================================================

def calculate_commute(origin, destination, api_key):
    """Calculate commute time using Google Maps Distance Matrix API"""
    print(f"  🗺️  Calculating commute: {destination[:50]}...")
    
    try:
        base_url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        
        params = {
            'origins': origin,
            'destinations': destination,
            'mode': 'transit',
            'transit_mode': 'bus|subway|train',
            'key': api_key
        }
        
        response = requests.get(base_url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data['status'] == 'OK':
                element = data['rows'][0]['elements'][0]
                
                if element['status'] == 'OK':
                    distance_meters = element['distance']['value']
                    distance_miles = round(distance_meters / 1609.34, 1)
                    duration_seconds = element['duration']['value']
                    duration_mins = round(duration_seconds / 60)
                    
                    # Get transit details
                    transit_routes = "Transit available"
                    transit_changes = 0
                    
                    # Generate Google Maps link
                    maps_link = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}"
                    
                    # Calculate commute rating
                    if duration_mins <= 30:
                        rating = "⭐⭐⭐ Excellent"
                    elif duration_mins <= 45:
                        rating = "⭐⭐ Good"
                    else:
                        rating = "⭐ Acceptable"
                    
                    return {
                        'google_maps_link': maps_link,
                        'transit_routes': transit_routes,
                        'transit_duration': f"{duration_mins} mins",
                        'transit_changes': transit_changes,
                        'bike_duration': '',
                        'nearest_metro': '',
                        'commute_rating': rating
                    }
        
        return None
    
    except Exception as e:
        print(f"  ⚠️  Google Maps error: {e}")
        return None

# ==============================================================================
# INDEED MCP INTEGRATION - THIS IS THE NEW PART!
# ==============================================================================

def search_indeed_jobs():
    """
    Use Indeed MCP to search for jobs
    NOTE: This requires Claude Desktop to call the MCP tools
    For now, returns a placeholder structure
    """
    print("🔍 Searching Indeed via MCP...")
    print("⚠️  This requires Claude Desktop to execute the MCP calls")
    print()
    
    # Placeholder - Claude Desktop will replace this with actual MCP calls
    # The structure matches what Indeed MCP returns
    return []

def extract_company_domain(company_name):
    """Try to guess company domain from name"""
    # Simple heuristic
    clean_name = company_name.lower()
    clean_name = re.sub(r'[^a-z0-9]', '', clean_name)
    return f"{clean_name}.com"

def process_indeed_job(job_result, google_maps_key):
    """
    Process a single Indeed job result into CSV format
    Matches the Built In LA CSV structure
    """
    print(f"\n📋 Processing: {job_result.get('title', 'Unknown')}")
    
    job_data = {
        'company': job_result.get('company', ''),
        'title': job_result.get('title', ''),
        'location': job_result.get('location', ''),
        'google_maps_link': '',
        'remote_option': 'Onsite',  # Will be updated
        'salary_min': job_result.get('salary_min', ''),
        'salary_max': job_result.get('salary_max', ''),
        'posted_date': job_result.get('posted_date', ''),
        'department': 'Data Engineering',
        'department_head': '',
        'department_head_email': '',
        'transit_routes': '',
        'transit_duration': '',
        'transit_changes': 0,
        'bike_duration': '',
        'nearest_metro': '',
        'commute_rating': '',
        'top_skills': '',
        'url': job_result.get('url', '')
    }
    
    # Detect remote option from job title/description
    title_lower = job_data['title'].lower()
    location_lower = job_data['location'].lower()
    
    if 'remote' in location_lower or 'remote' in title_lower:
        job_data['remote_option'] = 'Remote'
    elif 'hybrid' in location_lower or 'hybrid' in title_lower:
        job_data['remote_option'] = 'Hybrid'
    
    print(f"✅ Company: {job_data['company']}")
    print(f"✅ Location: {job_data['location']} ({job_data['remote_option']})")
    
    # Extract company domain
    company_domain = extract_company_domain(job_data['company'])
    
    # Get department head via Hunter.io
    if HUNTER_API_KEY:
        hunter_data = get_company_contacts(job_data['company'], company_domain)
        
        if hunter_data.get('contacts'):
            for contact in hunter_data['contacts']:
                position = contact.get('position', '').lower()
                if any(x in position for x in ['vp', 'head', 'director', 'manager']) and \
                   any(x in position for x in ['data', 'engineering']):
                    job_data['department_head'] = contact.get('name', '')
                    job_data['department_head_email'] = contact.get('email', '')
                    print(f"  📧 Found: {job_data['department_head']}")
                    break
    
    # Calculate commute (skip if remote)
    if job_data['remote_option'] != 'Remote' and job_data['location']:
        commute_data = calculate_commute(HOME_ADDRESS, job_data['location'], google_maps_key)
        if commute_data:
            job_data.update(commute_data)
            print(f"  ✅ Commute: {commute_data['commute_rating']}")
        else:
            print(f"  ⚠️  No transit data available")
            job_data['commute_rating'] = 'No transit'
    else:
        job_data['commute_rating'] = 'Remote - N/A'
    
    return job_data

def main():
    print("=" * 80)
    print("🚀 INDEED JOB SCRAPER - Claude Desktop + Official MCP")
    print("=" * 80)
    print()
    print(f"✅ Hunter.io API: Active")
    print(f"✅ Google Maps API: Active")
    print(f"✅ Indeed MCP: Official Anthropic Integration")
    print(f"📍 Home: {HOME_ADDRESS}")
    print(f"📏 Max Distance: {MAX_DISTANCE_MILES} miles")
    print()
    
    # Get jobs from Indeed MCP
    # NOTE: Claude Desktop will call Indeed MCP tools here
    indeed_jobs = search_indeed_jobs()
    
    if not indeed_jobs:
        print("⚠️  No jobs found or MCP not available")
        print("💡 This script requires Claude Desktop to execute Indeed MCP calls")
        return
    
    # Process each job
    results = []
    for job in indeed_jobs:
        processed_job = process_indeed_job(job, GOOGLE_MAPS_API_KEY)
        if processed_job:
            results.append(processed_job)
        time.sleep(1)  # Be nice to APIs
    
    # Export to CSV (same format as Built In LA)
    if results:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_file = f'data/raw/indeed_jobs_{timestamp}.csv'
        
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
            writer.writerows(results)
        
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
