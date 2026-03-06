#!/usr/bin/env python3
"""
Comprehensive Built In LA scraper that:
1. Scrapes the main data engineering jobs page
2. Gets ALL job listings
3. Filters by your tech stack
4. Calculates distances
5. Exports to CSV with transit options
"""

import json
import csv
import os
import time
import re
from datetime import datetime
from urllib.parse import urljoin

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Installing required packages...")
    os.system("pip install requests beautifulsoup4")
    import requests
    from bs4 import BeautifulSoup

# Configuration
HOME_ADDRESS = os.getenv("HOME_ADDRESS", "YOUR_HOME_ADDRESS")
MAX_DISTANCE_MILES = 10
BASE_URL = "https://www.builtinla.com"

# Your ideal tech stack
PRIORITY_TECH = {
    'aws': ['aws', 'amazon web services', 'ec2', 's3', 'lambda', 'redshift', 'glue', 'emr'],
    'gcp': ['gcp', 'google cloud', 'bigquery', 'dataflow', 'pub/sub', 'cloud functions'],
    'snowflake': ['snowflake'],
    'dbt': ['dbt', 'data build tool'],
    'vector_db': ['elasticsearch', 'opensearch', 'alloydb', 'pinecone', 'weaviate', 'vector database'],
    'ml_ai': ['rag', 'semantic search', 'embeddings', 'llm']
}

def calculate_distance_all_modes(origin, destination, api_key):
    """Get distance via car, transit (with bus/train details), and bike"""
    base_url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    
    result = {
        'distance_miles': None,
        'drive_duration': 'Unknown',
        'transit_duration': 'Unknown',
        'transit_details': 'Unknown',
        'transit_changes': 0,
        'bike_duration': 'Unknown',
        'commute_rating': 'Unknown'
    }
    
    modes = ['driving', 'transit', 'bicycling']
    
    for mode in modes:
        try:
            params = {
                'origins': origin,
                'destinations': destination,
                'units': 'imperial',
                'key': api_key,
                'mode': mode
            }
            
            # For transit, request departure time for accurate schedules
            if mode == 'transit':
                params['departure_time'] = 'now'
                params['transit_mode'] = 'bus|rail'  # Culver CityBus, Big Blue Bus, Metro
            
            response = requests.get(base_url, params=params, timeout=10)
            data = response.json()
            
            if data['status'] == 'OK':
                element = data['rows'][0]['elements'][0]
                if element['status'] == 'OK':
                    if mode == 'driving':
                        distance_meters = element['distance']['value']
                        result['distance_miles'] = round(distance_meters * 0.000621371, 2)
                        result['drive_duration'] = element['duration']['text']
                    
                    elif mode == 'transit':
                        result['transit_duration'] = element['duration']['text']
                        
                        # Extract transit details (bus lines, train lines)
                        # Note: Distance Matrix doesn't give full route details
                        # But we can get duration which is most important
                        duration_mins = element['duration']['value'] / 60
                        
                        # Parse if we can get transit info from response
                        transit_info = []
                        if 'transit_details' in element:
                            for step in element.get('transit_details', {}).get('lines', []):
                                line_name = step.get('short_name', '')
                                vehicle = step.get('vehicle', {}).get('type', '')
                                transit_info.append(f"{vehicle} {line_name}")
                        
                        if transit_info:
                            result['transit_details'] = ' → '.join(transit_info)
                            result['transit_changes'] = len(transit_info) - 1
                        else:
                            result['transit_details'] = f"{int(duration_mins)} min commute"
                            # Estimate transfers based on duration
                            if duration_mins > 45:
                                result['transit_changes'] = 2
                            elif duration_mins > 25:
                                result['transit_changes'] = 1
                            else:
                                result['transit_changes'] = 0
                    
                    elif mode == 'bicycling':
                        result['bike_duration'] = element['duration']['text']
            
            time.sleep(0.3)  # Rate limiting
        except Exception as e:
            print(f"  ⚠️  {mode} failed: {e}")
    
    # Rate the commute based on your preferences
    # Your criteria: < 40 mins one way, minimal transfers
    if result['transit_duration'] != 'Unknown':
        try:
            # Parse duration (e.g., "35 mins" or "1 hour 5 mins")
            duration_str = result['transit_duration'].lower()
            minutes = 0
            if 'hour' in duration_str:
                hours = int(duration_str.split('hour')[0].strip().split()[-1])
                minutes += hours * 60
                if 'min' in duration_str:
                    mins = int(duration_str.split('hour')[1].split('min')[0].strip())
                    minutes += mins
            elif 'min' in duration_str:
                minutes = int(duration_str.split('min')[0].strip().split()[-1])
            
            transfers = result['transit_changes']
            
            # Rate commute
            if minutes <= 40 and transfers <= 1:
                result['commute_rating'] = '⭐⭐⭐ Excellent'
            elif minutes <= 40 and transfers == 2:
                result['commute_rating'] = '⭐⭐ Good (2 transfers)'
            elif minutes <= 50 and transfers <= 1:
                result['commute_rating'] = '⭐⭐ Good (bit long)'
            elif minutes > 50 or transfers > 2:
                result['commute_rating'] = '⭐ Poor (too long/many transfers)'
            else:
                result['commute_rating'] = '⭐⭐ Acceptable'
        except:
            result['commute_rating'] = 'Unknown'
    
    return result

