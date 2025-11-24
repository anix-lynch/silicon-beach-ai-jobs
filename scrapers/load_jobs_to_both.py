#!/usr/bin/env python3
"""
Load scraped data into BOTH DuckDB (free) and Snowflake (learning)
"""
import duckdb
import snowflake.connector
import csv
import sys
from pathlib import Path
from datetime import datetime

# DuckDB config
DUCKDB_FILE = "../data/silicon_beach.duckdb"

# Snowflake config
SNOWFLAKE_CONFIG = {
    'account': os.getenv('SNOWFLAKE_ACCOUNT', 'TIQGFZV-GRB26326'),
    'user': os.getenv('SNOWFLAKE_USER', 'ALYNCH'),
    'password': os.getenv('SNOWFLAKE_PASSWORD'),  # REQUIRED - set in environment
    'database': os.getenv('SNOWFLAKE_DATABASE', 'JOB_SEARCH'),
    'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
    'schema': os.getenv('SNOWFLAKE_SCHEMA', 'RAW')
}
if not SNOWFLAKE_CONFIG['password']:
    raise ValueError("SNOWFLAKE_PASSWORD environment variable is required")

def load_to_duckdb(csv_file):
    """Load into DuckDB (free forever!)"""
    print("\n📦 Loading into DuckDB...")
    
    conn = duckdb.connect(DUCKDB_FILE)
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"  Found {len(rows)} rows")
    
    for row in rows:
        conn.execute("""
            INSERT INTO jobs (
                type, company, title, location, address, area,
                career_url, google_maps_link,
                transit_duration, transit_routes, transit_changes,
                commute_rating, commute_score, closest_metro,
                scraped_at, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            row.get('type', 'JOB'),
            row['company'],
            row['title'],
            row['location'],
            row.get('address', row['location']),
            row['area'],
            row['career_url'],
            row['google_maps_link'],
            row['transit_duration'],
            row['transit_routes'],
            int(row['transit_changes']),
            row['commute_rating'],
            int(row['commute_score']),
            row.get('closest_metro') or row.get('nearest_metro', 'N/A'),
            row['scraped_at'],
            row['source']
        ])
    
    # Verify
    result = conn.execute("SELECT COUNT(*) FROM jobs WHERE source = ?", [rows[0]['source']]).fetchone()
    print(f"  ✅ DuckDB: {result[0]} total records from this source")
    
    result = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()
    print(f"  ✅ DuckDB: {result[0]} total records across all sources")
    
    conn.close()

def load_to_snowflake(csv_file):
    """Load into Snowflake (for learning + resume!)"""
    print("\n❄️  Loading into Snowflake...")
    
    conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
    cursor = conn.cursor()
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"  Found {len(rows)} rows")
    
    # Insert into RAW.JOBS
    for row in rows:
        cursor.execute("""
            INSERT INTO RAW.JOBS (
                JOB_ID, TITLE, COMPANY, LOCATION, ADDRESS, AREA,
                CAREER_URL, GOOGLE_MAPS_LINK,
                TRANSIT_DURATION, TRANSIT_ROUTES, TRANSIT_CHANGES,
                COMMUTE_RATING, COMMUTE_SCORE, CLOSEST_METRO,
                SCRAPED_AT, SOURCE
            ) VALUES (
                %(job_id)s, %(title)s, %(company)s, %(location)s, %(address)s, %(area)s,
                %(career_url)s, %(google_maps_link)s,
                %(transit_duration)s, %(transit_routes)s, %(transit_changes)s,
                %(commute_rating)s, %(commute_score)s, %(closest_metro)s,
                %(scraped_at)s, %(source)s
            )
        """, {
            'job_id': row.get('job_url', row['career_url']),
            'title': row['title'],
            'company': row['company'],
            'location': row['location'],
            'address': row.get('address', row['location']),
            'area': row['area'],
            'career_url': row['career_url'],
            'google_maps_link': row['google_maps_link'],
            'transit_duration': row['transit_duration'],
            'transit_routes': row['transit_routes'],
            'transit_changes': int(row['transit_changes']),
            'commute_rating': row['commute_rating'],
            'commute_score': int(row['commute_score']),
            'closest_metro': row.get('closest_metro') or row.get('nearest_metro', 'N/A'),
            'scraped_at': row['scraped_at'],
            'source': row['source']
        })
    
    # Verify
    cursor.execute(f"SELECT COUNT(*) FROM RAW.JOBS WHERE SOURCE = '{rows[0]['source']}'")
    result = cursor.fetchone()
    print(f"  ✅ Snowflake: {result[0]} records from this source")
    
    cursor.execute("SELECT COUNT(*) FROM RAW.JOBS")
    result = cursor.fetchone()
    print(f"  ✅ Snowflake: {result[0]} total records across all sources")
    
    conn.close()

def show_warehouse_usage():
    """Show Snowflake credits used (so you can track your $400)"""
    print("\n💰 Checking Snowflake credit usage...")
    
    try:
        conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
        cursor = conn.cursor()
        
        # Query warehouse usage
        cursor.execute("""
            SELECT 
                WAREHOUSE_NAME,
                SUM(CREDITS_USED) as TOTAL_CREDITS,
                COUNT(*) as NUM_QUERIES
            FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
            WHERE START_TIME >= DATEADD(day, -7, CURRENT_TIMESTAMP())
            GROUP BY WAREHOUSE_NAME
            ORDER BY TOTAL_CREDITS DESC
        """)
        
        results = cursor.fetchall()
        
        if results:
            print("\n  📊 Last 7 days:")
            for row in results:
                warehouse, credits, queries = row
                cost = credits * 2  # Assuming $2/credit (standard rate)
                print(f"     {warehouse}: {credits:.4f} credits (≈${cost:.2f}) | {queries} queries")
        else:
            print("  ℹ️  No usage data yet (account too new)")
        
        conn.close()
    except Exception as e:
        print(f"  ⚠️  Could not fetch usage data: {e}")
        print(f"  💡 Check manually at: https://app.snowflake.com/tiqgfzv/grb26326/#/compute/warehouses")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python load_jobs_to_both.py <csv_file>")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    
    print("="*80)
    print("🚀 Loading Data into DuckDB + Snowflake")
    print("="*80)
    print(f"  File: {csv_file}")
    
    # Load to both databases
    load_to_duckdb(csv_file)
    load_to_snowflake(csv_file)
    
    # Show Snowflake usage
    show_warehouse_usage()
    
    print("\n" + "="*80)
    print("✅ Data loaded into both databases!")
    print("="*80)
    print("\n💡 Next steps:")
    print("  • DuckDB: streamlit run app_duckdb.py")
    print("  • Snowflake: streamlit run app_snowflake.py")
    print("  • Both apps show the same data!")
    print(f"\n📊 Your Snowflake dashboard: https://app.snowflake.com/tiqgfzv/grb26326/")

