#!/usr/bin/env python3
"""
Silicon Beach Job Finder using Perplexity AI
Safe, legal job search using AI-powered web search (no scraping!)
Focuses on tech companies within 5 miles of Culver City
"""

import requests
import csv
import time
from datetime import datetime

# ==============================================================================
# CONFIG
# ==============================================================================

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
HOME_ADDRESS = "YOUR_HOME_ADDRESS"

# Silicon Beach companies within 5 miles of Culver City
SILICON_BEACH_COMPANIES = [
    # Playa Vista (2-3 miles)
    {
        "name": "Google/YouTube",
        "location": "Playa Vista, CA",
        "address": "12777 W Jefferson Blvd, Los Angeles, CA 90066",
        "career_url": "https://careers.google.com",
        "priority": "HIGH"
    },
    {
        "name": "Snap Inc.",
        "location": "Santa Monica, CA",
        "address": "2772 Donald Douglas Loop N, Santa Monica, CA 90405",
        "career_url": "https://snap.com/en-US/jobs",
        "priority": "HIGH"
    },
    {
        "name": "Meta",
        "location": "Playa Vista, CA",
        "address": "5400 Beethoven St, Los Angeles, CA 90066",
        "career_url": "https://www.metacareers.com",
        "priority": "HIGH"
    },
    {
        "name": "Amazon",
        "location": "Santa Monica, CA",
        "address": "1620 26th St, Santa Monica, CA 90404",
        "career_url": "https://amazon.jobs",
        "priority": "HIGH"
    },
    {
        "name": "TikTok",
        "location": "Culver City, CA",
        "address": "5800 Bristol Pkwy, Culver City, CA 90230",
        "career_url": "https://careers.tiktok.com",
        "priority": "HIGH"
    },
    {
        "name": "Hulu",
        "location": "Santa Monica, CA",
        "address": "2500 Broadway, Santa Monica, CA 90404",
        "career_url": "https://www.hulu.com/jobs",
        "priority": "HIGH"
    },
    {
        "name": "Disney Streaming",
        "location": "Santa Monica, CA",
        "address": "2500 Broadway, Santa Monica, CA 90404",
        "career_url": "https://jobs.disneycareers.com",
        "priority": "HIGH"
    },
    {
        "name": "Riot Games",
        "location": "West LA, CA",
        "address": "12333 W Olympic Blvd, Los Angeles, CA 90064",
        "career_url": "https://www.riotgames.com/en/work-with-us",
        "priority": "HIGH"
    },
    {
        "name": "Blizzard Entertainment",
        "location": "Santa Monica, CA",
        "address": "1322 2nd St, Santa Monica, CA 90401",
        "career_url": "https://careers.blizzard.com",
        "priority": "HIGH"
    },
    {
        "name": "Electronic Arts (EA)",
        "location": "Playa Vista, CA",
        "address": "12790 W Jefferson Blvd, Los Angeles, CA 90066",
        "career_url": "https://www.ea.com/careers",
        "priority": "MEDIUM"
    },
    {
        "name": "Yahoo",
        "location": "Playa Vista, CA",
        "address": "Playa Vista, CA 90094",
        "career_url": "https://www.yahooinc.com/careers",
        "priority": "MEDIUM"
    },
    {
        "name": "Belkin",
        "location": "Playa Vista, CA",
        "address": "12045 E Waterfront Dr, Playa Vista, CA 90094",
        "career_url": "https://www.belkin.com/careers",
        "priority": "MEDIUM"
    },
    {
        "name": "SKIMS",
        "location": "Los Angeles, CA",
        "address": "Downtown LA",
        "career_url": "https://skims.com/pages/careers",
        "priority": "MEDIUM"
    },
    {
        "name": "Centerfield",
        "location": "Playa Vista, CA",
        "address": "12777 W Jefferson Blvd, Los Angeles, CA 90066",
        "career_url": "https://www.centerfield.com/careers",
        "priority": "MEDIUM"
    },
    # El Segundo (5-8 miles - aerospace heavy)
    {
        "name": "SpaceX",
        "location": "Hawthorne, CA",
        "address": "1 Rocket Rd, Hawthorne, CA 90250",
        "career_url": "https://www.spacex.com/careers",
        "priority": "MEDIUM"
    },
]

# ==============================================================================
# PERPLEXITY AI SEARCH
# ==============================================================================

