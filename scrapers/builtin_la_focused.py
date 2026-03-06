#!/usr/bin/env python3
"""
Scrape Built In LA for data engineering jobs near Culver City
Uses pre-identified job URLs + Google Maps Distance Matrix API
"""

import json
import csv
import os
import time
import re
from datetime import datetime

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

# Job URLs from Firecrawl search results - high match for your requirements
JOB_URLS = [
    "https://www.builtinla.com/job/senior-data-engineer/7584766",  # Button - AWS, Airflow, dbt
    "https://www.builtinla.com/job/staff-data-engineer/7505495",  # Bestow
    "https://www.builtinla.com/job/staff-data-engineer/6763507",  # Circle - AWS, GCP, DBT
    "https://www.builtinla.com/job/manager-data-engineering/7046921",  # Circle - AWS, GCP, Airflow, DBT
    "https://www.builtinla.com/job/data-engineer/6212211",  # Q-Centrix - AWS, GCP, Snowflake, BigQuery
    "https://www.builtinla.com/job/data-engineer/6934992",  # Alo Yoga - Beverly Hills
    "https://www.builtinla.com/job/senior-data-engineer/2276480",  # Alo Yoga Staff - BigQuery, dbt, Snowflake, Airflow
]

# Keywords for enhanced matching
TECH_KEYWORDS = {
    'aws': ['aws', 'amazon web services', 'ec2', 's3', 'lambda', 'redshift', 'glue', 'emr', 'kinesis'],
    'gcp': ['gcp', 'google cloud', 'bigquery', 'dataflow', 'pub/sub', 'cloud functions', 'composer'],
    'snowflake': ['snowflake'],
    'dbt': ['dbt', 'data build tool'],
    'vector_db': ['elasticsearch', 'opensearch', 'alloydb', 'vector database', 'pinecone', 'weaviate'],
    'ml_ai': ['rag', 'semantic search', 'embeddings', 'llm', 'machine learning', 'ml ops']
}

def calculate_distance(origin, destination, api_key):
    """
    Calculate distance using Google Maps Distance Matrix API
    Returns distance in miles and transit options
    """
    base_url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    
    # Try driving first
    params = {
        'origins': origin,
        'destinations': destination,
        'units': 'imperial',
        'key': api_key,
        'mode': 'driving'
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=10)
        data = response.json()
        
        result = {
            'distance_miles': None,
            'distance_text': 'Unknown',
            'drive_duration': 'Unknown',
            'transit_duration': 'Unknown',
            'bike_duration': 'Unknown',
            'status': 'ERROR'
        }
        
        if data['status'] == 'OK':
            element = data['rows'][0]['elements'][0]
            if element['status'] == 'OK':
                distance_value = element['distance']['value']  # in meters
                distance_miles = distance_value * 0.000621371
                
                result['distance_miles'] = round(distance_miles, 2)
                result['distance_text'] = element['distance']['text']
                result['drive_duration'] = element['duration']['text']
                result['status'] = 'OK'
                
                # Try transit
                params['mode'] = 'transit'
                transit_response = requests.get(base_url, params=params, timeout=10)
                transit_data = transit_response.json()
                if transit_data['status'] == 'OK':
                    transit_element = transit_data['rows'][0]['elements'][0]
                    if transit_element['status'] == 'OK':
                        result['transit_duration'] = transit_element['duration']['text']
                
                # Try bicycling
                params['mode'] = 'bicycling'
                bike_response = requests.get(base_url, params=params, timeout=10)
                bike_data = bike_response.json()
                if bike_data['status'] == 'OK':
                    bike_element = bike_data['rows'][0]['elements'][0]
                    if bike_element['status'] == 'OK':
                        result['bike_duration'] = bike_element['duration']['text']
        
        return result
        
    except Exception as e:
        print(f"⚠️  Error calculating distance: {e}")
        return result

def extract_tech_stack(text):
    """Extract relevant tech stack mentions from job description"""
    text_lower = text.lower()
    found_tech = []
    
    for category, keywords in TECH_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                found_tech.append(keyword)
    
    return ', '.join(set(found_tech))

