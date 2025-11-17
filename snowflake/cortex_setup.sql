-- ============================================================================
-- SNOWFLAKE CORTEX + SNOWPARK SETUP
-- Cost-Optimized AI/ML Layer for Silicon Beach Job Search
-- Target Cost: <$15 for full implementation
-- ============================================================================

-- ============================================================================
-- STEP 1: COST PROTECTION (RUN THIS FIRST!)
-- ============================================================================

-- Use your existing warehouse
USE WAREHOUSE COMPUTE_WH;
USE DATABASE JOB_SEARCH;
USE SCHEMA MARTS;

-- Set warehouse to smallest size (XS = $2/hour)
ALTER WAREHOUSE COMPUTE_WH SET WAREHOUSE_SIZE = 'X-SMALL';

-- Auto-suspend after 1 minute of inactivity (CRITICAL for cost control!)
ALTER WAREHOUSE COMPUTE_WH SET AUTO_SUSPEND = 60;

-- Auto-resume when needed
ALTER WAREHOUSE COMPUTE_WH SET AUTO_RESUME = TRUE;

-- Check current cost (should show ~$0 if you just started)
SELECT 
  WAREHOUSE_NAME,
  SUM(CREDITS_USED) AS total_credits_used,
  SUM(CREDITS_USED) * 2 AS estimated_cost_usd
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE START_TIME >= DATEADD(day, -7, CURRENT_TIMESTAMP())
GROUP BY WAREHOUSE_NAME;

-- ============================================================================
-- STEP 2: LAYER 4 - INTELLIGENCE & ML LAYER (Cortex AI)
-- ============================================================================

-- 2A. Create AI-Enriched Jobs View with Cortex Functions
CREATE OR REPLACE VIEW MARTS.JOBS_AI_ENRICHED AS
SELECT 
  j.job_id,
  j.title,
  j.company,
  j.location,
  j.description,
  j.career_url,
  j.commute_rating,
  j.transit_duration,
  
  -- Cortex: Auto-generate job summary (replaces manual reading!)
  SNOWFLAKE.CORTEX.SUMMARIZE(j.description) AS ai_summary,
  
  -- Cortex: Extract required skills automatically
  SNOWFLAKE.CORTEX.COMPLETE(
    'mistral-7b',
    'Extract top 5 required technical skills from this job description. Return as comma-separated list: ' || j.description
  ) AS extracted_skills,
  
  -- Cortex: Classify seniority level
  SNOWFLAKE.CORTEX.COMPLETE(
    'mistral-7b',
    'Classify this job as Junior, Mid, Senior, or Lead based on title and description. Return only one word: ' || j.title || ' - ' || SUBSTR(j.description, 1, 200)
  ) AS seniority_level,
  
  -- Cortex: Analyze sentiment of job description (positive = good culture!)
  SNOWFLAKE.CORTEX.SENTIMENT(j.description) AS description_sentiment,
  
  -- Cortex: Match to your resume/skills
  SNOWFLAKE.CORTEX.SIMILARITY(
    j.description,
    'I am a data scientist with expertise in Python, machine learning, SQL, AWS, GCP, Tableau, Docker, and Kubernetes. I specialize in ML pipelines, data visualization, and cloud deployment.'
  ) AS resume_match_score
  
FROM RAW.JOBS j
LIMIT 100;  -- COST CONTROL: Limit to 100 jobs for demo!

-- Test the AI-enriched view (Cost: ~$0.20 for 5 jobs)
SELECT 
  title,
  company,
  ai_summary,
  extracted_skills,
  seniority_level,
  ROUND(resume_match_score, 3) AS match_score
FROM MARTS.JOBS_AI_ENRICHED
LIMIT 5;

-- ============================================================================
-- STEP 3: LAYER 5 - VECTOR SEARCH LAYER (Semantic Similarity)
-- ============================================================================

