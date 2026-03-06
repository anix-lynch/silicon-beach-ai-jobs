#!/usr/bin/env python3
"""
Scrape LA/Culver City VC firms and add to job search database
Orange pins for VCs, green for tech jobs
"""

import requests
import os
import csv
from datetime import datetime

# API Keys
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', 'YOUR_KEY_HERE')
HOME_ADDRESS = os.getenv("HOME_ADDRESS", "YOUR_HOME_ADDRESS")

# VC List (from your research)
LA_VCS = [
    # Culver City VCs
    {"name": "Fika Ventures", "address": "9696 Culver Blvd, Suite 204, Culver City, CA 90232", "focus": "Enterprise software, fintech, marketplaces, digital health", "stage": "Seed"},
    {"name": "Navitas Capital", "address": "3975 Landmark Street, Suite 1200, Culver City, CA 90232", "focus": "Transformative technology & innovation", "stage": "Early"},
    {"name": "Plus Capital", "address": "Culver City, CA", "focus": "Media & entertainment, apps, e-commerce", "stage": "Seed/Early"},
    {"name": "Fulcrum Venture Capital", "address": "300 Corporate Pointe, Suite 380, Culver City, CA 90232", "focus": "Early-stage tech startups", "stage": "Seed"},
    
    # Silicon Beach / Venice / Santa Monica
    {"name": "Upfront Ventures", "address": "2901 28th St, Santa Monica, CA 90405", "focus": "Enterprise, consumer, fintech", "stage": "Seed/Series A"},
    {"name": "Crosscut Ventures", "address": "Santa Monica, CA", "focus": "Enterprise, consumer, fintech, spacetech", "stage": "Seed"},
    {"name": "Mucker Capital", "address": "Santa Monica, CA", "focus": "Early-stage technology", "stage": "Seed"},
    {"name": "Fifth Wall", "address": "Venice, CA", "focus": "PropTech", "stage": "Series A+"},
    {"name": "Greycroft", "address": "Santa Monica, CA", "focus": "Consumer internet, enterprise software", "stage": "Seed/Series A"},
    {"name": "M13", "address": "Venice, CA", "focus": "Consumer & enterprise", "stage": "Seed/Series A"},
    {"name": "Wonder Ventures", "address": "Santa Monica, CA", "focus": "Enterprise software", "stage": "Seed"},
    {"name": "Bonfire Ventures", "address": "Santa Monica, CA", "focus": "B2B tech", "stage": "Seed"},
    {"name": "TenOneTen Ventures", "address": "Santa Monica, CA", "focus": "Deep tech", "stage": "Seed"},
    {"name": "Amplify.LA", "address": "Venice, CA", "focus": "Early-stage tech", "stage": "Pre-seed/Seed"},
    {"name": "Wavemaker Partners", "address": "Los Angeles, CA", "focus": "Enterprise tech", "stage": "Seed/Series A"},
    {"name": "March Capital", "address": "Santa Monica, CA", "focus": "Digital infrastructure, cybersecurity", "stage": "Growth"},
    {"name": "Struck Capital", "address": "Los Angeles, CA", "focus": "Consumer & enterprise", "stage": "Seed/Series A"},
    {"name": "Embark Ventures", "address": "Los Angeles, CA", "focus": "Digital health, fintech", "stage": "Seed"},
    {"name": "Alpha Edison", "address": "Los Angeles, CA", "focus": "Industry-agnostic tech", "stage": "Seed"},
    {"name": "Backstage Capital", "address": "Los Angeles, CA", "focus": "Diverse founders", "stage": "Pre-seed/Seed"},
    {"name": "Science Inc.", "address": "Santa Monica, CA", "focus": "Startup studio", "stage": "Incubator"},
    {"name": "Slauson & Co.", "address": "Los Angeles, CA", "focus": "Underrepresented founders", "stage": "Pre-seed/Seed"},
    {"name": "BAM Ventures", "address": "Los Angeles, CA", "focus": "Media & entertainment tech", "stage": "Seed/Early"},
    {"name": "Clocktower Technology Ventures", "address": "Santa Monica, CA", "focus": "Fintech, insurtech", "stage": "Seed/Series A"},
    
    # Beverly Hills / West LA
    {"name": "Baroda Ventures", "address": "Beverly Hills, CA", "focus": "IT, e-commerce, blockchain", "stage": "Seed/Early"},
    {"name": "Clearstone Venture Partners", "address": "Santa Monica, CA", "focus": "eCommerce, infrastructure, mobile", "stage": "Early/Growth"},
    {"name": "Anthem Venture Partners", "address": "Santa Monica, CA", "focus": "Internet, media, software, biotech, fintech", "stage": "Seed/Early"},
    
    # Downtown LA / Hollywood
    {"name": "Core VC", "address": "Hollywood, CA", "focus": "Financial services, payments, future of work, healthcare", "stage": "Seed/Series A"},
    
    # Impact / Mission-Driven
    {"name": "Michelson Impact Ventures", "address": "Los Angeles, CA", "focus": "Mission-driven startups with societal impact", "stage": "Seed/Early"},
    {"name": "Angeleno Group", "address": "Los Angeles, CA", "focus": "Clean energy & climate solutions", "stage": "Early/Growth"},
    {"name": "Ground Force Capital", "address": "Venice, CA", "focus": "Food & ag tech", "stage": "Seed/Early"},
    {"name": "Aliment Capital", "address": "Century City, CA", "focus": "Food and agriculture tech", "stage": "Early/Growth"},
    
    # Pasadena
    {"name": "California Technology Ventures", "address": "Pasadena, CA", "focus": "IT, life science", "stage": "Early/Growth"},
    {"name": "Pasadena Angels", "address": "Pasadena, CA", "focus": "Angel network", "stage": "Pre-seed/Seed"},
]

