#!/usr/bin/env python3
"""
Migrate from Snowflake to DuckDB (free forever!)
Run once to export all your Snowflake data to local DuckDB
"""
import os
import snowflake.connector
import duckdb
from pathlib import Path

# Snowflake config
SNOWFLAKE_CONFIG = {
    'account': os.getenv('SNOWFLAKE_ACCOUNT', 'TIQGFZV-GRB26326'),
    'user': os.getenv('SNOWFLAKE_USER', 'ALYNCH'),
    'password': os.getenv('SNOWFLAKE_PASSWORD'),  # REQUIRED - set in environment
    'database': os.getenv('SNOWFLAKE_DATABASE', 'JOB_SEARCH'),
    'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
}
if not SNOWFLAKE_CONFIG['password']:
    raise ValueError("SNOWFLAKE_PASSWORD environment variable is required")

# DuckDB config (local file - free forever!)
DUCKDB_FILE = "data/silicon_beach.duckdb"

def migrate():
    """Export all Snowflake data to DuckDB"""
    
    print("🔌 Connecting to Snowflake...")
    sf_conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
    sf_cursor = sf_conn.cursor()
    
    print("📦 Connecting to DuckDB...")
    Path(DUCKDB_FILE).parent.mkdir(exist_ok=True)
    duck_conn = duckdb.connect(DUCKDB_FILE)
    
    # Export RAW.JOBS
    print("\n📊 Exporting RAW.JOBS...")
    sf_cursor.execute("""
        SELECT job_id, title, company, location, address, area,
               job_url, apply_url, career_url, google_maps_link, linkedin_search,
               transit_duration, transit_routes, transit_changes,
               bike_duration, commute_rating, closest_metro,
               department, contact_name, contact_title, contact_email, email_pattern,
               description, scraped_at, source
        FROM RAW.JOBS
    """)
    columns = [col[0].lower() for col in sf_cursor.description]
    rows = sf_cursor.fetchall()
    
    # Create table in DuckDB with exact same structure
    duck_conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            type VARCHAR DEFAULT 'JOB',
            job_id VARCHAR,
            title VARCHAR,
            company VARCHAR,
            location VARCHAR,
            address VARCHAR,
            area VARCHAR,
            stage VARCHAR,
            focus VARCHAR,
            job_url VARCHAR,
            apply_url VARCHAR,
            career_url VARCHAR,
            google_maps_link VARCHAR,
            linkedin_search VARCHAR,
            transit_duration VARCHAR,
            transit_routes VARCHAR,
            transit_changes INTEGER,
            bike_duration VARCHAR,
            commute_rating VARCHAR,
            commute_score INTEGER,
            closest_metro VARCHAR,
            department VARCHAR,
            contact_name VARCHAR,
            contact_title VARCHAR,
            contact_email VARCHAR,
            email_pattern VARCHAR,
            description TEXT,
            scraped_at TIMESTAMP,
            source VARCHAR
        )
    """)
    
    # Insert data
    print(f"  Inserting {len(rows)} rows...")
    duck_conn.executemany(f"""
        INSERT INTO jobs ({', '.join(columns)})
        VALUES ({', '.join(['?' for _ in columns])})
    """, rows)
    
    # Create views (same as Snowflake!)
    print("\n🔍 Creating views...")
    
    duck_conn.execute("""
        CREATE OR REPLACE VIEW jobs_cleaned AS
        SELECT 
            job_id,
            UPPER(TRIM(title)) as title,
            UPPER(TRIM(company)) as company,
            location,
            address,
            area,
            job_url,
            apply_url,
            google_maps_link,
            career_url,
            linkedin_search,
            
            -- Commute score (0-100)
            CASE 
                WHEN commute_rating LIKE '%Excellent%' THEN 100
                WHEN commute_rating LIKE '%Good%' THEN 75
                WHEN commute_rating LIKE '%Acceptable%' THEN 50
                ELSE 25
            END as commute_score,
            
            transit_duration,
            transit_routes,
            transit_changes,
            bike_duration,
            commute_rating,
            closest_metro,
            
            department,
            contact_name,
            contact_title,
            contact_email,
            
            scraped_at
        FROM jobs
        WHERE job_url IS NOT NULL
    """)
    
    duck_conn.execute("""
        CREATE OR REPLACE VIEW my_targets AS
        SELECT 
            company,
            title,
            location,
            transit_duration,
            transit_routes,
            commute_score,
            job_url,
            apply_url,
            contact_name,
            contact_email,
            closest_metro
        FROM jobs_cleaned
        WHERE commute_score >= 75
        ORDER BY commute_score DESC, transit_changes ASC
    """)
    
    # Create referral_paths table
    print("🔗 Creating referral_paths table...")
    duck_conn.execute("""
        CREATE TABLE IF NOT EXISTS referral_paths (
            id INTEGER PRIMARY KEY,
            company VARCHAR,
            target_person VARCHAR,
            target_title VARCHAR,
            connector_name VARCHAR,
            connector_relationship VARCHAR,
            connection_tier INTEGER,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Export existing referrals from Snowflake
    print("  Exporting referral paths...")
    sf_cursor.execute("SELECT * FROM MARTS.REFERRAL_PATHS")
    referrals = sf_cursor.fetchall()
    if referrals:
        duck_conn.executemany("""
            INSERT INTO referral_paths VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, referrals)
        print(f"  ✓ Exported {len(referrals)} referral paths")
    
    # Verify
    print("\n✅ Migration complete!")
    print("\n📊 DuckDB Summary:")
    result = duck_conn.execute("SELECT COUNT(*) FROM jobs").fetchone()
    print(f"  • Jobs: {result[0]}")
    result = duck_conn.execute("SELECT COUNT(*) FROM jobs_cleaned WHERE commute_score >= 75").fetchone()
    print(f"  • Top targets: {result[0]}")
    result = duck_conn.execute("SELECT COUNT(*) FROM referral_paths").fetchone()
    print(f"  • Referral paths: {result[0]}")
    
    print(f"\n💾 Data saved to: {DUCKDB_FILE}")
    print("🎉 You can now delete your Snowflake account and use DuckDB forever (free!)")
    
    sf_conn.close()
    duck_conn.close()

if __name__ == '__main__':
    migrate()