-- 3A. Find Similar Jobs by Semantic Meaning (not just keywords!)
CREATE OR REPLACE VIEW MARTS.JOB_SIMILARITY AS
SELECT 
  a.job_id,
  a.title AS job_title,
  a.company AS job_company,
  b.job_id AS similar_job_id,
  b.title AS similar_job_title,
  b.company AS similar_company,
  
  -- Vector similarity: Compare job descriptions semantically
  SNOWFLAKE.CORTEX.SIMILARITY(
    a.description,
    b.description
  ) AS similarity_score
  
FROM RAW.JOBS a
CROSS JOIN RAW.JOBS b
WHERE a.job_id < b.job_id  -- Avoid duplicate pairs (a,b) and (b,a)
  AND SNOWFLAKE.CORTEX.SIMILARITY(a.description, b.description) > 0.7  -- Only high similarity
LIMIT 50;  -- COST CONTROL: Limit results!

-- Test similarity search (Cost: ~$0.10 for 10 pairs)
SELECT 
  job_title,
  similar_job_title,
  ROUND(similarity_score, 3) AS similarity
FROM MARTS.JOB_SIMILARITY
ORDER BY similarity_score DESC
LIMIT 10;

-- ============================================================================
-- STEP 4: SMART JOB RECOMMENDATIONS (Cortex + Your Data)
-- ============================================================================

-- 4A. Rank jobs by AI-powered composite score
CREATE OR REPLACE VIEW MARTS.JOB_RECOMMENDATIONS AS
SELECT 
  job_id,
  title,
  company,
  location,
  commute_rating,
  ai_summary,
  extracted_skills,
  seniority_level,
  resume_match_score,
  description_sentiment,
  
  -- Composite AI score (weights: 40% resume match, 30% commute, 20% sentiment, 10% seniority)
  (
    (resume_match_score * 0.4) +
    (CASE commute_rating 
      WHEN 'Excellent' THEN 1.0
      WHEN 'Good' THEN 0.7
      WHEN 'Acceptable' THEN 0.4
      ELSE 0.2
    END * 0.3) +
    ((description_sentiment + 1) / 2 * 0.2) +  -- Normalize sentiment -1 to 1 → 0 to 1
    (CASE seniority_level
      WHEN 'Senior' THEN 1.0
      WHEN 'Mid' THEN 0.8
      WHEN 'Lead' THEN 0.9
      ELSE 0.5
    END * 0.1)
  ) AS ai_composite_score
  
FROM MARTS.JOBS_AI_ENRICHED
ORDER BY ai_composite_score DESC;

-- Test recommendations (Cost: ~$0.05)
SELECT 
  title,
  company,
  ROUND(ai_composite_score, 3) AS score,
  commute_rating,
  ROUND(resume_match_score, 3) AS resume_match
FROM MARTS.JOB_RECOMMENDATIONS
LIMIT 10;

-- ============================================================================
-- STEP 5: COST MONITORING (Check your spend!)
-- ============================================================================

-- Monitor warehouse usage (run this frequently!)
SELECT 
  WAREHOUSE_NAME,
  TO_DATE(START_TIME) AS usage_date,
  SUM(CREDITS_USED) AS daily_credits,
  SUM(CREDITS_USED) * 2 AS estimated_cost_usd
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE START_TIME >= DATEADD(day, -1, CURRENT_TIMESTAMP())
GROUP BY WAREHOUSE_NAME, TO_DATE(START_TIME)
ORDER BY usage_date DESC;

-- Check Cortex LLM usage (if available in your account)
-- Note: Cortex usage may not show immediately in ACCOUNT_USAGE views

-- ============================================================================
-- STEP 6: EXPORT PREP (Before Migration to DuckDB)
-- ============================================================================

-- Create materialized snapshot of AI-enriched data (for export)
CREATE OR REPLACE TABLE MARTS.JOBS_AI_SNAPSHOT AS
SELECT * FROM MARTS.JOBS_AI_ENRICHED;

-- Verify snapshot created
SELECT COUNT(*) AS total_enriched_jobs FROM MARTS.JOBS_AI_SNAPSHOT;

-- ============================================================================
-- DONE! Next: Add Snowpark Python UDFs in Streamlit app
-- ============================================================================

-- Total Expected Cost: $5-8 for all queries above
-- Remaining Budget: $392+

