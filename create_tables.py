#!/usr/bin/env python3
"""
Create missing Snowflake tables
"""
import os
import snowflake.connector

# Load credentials from environment
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

print("Creating STAGING schema...")
cursor.execute("CREATE SCHEMA IF NOT EXISTS STAGING")

print("Creating STAGING.JOBS_CLEANED table...")
cursor.execute("""
CREATE TABLE IF NOT EXISTS STAGING.JOBS_CLEANED (
    TYPE VARCHAR(50),
    COMPANY VARCHAR(500),
    TITLE VARCHAR(500),
    AREA VARCHAR(200),
    LOCATION VARCHAR(500),
    ADDRESS VARCHAR(1000),
    TRANSIT_DURATION VARCHAR(100),
    TRANSIT_ROUTES VARCHAR(500),
    TRANSIT_CHANGES NUMBER,
    COMMUTE_RATING VARCHAR(50),
    COMMUTE_SCORE NUMBER,
    GOOGLE_MAPS_LINK VARCHAR(1000),
    CAREER_URL VARCHAR(1000),
    LINKEDIN_SEARCH VARCHAR(1000),
    CONTACT_NAME VARCHAR(500),
    CONTACT_EMAIL VARCHAR(500),
    CLOSEST_METRO VARCHAR(500)
)
""")

print("Creating MARTS.REFERRAL_PATHS table...")
cursor.execute("""
CREATE TABLE IF NOT EXISTS MARTS.REFERRAL_PATHS (
    ID NUMBER AUTOINCREMENT PRIMARY KEY,
    COMPANY VARCHAR(500),
    TARGET_PERSON VARCHAR(500),
    TARGET_TITLE VARCHAR(500),
    CONNECTOR_NAME VARCHAR(500),
    CONNECTOR_RELATIONSHIP VARCHAR(500),
    CONNECTION_TIER NUMBER,
    NOTES TEXT,
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
)
""")

print("Verifying tables...")
cursor.execute("SHOW TABLES IN SCHEMA STAGING")
staging_tables = cursor.fetchall()
print(f"STAGING tables: {[t[1] for t in staging_tables]}")

cursor.execute("SHOW TABLES IN SCHEMA MARTS")
marts_tables = cursor.fetchall()
print(f"MARTS tables: {[t[1] for t in marts_tables]}")

cursor.close()
conn.close()

print("✅ Setup complete!")