def scrape_job_with_requests(url):
    """
    Scrape job details using requests + BeautifulSoup
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract job details
        job_data = {
            'url': url,
            'company': '',
            'title': '',
            'location': '',
            'remote_option': 'Unknown',
            'salary': '',
            'description': '',
            'tech_stack': ''
        }
        
        # Company name
        company_elem = soup.find('a', {'data-id': 'company-title-link'})
        if company_elem:
            job_data['company'] = company_elem.text.strip()
        
        # Job title
        title_elem = soup.find('h1', class_=re.compile('job.*title|title.*job', re.I))
        if not title_elem:
            title_elem = soup.find('h1')
        if title_elem:
            job_data['title'] = title_elem.text.strip()
        
        # Location
        location_elem = soup.find(string=re.compile('Location|Office', re.I))
        if location_elem:
            location_parent = location_elem.find_parent()
            if location_parent:
                job_data['location'] = location_parent.text.replace('Location:', '').strip()
        
        # Check for remote
        page_text = soup.get_text().lower()
        if 'remote' in page_text:
            if 'hybrid' in page_text:
                job_data['remote_option'] = 'Hybrid'
            else:
                job_data['remote_option'] = 'Remote'
        else:
            job_data['remote_option'] = 'Onsite'
        
        # Salary
        salary_elem = soup.find(string=re.compile(r'\$\d{2,3}[,k]', re.I))
        if salary_elem:
            job_data['salary'] = salary_elem.strip()
        
        # Description
        desc_elem = soup.find('div', class_=re.compile('description|content', re.I))
        if desc_elem:
            job_data['description'] = desc_elem.get_text(separator=' ', strip=True)[:500]
        
        # Tech stack
        job_data['tech_stack'] = extract_tech_stack(soup.get_text())
        
        return job_data
        
    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
        return None

def main():
    """Main execution"""
    print("=" * 80)
    print("🚀 Built In LA Data Engineering Job Scraper")
    print("=" * 80)
    print(f"\n📍 Home: {HOME_ADDRESS}")
    print(f"📏 Max Distance: {MAX_DISTANCE_MILES} miles")
    print(f"🎯 Target Tech: AWS, GCP, Snowflake, BigQuery, dbt, Vector DBs, RAG\n")
    
    # Get API key
    google_maps_api_key = input("🔑 Enter your Google Maps API key: ").strip()
    
    if not google_maps_api_key:
        print("❌ Google Maps API key required!")
        return
    
    print(f"\n🔍 Scraping {len(JOB_URLS)} jobs from Built In LA...")
    print("-" * 80)
    
    results = []
    
    for i, url in enumerate(JOB_URLS, 1):
        print(f"\n[{i}/{len(JOB_URLS)}] Scraping: {url}")
        
        job_data = scrape_job_with_requests(url)
        
        if job_data:
            print(f"  ✓ Company: {job_data['company']}")
            print(f"  ✓ Title: {job_data['title']}")
            print(f"  ✓ Location: {job_data['location']}")
            print(f"  ✓ Remote: {job_data['remote_option']}")
            
            # Calculate distance if location is available
            if job_data['location'] and 'remote' not in job_data['location'].lower():
                location_query = f"{job_data['location']}, California"
                print(f"  📍 Calculating distance from {location_query}...")
                
                distance_info = calculate_distance(HOME_ADDRESS, location_query, google_maps_api_key)
                job_data.update(distance_info)
                
                if distance_info['distance_miles']:
                    print(f"  📏 Distance: {distance_info['distance_miles']} miles")
                    print(f"  🚗 Drive: {distance_info['drive_duration']}")
                    if distance_info['transit_duration'] != 'Unknown':
                        print(f"  🚌 Transit: {distance_info['transit_duration']}")
                    if distance_info['bike_duration'] != 'Unknown':
                        print(f"  🚴 Bike: {distance_info['bike_duration']}")
                    
                    # Filter by distance
                    if distance_info['distance_miles'] <= MAX_DISTANCE_MILES:
                        print(f"  ✅ Within {MAX_DISTANCE_MILES} mile radius!")
                        results.append(job_data)
                    else:
                        print(f"  ❌ Too far ({distance_info['distance_miles']} miles)")
                
                time.sleep(0.5)  # Rate limiting
            elif 'remote' in job_data.get('remote_option', '').lower():
                print(f"  ✅ Remote position - adding to results")
                job_data.update({
                    'distance_miles': 0,
                    'distance_text': 'Remote',
                    'drive_duration': 'N/A',
                    'transit_duration': 'N/A',
                    'bike_duration': 'N/A',
                    'status': 'Remote'
                })
                results.append(job_data)
        
        time.sleep(1)  # Be nice to the server
    
    # Export results
    if results:
        print("\n" + "=" * 80)
        print(f"✅ Found {len(results)} matching jobs!")
        print("=" * 80)
        
        # Ensure output directory exists
        os.makedirs('data/raw', exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_file = f'data/raw/la_data_jobs_{timestamp}.csv'
        json_file = f'data/raw/la_data_jobs_{timestamp}.json'
        
        # Export to CSV
        fieldnames = [
            'company', 'title', 'location', 'remote_option',
            'distance_miles', 'distance_text', 
            'drive_duration', 'transit_duration', 'bike_duration',
            'salary', 'tech_stack', 'url', 'description'
        ]
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        # Export to JSON
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 CSV: {csv_file}")
        print(f"📄 JSON: {json_file}")
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 SUMMARY")
        print("=" * 80)
        
        for job in results:
            print(f"\n🏢 {job['company']} - {job['title']}")
            print(f"   📍 {job['location']} ({job['remote_option']})")
            if job.get('distance_miles'):
                print(f"   📏 {job['distance_miles']} mi | 🚗 {job['drive_duration']}")
                if job.get('transit_duration') != 'Unknown':
                    print(f"   🚌 {job['transit_duration']} | 🚴 {job.get('bike_duration', 'N/A')}")
            print(f"   🔗 {job['url']}")
            if job['tech_stack']:
                print(f"   💻 {job['tech_stack'][:100]}...")
    else:
        print("\n❌ No matching jobs found within your criteria")
    
    print("\n" + "=" * 80)
    print("✨ Done!")
    print("=" * 80)

if __name__ == '__main__':
    main()