def calculate_commute(destination_address):
    """Get transit/bike commute info from Google Maps"""
    if not GOOGLE_MAPS_API_KEY or GOOGLE_MAPS_API_KEY == 'YOUR_KEY_HERE':
        print("⚠️  No Google Maps API key - skipping commute data")
        return {
            'transit_duration': 'N/A',
            'transit_routes': 'N/A',
            'transit_changes': 0,
            'bike_duration': 'N/A',
            'commute_rating': 'Unknown',
            'commute_score': 50,
            'nearest_metro': 'N/A',
            'google_maps_link': f"https://www.google.com/maps/dir/?api=1&origin={HOME_ADDRESS.replace(' ', '+')}&destination={destination_address.replace(' ', '+')}"
        }
    
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
        
        # Bike directions
        bike_params = {
            'origin': HOME_ADDRESS,
            'destination': destination_address,
            'mode': 'bicycling',
            'key': GOOGLE_MAPS_API_KEY
        }
        bike_resp = requests.get(transit_url, params=bike_params, timeout=10)
        bike_data = bike_resp.json()
        
        if transit_data['status'] != 'OK':
            print(f"  Transit API error: {transit_data.get('status', 'Unknown')}")
            return {
                'transit_duration': 'No transit available',
                'transit_routes': 'N/A',
                'transit_changes': 0,
                'bike_duration': 'N/A',
                'commute_rating': 'Not accessible',
                'commute_score': 0,
                'nearest_metro': 'N/A',
                'google_maps_link': f"https://www.google.com/maps/dir/?api=1&origin={HOME_ADDRESS.replace(' ', '+')}&destination={destination_address.replace(' ', '+')}"
            }
        
        route = transit_data['routes'][0]['legs'][0]
        duration_mins = route['duration']['value'] // 60
        
        # Extract transit routes
        transit_routes = []
        transit_changes = 0
        nearest_metro = "N/A"
        
        for step in route['steps']:
            if step['travel_mode'] == 'TRANSIT':
                transit_details = step.get('transit_details', {})
                line = transit_details.get('line', {})
                vehicle_type = line.get('vehicle', {}).get('type', 'TRANSIT')
                line_name = line.get('short_name') or line.get('name', 'Transit')
                
                # Check for subway stations
                if vehicle_type == 'SUBWAY':
                    departure_stop = transit_details.get('departure_stop', {}).get('name', '')
                    if nearest_metro == "N/A":
                        nearest_metro = departure_stop
                
                transit_routes.append(f"{line_name} ({vehicle_type.lower()})")
                transit_changes += 1
        
        transit_routes_str = " → ".join(transit_routes) if transit_routes else "Walking only"
        transit_changes = max(0, transit_changes - 1)  # Transfers = routes - 1
        
        # Bike duration
        bike_duration = "N/A"
        if bike_data['status'] == 'OK':
            bike_mins = bike_data['routes'][0]['legs'][0]['duration']['value'] // 60
            bike_duration = f"{bike_mins} min"
        
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
            rating = "❌ Too far"
            score = 25
        
        google_maps_link = f"https://www.google.com/maps/dir/?api=1&origin={HOME_ADDRESS.replace(' ', '+')}&destination={destination_address.replace(' ', '+')}&travelmode=transit"
        
        return {
            'transit_duration': f"{duration_mins} min",
            'transit_routes': transit_routes_str,
            'transit_changes': transit_changes,
            'bike_duration': bike_duration,
            'commute_rating': rating,
            'commute_score': score,
            'nearest_metro': nearest_metro,
            'google_maps_link': google_maps_link
        }
        
    except Exception as e:
        print(f"  Commute calculation error: {e}")
        return {
            'transit_duration': 'Error',
            'transit_routes': 'Error',
            'transit_changes': 0,
            'bike_duration': 'Error',
            'commute_rating': 'Error',
            'commute_score': 0,
            'nearest_metro': 'N/A',
            'google_maps_link': f"https://www.google.com/maps/dir/?api=1&origin={HOME_ADDRESS.replace(' ', '+')}&destination={destination_address.replace(' ', '+')}"
        }

