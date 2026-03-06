#!/usr/bin/env python3
"""
Silicon Beach Department Head Finder
Uses Firecrawl to search LinkedIn publicly + Hunter.io to guess emails
100% FREE - No API signups needed!
"""

import requests
import csv
import time
import re
from datetime import datetime

# ==============================================================================
# CONFIG
# ==============================================================================

FIRECRAWL_API_KEY = "fc-4d8f0ec8ff9b49eb8acf8c19b0d356d7"  # From your .env
HUNTER_API_KEY = os.getenv("HUNTER_API_KEY")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
HOME_ADDRESS = os.getenv("HOME_ADDRESS", "YOUR_HOME_ADDRESS")

# LA Tech Companies - Organized by area, within 1 hour transit from Culver City
LA_TECH_COMPANIES = [
    # ==== SILICON BEACH (Playa Vista / Santa Monica / Venice) - 20-45 mins ====
    {
        "name": "TikTok",
        "domain": "tiktok.com",
        "location": "Culver City, CA",
        "address": "5800 Bristol Pkwy, Culver City, CA 90230",
        "career_url": "https://careers.tiktok.com",
        "area": "Culver City"
    },
    {
        "name": "Snap Inc.",
        "domain": "snap.com",
        "location": "Santa Monica, CA",
        "address": "2772 Donald Douglas Loop N, Santa Monica, CA 90405",
        "career_url": "https://snap.com/en-US/jobs",
        "area": "Santa Monica"
    },
    {
        "name": "Amazon",
        "domain": "amazon.com",
        "location": "Santa Monica, CA",
        "address": "1620 26th St, Santa Monica, CA 90404",
        "career_url": "https://amazon.jobs",
        "area": "Santa Monica"
    },
    {
        "name": "Riot Games",
        "domain": "riotgames.com",
        "location": "West LA, CA",
        "address": "12333 W Olympic Blvd, Los Angeles, CA 90064",
        "career_url": "https://www.riotgames.com/en/work-with-us",
        "area": "West LA"
    },
    {
        "name": "Google/YouTube",
        "domain": "google.com",
        "location": "Playa Vista, CA",
        "address": "12777 W Jefferson Blvd, Los Angeles, CA 90066",
        "career_url": "https://careers.google.com",
        "area": "Playa Vista"
    },
    {
        "name": "Meta",
        "domain": "meta.com",
        "location": "Playa Vista, CA",
        "address": "5400 Beethoven St, Los Angeles, CA 90066",
        "career_url": "https://www.metacareers.com",
        "area": "Playa Vista"
    },
    {
        "name": "Hulu",
        "domain": "hulu.com",
        "location": "Santa Monica, CA",
        "address": "2500 Broadway, Santa Monica, CA 90404",
        "career_url": "https://www.hulu.com/jobs",
        "area": "Santa Monica"
    },
    {
        "name": "Disney Streaming",
        "domain": "disney.com",
        "location": "Santa Monica, CA",
        "address": "2500 Broadway, Santa Monica, CA 90404",
        "career_url": "https://jobs.disneycareers.com",
        "area": "Santa Monica"
    },
    {
        "name": "Blizzard Entertainment",
        "domain": "blizzard.com",
        "location": "Santa Monica, CA",
        "address": "1322 2nd St, Santa Monica, CA 90401",
        "career_url": "https://careers.blizzard.com",
        "area": "Santa Monica"
    },
    {
        "name": "Electronic Arts",
        "domain": "ea.com",
        "location": "Playa Vista, CA",
        "address": "12790 W Jefferson Blvd, Los Angeles, CA 90066",
        "career_url": "https://www.ea.com/careers",
        "area": "Playa Vista"
    },
    {
        "name": "Yahoo",
        "domain": "yahooinc.com",
        "location": "Playa Vista, CA",
        "address": "12777 W Jefferson Blvd, Los Angeles, CA 90094",
        "career_url": "https://www.yahooinc.com/careers",
        "area": "Playa Vista"
    },
    
    # ==== DOWNTOWN LA - 45-60 mins via Metro ====
    {
        "name": "SpaceX",
        "domain": "spacex.com",
        "location": "Hawthorne, CA",
        "address": "1 Rocket Rd, Hawthorne, CA 90250",
        "career_url": "https://www.spacex.com/careers",
        "area": "Hawthorne"
    },
    {
        "name": "Netflix",
        "domain": "netflix.com",
        "location": "Hollywood, CA",
        "address": "5808 W Sunset Blvd, Los Angeles, CA 90028",
        "career_url": "https://jobs.netflix.com",
        "area": "Hollywood"
    },
    {
        "name": "SKIMS",
        "domain": "skims.com",
        "location": "Downtown LA",
        "address": "700 S Flower St, Los Angeles, CA 90017",
        "career_url": "https://skims.com/pages/careers",
        "area": "Downtown LA"
    },
    {
        "name": "Scopely",
        "domain": "scopely.com",
        "location": "Culver City, CA",
        "address": "3530 Hayden Ave, Culver City, CA 90232",
        "career_url": "https://scopely.com/en/careers",
        "area": "Culver City"
    },
    {
        "name": "Headspace",
        "domain": "headspace.com",
        "location": "Santa Monica, CA",
        "address": "2415 Michigan Ave, Santa Monica, CA 90404",
        "career_url": "https://www.headspace.com/careers",
        "area": "Santa Monica"
    },
    {
        "name": "Bird",
        "domain": "bird.co",
        "location": "Santa Monica, CA",
        "address": "406 Broadway, Santa Monica, CA 90401",
        "career_url": "https://www.bird.co/careers",
        "area": "Santa Monica"
    },
    {
        "name": "Tinder",
        "domain": "gotinder.com",
        "location": "West Hollywood, CA",
        "address": "8750 Sunset Blvd, West Hollywood, CA 90069",
        "career_url": "https://mtch.com/careers",
        "area": "West Hollywood"
    },
    {
        "name": "DoorDash",
        "domain": "doordash.com",
        "location": "Los Angeles, CA",
        "address": "901 Market St, Los Angeles, CA 90021",
        "career_url": "https://careers.doordash.com",
        "area": "Downtown LA"
    },
    {
        "name": "Honey (PayPal)",
        "domain": "joinhoney.com",
        "location": "Downtown LA",
        "address": "963 E 4th Pl, Los Angeles, CA 90013",
        "career_url": "https://www.paypal.com/us/webapps/mpp/jobs",
        "area": "Downtown LA"
    },
    {
        "name": "Hyperion Entertainment",
        "domain": "hyperionentertainment.com",
        "location": "West LA",
        "address": "11377 W Olympic Blvd, Los Angeles, CA 90064",
        "career_url": "https://www.warnerbros.com/careers",
        "area": "West LA"
    },
    
    # ==== EL SEGUNDO (Aerospace + Tech) - 45-60 mins ====
    {
        "name": "Northrop Grumman",
        "domain": "northropgrumman.com",
        "location": "El Segundo, CA",
        "address": "1 Space Park, El Segundo, CA 90245",
        "career_url": "https://www.northropgrumman.com/careers",
        "area": "El Segundo"
    },
    {
        "name": "Boeing",
        "domain": "boeing.com",
        "location": "El Segundo, CA",
        "address": "2401 E El Segundo Blvd, El Segundo, CA 90245",
        "career_url": "https://jobs.boeing.com",
        "area": "El Segundo"
    },
    {
        "name": "Aerospace Corp",
        "domain": "aerospace.org",
        "location": "El Segundo, CA",
        "address": "2310 E El Segundo Blvd, El Segundo, CA 90245",
        "career_url": "https://aerospace.org/careers",
        "area": "El Segundo"
    },
]