def search_jobs_perplexity(company_name, location):
    """
    Use Perplexity AI to search for current job openings
    This is SAFE - it's just searching the web, not scraping
    """
    print(f"\n🔍 Searching: {company_name} ({location})")
    
    try:
        query = f"""Does {company_name} in {location} have any current job openings for:
        - Data Engineer
        - AI Engineer / ML Engineer
        - Data Analyst
        - Analytics Engineer
        
        For each open position, provide:
        1. Job title
        2. Exact office location/address
        3. Salary range (if available)
        4. Whether it's remote/hybrid/onsite
        5. Direct application URL
        
        Only include jobs that are currently accepting applications. Be concise."""
        
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.1-sonar-small-128k-online",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful job search assistant. Provide factual, current information about job openings from official career pages and job boards. Be concise and structured."
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            "max_tokens": 500,
            "temperature": 0.2,
            "return_citations": True
        }
        
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=payload,
            timeout=20
        )
        
        if response.status_code == 200:
            data = response.json()
            answer = data['choices'][0]['message']['content']
            citations = data.get('citations', [])
            
            print(f"✅ Result:")
            print(answer)
            
            if citations:
                print(f"\n📎 Sources:")
                for cite in citations[:3]:
                    print(f"   - {cite}")
            
            return {
                'company': company_name,
                'location': location,
                'search_result': answer,
                'sources': ', '.join(citations[:3]) if citations else ''
            }
        else:
            print(f"❌ Error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

# ==============================================================================
# CALCULATE COMMUTE
# ==============================================================================

def calculate_commute(destination_address):
    """Quick commute calculation"""
    try:
        url = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            'origin': HOME_ADDRESS,
            'destination': destination_address,
            'mode': 'transit',
            'transit_mode': 'bus|rail',
            'departure_time': 'now',
            'key': GOOGLE_MAPS_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data['status'] == 'OK' and data.get('routes'):
            route = data['routes'][0]['legs'][0]
            duration = route['duration']['text']
            
            # Extract bus/metro lines
            transit_routes = []
            for step in route['steps']:
                if step.get('travel_mode') == 'TRANSIT':
                    transit = step.get('transit_details', {})
                    line = transit.get('line', {})
                    vehicle = line.get('vehicle', {}).get('type', '')
                    line_name = line.get('short_name') or line.get('name', '')
                    
                    if vehicle == 'BUS':
                        transit_routes.append(f"Bus {line_name}")
                    elif vehicle in ['SUBWAY', 'HEAVY_RAIL', 'METRO_RAIL']:
                        transit_routes.append(f"Metro {line_name}")
            
            return {
                'transit_duration': duration,
                'transit_routes': ' → '.join(transit_routes) if transit_routes else 'Transit available',
                'google_maps_link': f"https://www.google.com/maps/dir/?api=1&origin={HOME_ADDRESS.replace(' ', '+')}&destination={destination_address.replace(' ', '+')}"
            }
        else:
            return {
                'transit_duration': 'No transit',
                'transit_routes': 'No public transit',
                'google_maps_link': f"https://www.google.com/maps/dir/?api=1&origin={HOME_ADDRESS.replace(' ', '+')}&destination={destination_address.replace(' ', '+')}"
            }
    except:
        return {
            'transit_duration': 'Unknown',
            'transit_routes': 'Unknown',
            'google_maps_link': ''
        }

# ==============================================================================
# MAIN
# ==============================================================================

def main():
    print("=" * 80)
    print("🏖️  SILICON BEACH JOB FINDER - Powered by Perplexity AI")
    print("=" * 80)
    print()
    print(f"📍 Your location: {HOME_ADDRESS}")
    print(f"🏢 Searching {len(SILICON_BEACH_COMPANIES)} companies in Silicon Beach")
    print()
    
    results = []
    
    # Search each company
    for i, company in enumerate(SILICON_BEACH_COMPANIES, 1):
        print(f"\n[{i}/{len(SILICON_BEACH_COMPANIES)}] {company['priority']} priority")
        
        # Get commute info
        commute = calculate_commute(company['address'])
        time.sleep(1)
        
        # Search for jobs
        job_result = search_jobs_perplexity(company['name'], company['location'])
        
        if job_result:
            job_result.update({
                'address': company['address'],
                'career_url': company['career_url'],
                'priority': company['priority'],
                **commute
            })
            results.append(job_result)
        
        # Rate limit - be nice to APIs
        time.sleep(3)
        
        # Progress update
        if i % 5 == 0:
            print(f"\n✅ Progress: Searched {i}/{len(SILICON_BEACH_COMPANIES)} companies...")
    
    # Export results
    if results:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_file = f'data/raw/silicon_beach_jobs_{timestamp}.csv'
        
        fieldnames = [
            'company', 'location', 'address', 'priority',
            'transit_duration', 'transit_routes', 'google_maps_link',
            'search_result', 'sources', 'career_url'
        ]
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        print("\n" + "=" * 80)
        print(f"✅ Exported {len(results)} company searches to: {csv_file}")
        print("=" * 80)
        
        # Summary
        print("\n📊 SUMMARY:")
        for result in results:
            print(f"\n🏢 {result['company']}")
            print(f"   📍 {result['location']} | {result['transit_duration']}")
            print(f"   🚌 {result['transit_routes']}")
            print(f"   🔗 {result['career_url']}")
            if "no current" not in result['search_result'].lower() and "not currently" not in result['search_result'].lower():
                print(f"   ✅ HAS OPENINGS!")
    else:
        print("\n❌ No results found!")

if __name__ == '__main__':
    main()

