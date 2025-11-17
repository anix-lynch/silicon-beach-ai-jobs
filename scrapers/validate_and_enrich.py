#!/usr/bin/env python3
"""
VALIDATE & ENRICH CSV before loading to databases
This is proper ETL - clean data first, then load!
"""

import pandas as pd
import requests
import os
import sys
from datetime import datetime

GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
HOME_ADDRESS = "YOUR_HOME_ADDRESS"

def calculate_commute(destination_address, company_name):
    """Get real commute data from Google Maps"""
    if not GOOGLE_MAPS_API_KEY:
        print(f"  ⚠️  No Google Maps API - using placeholder data")
        return {
            'transit_duration': 'Unknown',
            'transit_routes': 'Unknown',
            'transit_changes': 0,
            'commute_rating': 'Unknown',
            'commute_score': 50,
            'closest_metro': 'Unknown',
        }
    
    try:
        transit_url = "https://maps.googleapis.com/maps/api/directions/json"
        transit_params = {
            'origin': HOME_ADDRESS,
            'destination': destination_address,
            'mode': 'transit',
            'key': GOOGLE_MAPS_API_KEY
        }
        transit_resp = requests.get(transit_url, params=transit_params, timeout=10)
        transit_data = transit_resp.json()
        
        if transit_data['status'] != 'OK':
            print(f"  ⚠️  API Error: {transit_data['status']}")
            print(f"  Details: {transit_data.get('error_message', 'No error message')}")
            return {
                'transit_duration': 'No transit',
                'transit_routes': 'N/A',
                'transit_changes': 0,
                'commute_rating': 'Unknown',
                'commute_score': 25,
                'closest_metro': 'N/A',
            }
        
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
                
                transit_routes.append(f"{line_name}")
        
        transit_routes_str = " → ".join(transit_routes) if transit_routes else "Walking only"
        transit_changes = max(0, len(transit_routes) - 1)
        
        # Rating
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
        
        print(f"  ✅ {duration_mins} min | {transit_routes_str} | {rating}")
        
        return {
            'transit_duration': f"{duration_mins} min",
            'transit_routes': transit_routes_str,
            'transit_changes': transit_changes,
            'commute_rating': rating,
            'commute_score': score,
            'closest_metro': nearest_metro,
        }
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return {
            'transit_duration': 'Error',
            'transit_routes': 'Error',
            'transit_changes': 0,
            'commute_rating': 'Unknown',
            'commute_score': 50,
            'closest_metro': 'N/A',
        }

