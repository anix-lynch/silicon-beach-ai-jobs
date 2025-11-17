#!/usr/bin/env python3
"""
Load existing CSV data into Snowflake
"""
import snowflake.connector
import pandas as pd
import os
from pathlib import Path

# Snowflake connection
SNOWFLAKE_CONFIG = {
    'account': 'vwyiycr-rpb51995',
    'user': 'ANIXLYNCH',
    'password': 'aRTHMrC5Pos@L76T',
    'database': 'JOB_SEARCH',
    'schema': 'RAW',
    'warehouse': 'COMPUTE_WH',
}

def load_csv_to_snowflake(csv_path):
    """Load CSV data into Snowflake RAW.JOBS table"""
    
    # Read CSV
    print(f"📖 Reading CSV: {csv_path}")
    df = pd.read_csv(csv_path)
    
    print(f"✅ Loaded {len(df)} rows")
    print(f"📊 Columns: {', '.join(df.columns.tolist())}")
    
    # Connect to Snowflake
    print("\n🔌 Connecting to Snowflake...")
    conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
    cursor = conn.cursor()
    
    # Prepare data for insertion
    print("📝 Preparing data...")
    
    # Insert each row
    insert_count = 0
    for idx, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO RAW.JOBS (
                    job_id, title, company, location, address, area,
                    job_url, apply_url, career_url, google_maps_link, linkedin_search,
                    transit_duration, transit_routes, transit_changes,
                    bike_duration, commute_rating, closest_metro,
                    department, contact_name, contact_title, contact_email, email_pattern,
                    description, source
                ) VALUES (
                    %(job_id)s, %(title)s, %(company)s, %(location)s, %(address)s, %(area)s,
                    %(job_url)s, %(apply_url)s, %(career_url)s, %(google_maps_link)s, %(linkedin_search)s,
                    %(transit_duration)s, %(transit_routes)s, %(transit_changes)s,
                    %(bike_duration)s, %(commute_rating)s, %(closest_metro)s,
                    %(department)s, %(contact_name)s, %(contact_title)s, %(contact_email)s, %(email_pattern)s,
                    %(description)s, 'silicon_beach_manual'
                )
            """, {
                'job_id': f"sb_{idx}",
                'title': row.get('title', 'N/A'),
                'company': row.get('company'),
                'location': row.get('location'),
                'address': row.get('address'),
                'area': row.get('area'),
                'job_url': row.get('linkedin_url'),
                'apply_url': None,
                'career_url': row.get('career_url'),
                'google_maps_link': row.get('google_maps_link'),
                'linkedin_search': row.get('linkedin_url'),
                'transit_duration': row.get('transit_duration'),
                'transit_routes': row.get('transit_routes'),
                'transit_changes': int(row.get('transit_changes', 0)) if pd.notna(row.get('transit_changes')) else None,
                'bike_duration': None,
                'commute_rating': row.get('commute_rating'),
                'closest_metro': row.get('closest_metro'),
                'department': None,
                'contact_name': row.get('contact_name'),
                'contact_title': row.get('contact_title'),
                'contact_email': row.get('contact_email'),
                'email_pattern': row.get('email_pattern'),
                'description': None,
            })
            insert_count += 1
            if insert_count % 5 == 0:
                print(f"  ✓ Inserted {insert_count}/{len(df)} rows...")
        except Exception as e:
            print(f"  ⚠️  Error inserting row {idx}: {e}")
            continue
    
    conn.commit()
    print(f"\n✅ Successfully inserted {insert_count} rows into Snowflake!")
    
    # Verify data
    print("\n🔍 Verifying data in Snowflake...")
    cursor.execute("SELECT COUNT(*) FROM RAW.JOBS")
    total_count = cursor.fetchone()[0]
    print(f"📊 Total rows in RAW.JOBS: {total_count}")
    
    # Show top companies by commute score
    print("\n🎯 Top companies by commute:")
    cursor.execute("""
        SELECT company, commute_rating, transit_duration, transit_routes
        FROM STAGING.JOBS_CLEANED
        ORDER BY commute_score DESC
        LIMIT 5
    """)
    
    for row in cursor.fetchall():
        print(f"  • {row[0]}: {row[1]} ({row[2]}) - {row[3]}")
    
    cursor.close()
    conn.close()
    print("\n🎉 Done!")

if __name__ == '__main__':
    # Find the most recent CSV
    data_dir = Path(__file__).parent.parent / 'data' / 'raw'
    csv_files = list(data_dir.glob('silicon_beach_*.csv'))
    
    if not csv_files:
        print("❌ No CSV files found in data/raw/")
        exit(1)
    
    latest_csv = max(csv_files, key=lambda p: p.stat().st_mtime)
    load_csv_to_snowflake(latest_csv)