def score_job(text):
    """Score job based on tech stack match"""
    text_lower = text.lower()
    score = 0
    matched_tech = []
    
    for category, keywords in PRIORITY_TECH.items():
        for keyword in keywords:
            if keyword in text_lower:
                score += 1
                matched_tech.append(keyword)
    
    return score, ', '.join(set(matched_tech))

def scrape_jobs_list(max_pages=3):
    """Scrape all data engineering jobs from Built In LA listing pages"""
    print("🔍 Scraping job listings from Built In LA...\n")
    
    jobs = []
    
    for page in range(1, max_pages + 1):
        url = f"{BASE_URL}/jobs/data-analytics/data-engineering?page={page}"
        print(f"📄 Page {page}: {url}")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all job cards
            job_cards = soup.find_all('div', class_=re.compile('job.*card|company.*card', re.I))
            
            if not job_cards:
                # Try alternative selectors
                job_cards = soup.find_all('a', href=re.compile(r'/job/'))
            
            print(f"  Found {len(job_cards)} job listings")
            
            for card in job_cards:
                try:
                    # Extract job URL
                    link = card.get('href') if card.name == 'a' else card.find('a', href=True)
                    if isinstance(link, str):
                        job_url = urljoin(BASE_URL, link)
                    elif link:
                        job_url = urljoin(BASE_URL, link.get('href', ''))
                    else:
                        continue
                    
                    # Extract basic info from card
                    company = card.find(class_=re.compile('company', re.I))
                    title = card.find(class_=re.compile('title', re.I))
                    location = card.find(class_=re.compile('location', re.I))
                    
                    job_info = {
                        'url': job_url,
                        'company': company.get_text(strip=True) if company else 'Unknown',
                        'title': title.get_text(strip=True) if title else 'Unknown',
                        'location': location.get_text(strip=True) if location else 'Unknown',
                        'card_text': card.get_text()
                    }
                    
                    # Score based on tech stack
                    score, tech = score_job(job_info['card_text'])
                    job_info['tech_score'] = score
                    job_info['tech_preview'] = tech
                    
                    # Only add if score > 0 (has relevant tech)
                    if score > 0:
                        jobs.append(job_info)
                
                except Exception as e:
                    print(f"  ⚠️  Error parsing card: {e}")
            
            time.sleep(2)  # Be nice to the server
            
        except Exception as e:
            print(f"  ❌ Error scraping page {page}: {e}")
    
    # Remove duplicates by URL
    seen_urls = set()
    unique_jobs = []
    for job in jobs:
        if job['url'] not in seen_urls:
            seen_urls.add(job['url'])
            unique_jobs.append(job)
    
    print(f"\n✅ Found {len(unique_jobs)} unique jobs with relevant tech stack")
    
    # Sort by tech score
    unique_jobs.sort(key=lambda x: x['tech_score'], reverse=True)
    
    return unique_jobs