def validate_and_enrich(input_csv):
    """
    Validate & enrich CSV data:
    1. Check required columns exist
    2. Fill missing data
    3. Add commute data if missing
    4. Standardize formats
    5. Save enriched version
    """
    print("\n" + "="*80)
    print("📋 STEP 1: LOAD & VALIDATE CSV")
    print("="*80)
    
    # Load CSV
    df = pd.read_csv(input_csv)
    print(f"  Loaded {len(df)} rows from {input_csv}")
    print(f"  Columns: {', '.join(df.columns.tolist())}")
    
    # Check required columns
    required_cols = ['company', 'type']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        print(f"\n  ❌ Missing required columns: {missing_cols}")
        print(f"  💡 Adding default values...")
        
        if 'type' not in df.columns:
            # Guess type based on source
            if 'source' in df.columns:
                df['type'] = df['source'].apply(lambda x: 'VC' if 'vc' in str(x).lower() else 'JOB')
            else:
                df['type'] = 'JOB'
    
    print("\n" + "="*80)
    print("🔍 STEP 2: VALIDATE DATA QUALITY")
    print("="*80)
    
    issues = []
    
    # Check for missing company names
    missing_company = df['company'].isna().sum()
    if missing_company > 0:
        issues.append(f"  ⚠️  {missing_company} rows missing company name")
        df = df.dropna(subset=['company'])
    
    # Check for missing areas
    missing_area = df['area'].isna().sum() if 'area' in df.columns else len(df)
    if missing_area > 0:
        issues.append(f"  ⚠️  {missing_area} rows missing area")
        if 'area' not in df.columns:
            df['area'] = 'Los Angeles'
        else:
            df['area'] = df['area'].fillna('Los Angeles')
    
    # Check for missing commute data
    if 'commute_score' not in df.columns:
        issues.append(f"  ⚠️  No commute data - will need to enrich")
        df['commute_score'] = None
    
    missing_commute = df['commute_score'].isna().sum()
    
    if issues:
        print("\n".join(issues))
    else:
        print("  ✅ All validation checks passed!")
    
    print("\n" + "="*80)
    print("🚀 STEP 3: ENRICH MISSING DATA")
    print("="*80)
    
    enriched_count = 0
    
    for idx, row in df.iterrows():
        # Only enrich if commute data is missing
        if pd.isna(row.get('commute_score')) or row.get('commute_rating') == 'Unknown':
            print(f"\n[{idx+1}/{len(df)}] Enriching {row['company']}...")
            
            # Get address
            address = row.get('address') or row.get('location') or f"{row['area']}, CA"
            
            # Calculate commute
            commute_data = calculate_commute(address, row['company'])
            
            # Update dataframe
            for key, value in commute_data.items():
                df.at[idx, key] = value
            
            enriched_count += 1
    
    print(f"\n  ✅ Enriched {enriched_count} rows with commute data")
    
    print("\n" + "="*80)
    print("📊 STEP 4: STANDARDIZE & VALIDATE")
    print("="*80)
    
    # Ensure all required columns exist
    required_output_cols = [
        'type', 'company', 'title', 'location', 'address', 'area',
        'career_url', 'google_maps_link', 'linkedin_search',
        'transit_duration', 'transit_routes', 'transit_changes',
        'commute_rating', 'commute_score', 'closest_metro',
        'scraped_at', 'source'
    ]
    
    for col in required_output_cols:
        if col not in df.columns:
            df[col] = None
            print(f"  ➕ Added missing column: {col}")
    
    # Standardize types
    df['transit_changes'] = df['transit_changes'].fillna(0).astype(int)
    df['commute_score'] = df['commute_score'].fillna(50).astype(int)
    
    # Fill empty strings
    df['title'] = df['title'].fillna('Position Available')
    df['location'] = df['location'].fillna(df['area'] + ', CA')
    df['address'] = df['address'].fillna(df['location'])
    
    if 'google_maps_link' not in df.columns or df['google_maps_link'].isna().all():
        df['google_maps_link'] = df['address'].apply(
            lambda x: f"https://www.google.com/maps/dir/?api=1&origin={HOME_ADDRESS.replace(' ', '+')}&destination={str(x).replace(' ', '+')}&travelmode=transit"
        )
    
    if 'scraped_at' not in df.columns or df['scraped_at'].isna().all():
        df['scraped_at'] = datetime.now().isoformat()
    
    print(f"  ✅ Standardized all columns")
    
    print("\n" + "="*80)
    print("💾 STEP 5: SAVE ENRICHED CSV")
    print("="*80)
    
    # Save enriched version
    output_file = input_csv.replace('.csv', '_enriched.csv')
    df[required_output_cols].to_csv(output_file, index=False)
    
    print(f"  ✅ Saved to: {output_file}")
    
    print("\n" + "="*80)
    print("📊 FINAL SUMMARY")
    print("="*80)
    
    # Summary stats
    total_records = len(df)
    vcs = len(df[df['type'] == 'VC'])
    jobs = len(df[df['type'] == 'JOB'])
    
    excellent = len(df[df['commute_score'] >= 100])
    good = len(df[(df['commute_score'] >= 75) & (df['commute_score'] < 100)])
    acceptable = len(df[(df['commute_score'] >= 50) & (df['commute_score'] < 75)])
    poor = len(df[df['commute_score'] < 50])
    
    print(f"\n  Total Records: {total_records}")
    print(f"  • VCs: {vcs}")
    print(f"  • Jobs: {jobs}")
    print(f"\n  Commute Quality:")
    print(f"  • 🟢 Excellent (<40 min): {excellent}")
    print(f"  • 🟠 Good (40-50 min): {good}")
    print(f"  • ⚫ Acceptable (50-60 min): {acceptable}")
    print(f"  • ❌ Poor/Unknown: {poor}")
    
    print(f"\n  ✅ Data is now clean and ready to load!")
    print(f"  💡 Next: python load_jobs_to_both.py {output_file}")
    
    return output_file

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python validate_and_enrich.py <input_csv>")
        print("\nExample:")
        print("  python validate_and_enrich.py ../data/la_vcs_20251111_083756.csv")
        sys.exit(1)
    
    input_csv = sys.argv[1]
    output_csv = validate_and_enrich(input_csv)

