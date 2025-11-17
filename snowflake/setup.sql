-- ============================================
-- LA TECH JOB SEARCH - SNOWFLAKE SETUP
-- Run this in Snowflake SQL Worksheet
-- ============================================

-- Create database and schemas
CREATE DATABASE IF NOT EXISTS JOB_SEARCH;
USE DATABASE JOB_SEARCH;

CREATE SCHEMA IF NOT EXISTS RAW;      -- Scraped data lands here
CREATE SCHEMA IF NOT EXISTS STAGING;  -- Cleaned data
CREATE SCHEMA IF NOT EXISTS MARTS;    -- Final analytics-ready tables

-- ============================================
-- RAW LAYER: Direct scraper output
-- ============================================

USE SCHEMA RAW;

CREATE OR REPLACE TABLE JOBS (
    -- Job Details
    job_id VARCHAR(500),
    title VARCHAR(500),
    company VARCHAR(500),
    location VARCHAR(500),
    address VARCHAR(1000),
    area VARCHAR(100),
    
    -- URLs & Links
    job_url VARCHAR(1000),
    apply_url VARCHAR(1000),
    career_url VARCHAR(1000),
    google_maps_link VARCHAR(2000),
    linkedin_search VARCHAR(2000),
    
    -- Commute Data
    transit_duration VARCHAR(100),
    transit_routes VARCHAR(500),
    transit_changes INTEGER,
    bike_duration VARCHAR(100),
    commute_rating VARCHAR(50),
    closest_metro VARCHAR(200),
    
    -- Contact Info
    department VARCHAR(500),
    contact_name VARCHAR(500),
    contact_title VARCHAR(500),
    contact_email VARCHAR(500),
    email_pattern VARCHAR(200),
    
    -- Job Details
    description TEXT,
    requirements TEXT,
    skills ARRAY,
    
    -- Metadata
    scraped_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    source VARCHAR(100) DEFAULT 'builtin_la'
);

-- ============================================
-- STAGING LAYER: Cleaned & enriched
-- ============================================

USE SCHEMA STAGING;

CREATE OR REPLACE VIEW JOBS_CLEANED AS
SELECT 
    job_id,
    UPPER(TRIM(title)) as title,
    UPPER(TRIM(company)) as company,
    location,
    address,
    area,
    job_url,
    apply_url,
    
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
    contact_email,
    
    scraped_at
FROM RAW.JOBS
WHERE job_url IS NOT NULL;

-- ============================================
-- MARTS LAYER: Analytics-ready tables
-- ============================================

USE SCHEMA MARTS;

-- My top targets (Excellent commute only)
CREATE OR REPLACE VIEW MY_TARGETS AS
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
FROM STAGING.JOBS_CLEANED
WHERE commute_score >= 75  -- Excellent or Good only
ORDER BY commute_score DESC, transit_changes ASC;

-- Companies by area
CREATE OR REPLACE VIEW COMPANIES_BY_AREA AS
SELECT 
    area,
    COUNT(DISTINCT company) as company_count,
    COUNT(*) as job_count,
    AVG(commute_score) as avg_commute_score,
    ARRAY_AGG(DISTINCT company) as companies
FROM STAGING.JOBS_CLEANED
GROUP BY area
ORDER BY job_count DESC;

-- Network tracking table
CREATE OR REPLACE TABLE REFERRAL_PATHS (
    id INTEGER AUTOINCREMENT,
    company VARCHAR(500),
    target_person VARCHAR(500),
    target_title VARCHAR(500),
    connector_name VARCHAR(500),
    connector_relationship VARCHAR(1000),
    connection_tier INTEGER,
    notes TEXT,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (id)
);

-- ============================================
-- SUCCESS! 
-- ============================================

SELECT 'Setup complete! 🚀' as status;
SELECT 'Database: JOB_SEARCH' as info;
SELECT 'Schemas: RAW, STAGING, MARTS' as info;