# ==============================================================================
# FIRECRAWL SEARCH FOR LINKEDIN PROFILES
# ==============================================================================

def find_department_heads(company_name):
    """
    Use Firecrawl to search LinkedIn publicly for department heads
    NO LOGIN NEEDED - uses Google's public index of LinkedIn
    """
    print(f"\n🔍 Searching LinkedIn for {company_name} data/engineering leaders...")
    
    try:
        # Search LinkedIn via Google's public index
        query = f'site:linkedin.com "{company_name}" ("Head of Data" OR "VP Engineering" OR "Director of Data" OR "Data Engineering Manager" OR "VP of Data" OR "Chief Data Officer")'
        
        headers = {
            "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": query,
            "limit": 5
        }
        
        response = requests.post(
            "https://api.firecrawl.dev/v1/search",
            headers=headers,
            json=payload,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('data', [])
            
            # Parse results
            leaders = []
            for result in results:
                title_desc = result.get('title', '') + ' ' + result.get('description', '')
                
                # Extract name from title (usually "Name - Title - Company")
                name_match = re.match(r'^([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', result.get('title', ''))
                
                # Extract title
                title_keywords = ['Head of Data', 'VP Engineering', 'Director of Data', 'Data Engineering Manager', 
                                 'VP of Data', 'Chief Data Officer', 'VP, Data', 'Director, Data', 'Engineering Manager']
                
                found_title = None
                for keyword in title_keywords:
                    if keyword.lower() in title_desc.lower():
                        found_title = keyword
                        break
                
                if name_match and found_title:
                    name = name_match.group(1)
                    linkedin_url = result.get('url', '')
                    
                    leaders.append({
                        'name': name,
                        'title': found_title,
                        'linkedin_url': linkedin_url
                    })
                    
                    print(f"   ✅ Found: {name} - {found_title}")
            
            return leaders if leaders else None
        else:
            print(f"   ⚠️  Search failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ⚠️  Error: {e}")
        return None

# ==============================================================================
# HUNTER.IO - GUESS EMAIL FROM NAME
# ==============================================================================

def guess_email(name, domain):
    """
    Use Hunter.io to get company email pattern, then construct email
    """
    try:
        # Get domain email pattern
        url = f"https://api.hunter.io/v2/domain-search"
        params = {
            'domain': domain,
            'api_key': HUNTER_API_KEY,
            'limit': 1  # Just need the pattern
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            pattern = data.get('data', {}).get('pattern', '')
            
            if pattern:
                # Parse name
                parts = name.split()
                first_name = parts[0].lower() if len(parts) > 0 else ''
                last_name = parts[-1].lower() if len(parts) > 1 else ''
                
                # Apply pattern
                email = pattern.replace('{first}', first_name)
                email = email.replace('{last}', last_name)
                email = email.replace('{f}', first_name[0] if first_name else '')
                email = email.replace('{l}', last_name[0] if last_name else '')
                
                return email, pattern
        
        return None, None
        
    except Exception as e:
        print(f"      ⚠️  Hunter error: {e}")
        return None, None

# ==============================================================================
# CALCULATE COMMUTE
# ==============================================================================

def calculate_commute(destination_address):
    """Quick transit commute calculation"""
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
            duration_mins = route['duration']['value'] / 60
            duration_text = route['duration']['text']
            
            # Extract transit lines
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
            
            # Rate commute
            num_transfers = len(transit_routes) - 1
            if duration_mins <= 40 and num_transfers <= 1:
                rating = '⭐⭐⭐ Excellent'
            elif duration_mins <= 50 and num_transfers <= 1:
                rating = '⭐⭐ Good'
            else:
                rating = '⭐ Acceptable'
            
            return {
                'transit_duration': duration_text,
                'transit_routes': ' → '.join(transit_routes) if transit_routes else 'Transit',
                'transit_changes': num_transfers,
                'commute_rating': rating,
                'google_maps_link': f"https://www.google.com/maps/dir/?api=1&origin={HOME_ADDRESS.replace(' ', '+')}&destination={destination_address.replace(' ', '+')}"
            }
        else:
            return {
                'transit_duration': 'No transit',
                'transit_routes': 'No public transit',
                'transit_changes': 0,
                'commute_rating': 'N/A',
                'google_maps_link': f"https://www.google.com/maps/dir/?api=1&origin={HOME_ADDRESS.replace(' ', '+')}&destination={destination_address.replace(' ', '+')}"
            }
    except Exception as e:
        return {
            'transit_duration': 'Unknown',
            'transit_routes': 'Unknown',
            'transit_changes': 0,
            'commute_rating': 'Unknown',
            'google_maps_link': ''
        }

# ==============================================================================
# MAIN
# ==============================================================================

def main():
    print("=" * 80)
    print("🏖️  SILICON BEACH DEPARTMENT HEAD FINDER")
    print("=" * 80)
    print("📍 Using Firecrawl (LinkedIn search) + Hunter.io (email guessing)")
    print(f"📍 Your location: {HOME_ADDRESS}")
    print()
    
    all_results = []
    
    for i, company in enumerate(LA_TECH_COMPANIES, 1):
        print(f"\n{'='*80}")
        print(f"[{i}/{len(LA_TECH_COMPANIES)}] {company['name']} ({company['area']})")
        print(f"{'='*80}")
        
        # Get commute info
        commute = calculate_commute(company['address'])
        print(f"🚌 Commute: {commute['transit_duration']} via {commute['transit_routes']}")
        print(f"   Rating: {commute['commute_rating']}")
        time.sleep(1)
        
        # Find department heads on LinkedIn
        leaders = find_department_heads(company['name'])
        
        if leaders:
            for leader in leaders:
                # Guess email using Hunter.io
                email, pattern = guess_email(leader['name'], company['domain'])
                
                if email:
                    print(f"      📧 Guessed email: {email} (pattern: {pattern})")
                
                result = {
                    'company': company['name'],
                    'area': company['area'],
                    'location': company['location'],
                    'address': company['address'],
                    'contact_name': leader['name'],
                    'contact_title': leader['title'],
                    'contact_email': email or 'Unknown',
                    'email_pattern': pattern or 'Unknown',
                    'linkedin_url': leader['linkedin_url'],
                    **commute,
                    'career_url': company['career_url']
                }
                
                all_results.append(result)
        else:
            # Still add company even if no contacts found
            result = {
                'company': company['name'],
                'area': company['area'],
                'location': company['location'],
                'address': company['address'],
                'contact_name': 'Not found',
                'contact_title': 'Not found',
                'contact_email': 'Check LinkedIn manually',
                'email_pattern': 'Unknown',
                'linkedin_url': f'https://www.linkedin.com/search/results/people/?keywords={company["name"]}%20data%20engineering',
                **commute,
                'career_url': company['career_url']
            }
            all_results.append(result)
        
        # Be nice to APIs
        time.sleep(3)
    
    # Export to CSV
    if all_results:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_file = f'data/raw/silicon_beach_contacts_{timestamp}.csv'
        
        fieldnames = [
            'company', 'area', 'location', 'address',
            'contact_name', 'contact_title', 'contact_email', 'email_pattern', 'linkedin_url',
            'transit_duration', 'transit_routes', 'transit_changes', 'commute_rating',
            'google_maps_link', 'career_url'
        ]
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_results)
        
        print("\n" + "=" * 80)
        print(f"✅ Exported {len(all_results)} contacts to: {csv_file}")
        print("=" * 80)
        
        # Summary
        print("\n📊 COMPANIES WITH CONTACTS FOUND:")
        for result in all_results:
            if result['contact_name'] != 'Not found':
                print(f"\n🏢 {result['company']}")
                print(f"   👤 {result['contact_name']} - {result['contact_title']}")
                print(f"   📧 {result['contact_email']}")
                print(f"   🚌 {result['commute_rating']}")
    else:
        print("\n❌ No results found!")

if __name__ == '__main__':
    main()