def scrape_vcs():
    """Process VC list and calculate commutes"""
    results = []
    
    print(f"\n🎯 Processing {len(LA_VCS)} LA VC firms...")
    
    for i, vc in enumerate(LA_VCS, 1):
        print(f"\n[{i}/{len(LA_VCS)}] {vc['name']}...")
        
        # Calculate commute
        commute_data = calculate_commute(vc['address'])
        
        # Build result
        result = {
            'type': 'VC',
            'company': vc['name'],
            'title': f"Portfolio Company / {vc['focus']}",
            'location': vc['address'],
            'address': vc['address'],
            'area': vc['address'].split(',')[-2].strip() if ',' in vc['address'] else 'Los Angeles',
            'stage': vc['stage'],
            'focus': vc['focus'],
            'career_url': f"https://www.google.com/search?q={vc['name'].replace(' ', '+')}+careers",
            'linkedin_search': f"https://www.linkedin.com/search/results/people/?keywords={vc['name'].replace(' ', '%20')}%20partner",
            **commute_data,
            'scraped_at': datetime.now().isoformat(),
            'source': 'manual_vc_list'
        }
        
        results.append(result)
        print(f"  ✓ {commute_data['commute_rating']} | {commute_data['transit_duration']} | {commute_data['transit_routes']}")
    
    return results

def save_to_csv(results):
    """Save to CSV"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"../data/la_vcs_{timestamp}.csv"
    
    fieldnames = [
        'type', 'company', 'title', 'location', 'address', 'area', 'stage', 'focus',
        'career_url', 'linkedin_search',
        'transit_duration', 'transit_routes', 'transit_changes',
        'bike_duration', 'commute_rating', 'commute_score', 'nearest_metro',
        'google_maps_link', 'scraped_at', 'source'
    ]
    
    os.makedirs('../data', exist_ok=True)
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n✅ Saved {len(results)} VCs to: {filename}")
    return filename

if __name__ == '__main__':
    results = scrape_vcs()
    csv_file = save_to_csv(results)
    
    print("\n" + "="*80)
    print("📊 SUMMARY")
    print("="*80)
    
    excellent = len([r for r in results if r['commute_score'] >= 100])
    good = len([r for r in results if 75 <= r['commute_score'] < 100])
    acceptable = len([r for r in results if 50 <= r['commute_score'] < 75])
    
    print(f"  Total VCs: {len(results)}")
    print(f"  🟢 Excellent commute (<40 min): {excellent}")
    print(f"  🟠 Good commute: {good}")
    print(f"  ⚫ Acceptable: {acceptable}")
    print(f"\n  Next: python load_to_duckdb.py {csv_file}")

