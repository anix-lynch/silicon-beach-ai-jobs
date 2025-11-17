#!/usr/bin/env python3
"""
Load VC data into DuckDB
"""
import duckdb
import csv
import sys
from pathlib import Path

DUCKDB_FILE = "../data/silicon_beach.duckdb"

def load_vcs(csv_file):
    """Load VC CSV into DuckDB"""
    conn = duckdb.connect(DUCKDB_FILE)
    
    # Read CSV
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"📊 Loading {len(rows)} VCs into DuckDB...")
    
    # Insert into jobs table
    for row in rows:
        conn.execute("""
            INSERT INTO jobs (
                type, company, title, location, address, area, stage, focus,
                career_url, linkedin_search,
                transit_duration, transit_routes, transit_changes,
                bike_duration, commute_rating, commute_score, closest_metro,
                google_maps_link, scraped_at, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            row['type'], row['company'], row['title'], row['location'], 
            row['address'], row['area'], row['stage'], row['focus'],
            row['career_url'], row['linkedin_search'],
            row['transit_duration'], row['transit_routes'], int(row['transit_changes']),
            row['bike_duration'], row['commute_rating'], int(row['commute_score']), 
            row['nearest_metro'], row['google_maps_link'], row['scraped_at'], row['source']
        ])
    
    # Verify
    result = conn.execute("SELECT COUNT(*) FROM jobs WHERE type = 'VC'").fetchone()
    print(f"✅ Total VCs in database: {result[0]}")
    
    result = conn.execute("SELECT COUNT(*) FROM jobs WHERE type = 'JOB'").fetchone()
    print(f"✅ Total Jobs in database: {result[0]}")
    
    conn.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python load_vcs_to_duckdb.py <csv_file>")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    load_vcs(csv_file)
    
    print("\n🚀 Now refresh your Streamlit app to see VCs on the map!")