def scrape_job_details(url):
    """Get detailed job description"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get full description
        desc_elem = soup.find('div', class_=re.compile('description|content|detail', re.I))
        description = desc_elem.get_text(separator=' ', strip=True) if desc_elem else ''
        
        # Look for remote/hybrid
        page_text = soup.get_text().lower()
        if 'fully remote' in page_text or 'work from home' in page_text:
            remote_option = 'Remote'
        elif 'hybrid' in page_text:
            remote_option = 'Hybrid'
        else:
            remote_option = 'Onsite'
        
        # Salary
        salary = ''
        salary_elem = soup.find(string=re.compile(r'\$\d{2,3}[,k]'))
        if salary_elem:
            salary = salary_elem.strip()
        
        return {
            'description': description[:1000],
            'remote_option': remote_option,
            'salary': salary
        }
    except Exception as e:
        print(f"    ⚠️  Error getting details: {e}")
        return {
            'description': '',
            'remote_option': 'Unknown',
            'salary': ''
        }

def main():
    print("=" * 80)
    print("🚀 Built In LA Comprehensive Data Engineering Job Scraper")
    print("=" * 80)
    print(f"\n📍 Home: {HOME_ADDRESS}")
    print(f"📏 Max Distance: {MAX_DISTANCE_MILES} miles")
    print(f"🎯 Tech Stack: AWS, GCP, Snowflake, BigQuery, dbt, Vector DBs, RAG")
    print(f"🚗 Will check: Driving, Transit, and Bike commute times\n")
    
    # Get API key
    google_maps_api_key = input("🔑 Enter your Google Maps API key: ").strip()
    
    if not google_maps_api_key:
        print("❌ API key required!")
        return
    
    # Ask how many pages to scrape
    try:
        max_pages = int(input("📄 How many pages to scrape? (1-5): ").strip() or "2")
        max_pages = min(max(max_pages, 1), 5)
    except:
        max_pages = 2
    
    print("\n" + "=" * 80)
    
    # Step 1: Scrape job listings
    jobs = scrape_jobs_list(max_pages=max_pages)
    
    if not jobs:
        print("\n❌ No jobs found!")
        return
    
    print("\n" + "=" * 80)
    print("📊 Processing jobs...")
    print("=" * 80 + "\n")
    
    # Step 2: Get details and calculate distances
    final_results = []
    
    for i, job in enumerate(jobs[:30], 1):  # Limit to top 30 to save API calls
        print(f"[{i}/{min(30, len(jobs))}] {job['company']} - {job['title']}")
        print(f"  🔗 {job['url']}")
        print(f"  ⭐ Tech Score: {job['tech_score']} | 💻 {job['tech_preview'][:80]}")
        
        # Get detailed info
        details = scrape_job_details(job['url'])
        job.update(details)
        
        print(f"  📋 Remote: {job['remote_option']}")
        
        # Calculate distance if not fully remote
        if job['remote_option'] != 'Remote' and job['location'] != 'Unknown':
            location_query = f"{job['location']}, California"
            print(f"  📍 Calculating distance from {location_query}...")
            
            distance_info = calculate_distance_all_modes(HOME_ADDRESS, location_query, google_maps_api_key)
            job.update(distance_info)
            
            if distance_info['distance_miles']:
                print(f"  📏 {distance_info['distance_miles']} miles")
                print(f"  🚗 Drive: {distance_info['drive_duration']}")
                if distance_info['transit_duration'] != 'Unknown':
                    print(f"  🚌 Transit: {distance_info['transit_duration']} ({distance_info['transit_changes']} transfers)")
                    print(f"     {distance_info['commute_rating']}")
                if distance_info['bike_duration'] != 'Unknown':
                    print(f"  🚴 Bike: {distance_info['bike_duration']}")
                
                if distance_info['distance_miles'] <= MAX_DISTANCE_MILES:
                    print(f"  ✅ Within range!")
                    final_results.append(job)
                else:
                    print(f"  ❌ Too far")
        else:
            print(f"  ✅ Remote - added!")
            job['distance_miles'] = 0
            job['drive_duration'] = 'N/A'
            final_results.append(job)
        
        print()
        time.sleep(1.5)  # Rate limiting
    
    # Export results
    if final_results:
        print("=" * 80)
        print(f"✅ {len(final_results)} jobs match your criteria!")
        print("=" * 80 + "\n")
        
        os.makedirs('data/raw', exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_file = f'data/raw/builtinla_jobs_{timestamp}.csv'
        
        fieldnames = [
            'company', 'title', 'location', 'remote_option',
            'distance_miles', 'drive_duration', 
            'transit_duration', 'transit_changes', 'commute_rating',
            'bike_duration', 'tech_score', 'tech_preview', 
            'salary', 'url', 'description'
        ]
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(final_results)
        
        print(f"📄 Exported to: {csv_file}\n")
        
        # Summary
        print("=" * 80)
        print("📊 TOP MATCHES")
        print("=" * 80 + "\n")
        
        for job in sorted(final_results, key=lambda x: x['tech_score'], reverse=True)[:10]:
            print(f"🏢 {job['company']}")
            print(f"   {job['title']}")
            print(f"   📍 {job['location']} | {job['remote_option']}")
            if job.get('distance_miles'):
                print(f"   📏 {job['distance_miles']} mi | 🚗 {job['drive_duration']}", end='')
                if job.get('transit_duration') and job['transit_duration'] != 'Unknown':
                    print(f" | 🚌 {job['transit_duration']} ({job.get('transit_changes', 0)} transfers)", end='')
                print()
                if job.get('commute_rating') and job['commute_rating'] != 'Unknown':
                    print(f"   {job['commute_rating']}")
            print(f"   ⭐ Score: {job['tech_score']} | 💻 {job['tech_preview'][:60]}")
            print(f"   🔗 {job['url']}\n")
    else:
        print("\n❌ No jobs found within your criteria")
    
    print("=" * 80)
    print("✨ Done!")
    print("=" * 80)

if __name__ == '__main__':
    main()

