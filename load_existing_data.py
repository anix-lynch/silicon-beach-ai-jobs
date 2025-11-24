#!/usr/bin/env python3
"""
Load existing CSV data into Snowflake
"""
import os
import pandas as pd
import snowflake.connector

# Load credentials
SNOWFLAKE_CONFIG = {
    'account': os.getenv('SNOWFLAKE_ACCOUNT', 'TIQGFZV-GRB26326'),
    'user': os.getenv('SNOWFLAKE_USER', 'ALYNCH'),
    'password': os.getenv('SNOWFLAKE_PASSWORD'),
    'database': os.getenv('SNOWFLAKE_DATABASE', 'JOB_SEARCH'),
    'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
}

print("Connecting to Snowflake...")
conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
cursor = conn.cursor()

# Load DuckDB data
print("Reading from DuckDB...")
import duckdb
duck_conn = duckdb.connect('data/silicon_beach.duckdb', read_only=True)

# Get data from DuckDB
try:
    df = duck_conn.execute("SELECT * FROM jobs_cleaned").df()
    print(f"Found {len(df)} rows in DuckDB")
    
    if len(df) > 0:
        print("Inserting into Snowflake STAGING.JOBS_CLEANED...")
        
        # Map columns from DuckDB to Snowflake schema
        df_mapped = pd.DataFrame()
        df_mapped['TYPE'] = 'Job'
        df_mapped['COMPANY'] = df['company']
        df_mapped['TITLE'] = df['title']
        df_mapped['AREA'] = df['area']
        df_mapped['LOCATION'] = df['location']
        df_mapped['ADDRESS'] = df['address']
        df_mapped['TRANSIT_DURATION'] = df['transit_duration']
        df_mapped['TRANSIT_ROUTES'] = df['transit_routes']
        df_mapped['TRANSIT_CHANGES'] = df['transit_changes']
        df_mapped['COMMUTE_RATING'] = df['commute_rating']
        df_mapped['COMMUTE_SCORE'] = df['commute_score']
        df_mapped['GOOGLE_MAPS_LINK'] = df['google_maps_link']
        df_mapped['CAREER_URL'] = df['career_url']
        df_mapped['LINKEDIN_SEARCH'] = df['linkedin_search']
        df_mapped['CONTACT_NAME'] = df['contact_name']
        df_mapped['CONTACT_EMAIL'] = df['contact_email']
        df_mapped['CLOSEST_METRO'] = df['closest_metro']
        
        # Use Snowflake's write_pandas for bulk insert
        from snowflake.connector.pandas_tools import write_pandas
        
        success, nchunks, nrows, _ = write_pandas(
            conn=conn,
            df=df_mapped,
            table_name='JOBS_CLEANED',
            schema='STAGING',
            database='JOB_SEARCH'
        )
        
        print(f"✅ Loaded {nrows} rows into Snowflake!")
    else:
        print("⚠️  No data in DuckDB to load")
        
except Exception as e:
    print(f"Error: {e}")
    print("DuckDB might be empty or table doesn't exist")

duck_conn.close()
cursor.close()
conn.close()

print("Done!")
