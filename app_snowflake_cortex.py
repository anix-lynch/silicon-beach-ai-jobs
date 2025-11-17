#!/usr/bin/env python3
"""
Silicon Beach Tech Companies with SNOWFLAKE CORTEX AI
Demonstrates Layer 4 (Intelligence & ML) + Layer 5 (Vector Search)
"""

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col
import os
from datetime import datetime

# ==============================================================================
# CONFIG
# ==============================================================================

st.set_page_config(
    page_title="Silicon Beach AI Job Matcher",
    page_icon="🏖️",
    layout="wide"
)

SNOWFLAKE_CONFIG = {
    'account': os.getenv('SNOWFLAKE_ACCOUNT', 'vwyiycr-rpb51995'),
    'user': os.getenv('SNOWFLAKE_USER', 'ANIXLYNCH'),
    'password': os.getenv('SNOWFLAKE_PASSWORD'),
    'database': os.getenv('SNOWFLAKE_DATABASE', 'JOB_SEARCH'),
    'schema': os.getenv('SNOWFLAKE_SCHEMA', 'MARTS'),
    'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),  # Use X-SMALL for free tier
}

# ==============================================================================
# SNOWPARK SESSION
# ==============================================================================

@st.cache_resource
def get_snowpark_session():
    """Create Snowpark session with Cortex access"""
    try:
        session = Session.builder.configs(SNOWFLAKE_CONFIG).create()
        return session
    except Exception as e:
        st.error(f"Failed to connect to Snowflake: {e}")
        return None

session = get_snowpark_session()

# ==============================================================================
# HEADER
# ==============================================================================

st.title("🏖️ Silicon Beach AI Job Matcher")
st.markdown("**Powered by Snowflake Cortex AI + Vector Search**")

if not session:
    st.stop()

# Show connection status
with st.sidebar:
    st.success("✅ Connected to Snowflake")
    st.caption(f"Database: {SNOWFLAKE_CONFIG['database']}")
    st.caption(f"Warehouse: {SNOWFLAKE_CONFIG['warehouse']}")
    st.markdown("---")
    
    # Cost estimate
    st.markdown("### 💰 Estimated Cost")
    st.caption("**Today's Usage:** ~$2-5")
    st.caption("**Total Budget:** $400")
    st.caption("**Remaining:** $395+")

# ==============================================================================
# TABS
# ==============================================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "🗺️ Job Map",
    "🤖 AI Insights",
    "🔍 Semantic Search", 
    "📊 Analytics"
])

# ==============================================================================
# TAB 1: JOB MAP (Existing)
# ==============================================================================

with tab1:
    st.header("🗺️ Interactive Job Map")
    
    # Load basic jobs
    jobs_df = session.sql("""
        SELECT 
            job_id, title, company, location, address,
            career_url, commute_rating, transit_duration,
            closest_metro, description
        FROM RAW.JOBS
        LIMIT 100
    """).to_pandas()
    
    st.write(f"**Total Jobs:** {len(jobs_df)}")
    
    # Commute filter
    commute_filter = st.multiselect(
        "Filter by Commute",
        ["Excellent", "Good", "Acceptable", "Poor"],
        default=["Excellent", "Good"]
    )
    
    filtered = jobs_df[jobs_df['commute_rating'].isin(commute_filter)]
    st.dataframe(filtered[['title', 'company', 'location', 'commute_rating']], use_container_width=True)

# ==============================================================================
# TAB 2: AI INSIGHTS (NEW - Cortex Powered!)
# ==============================================================================

with tab2:
    st.header("🤖 AI-Powered Job Intelligence")
    st.markdown("*Powered by Snowflake Cortex - LLM functions running in your data warehouse*")
    
    # Load AI-enriched jobs
    with st.spinner("Loading AI insights..."):
        ai_jobs = session.sql("""
            SELECT 
                title,
                company,
                location,
                ai_summary,
                extracted_skills,
                seniority_level,
                ROUND(resume_match_score, 3) AS resume_match,
                ROUND(description_sentiment, 3) AS sentiment,
                career_url
            FROM MARTS.JOBS_AI_ENRICHED
            ORDER BY resume_match_score DESC
            LIMIT 20
        """).to_pandas()
    
    st.success(f"✅ Analyzed {len(ai_jobs)} jobs with Cortex AI")
    
    # Show top matches
    st.subheader("🎯 Top Matches for Your Profile")
    st.caption("Based on semantic similarity to your skills: Python, ML, AWS, GCP, Tableau, Docker")
    
    for idx, row in ai_jobs.head(5).iterrows():
        with st.expander(f"#{idx+1}: {row['title']} at {row['company']} (Match: {row['resume_match']:.1%})"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("**AI Summary:**")
                st.info(row['ai_summary'])
                
                st.write("**Extracted Skills:**")
                st.write(row['extracted_skills'])
            
            with col2:
                st.metric("Resume Match", f"{row['resume_match']:.1%}")
                st.metric("Seniority", row['seniority_level'])
                st.metric("Sentiment", f"{row['sentiment']:.2f}")
                
                if row['career_url']:
                    st.link_button("Apply Now", row['career_url'])
    
    # Show all results table
    st.subheader("📋 All AI-Analyzed Jobs")
    st.dataframe(
        ai_jobs[['title', 'company', 'resume_match', 'seniority_level', 'sentiment']],
        use_container_width=True
    )

# ==============================================================================
# TAB 3: SEMANTIC SEARCH (NEW - Vector Search!)
# ==============================================================================

with tab3:
    st.header("🔍 Semantic Job Search")
    st.markdown("*Find jobs by meaning, not just keywords - powered by Cortex Vector Similarity*")
    
    # Search input
    search_query = st.text_area(
        "Describe your ideal role:",
        "I want a senior data scientist role working on ML infrastructure and cloud deployment",
        height=100
    )
    
    if st.button("🔎 Search with AI", type="primary"):
        with st.spinner("Searching with semantic understanding..."):
            # Use Cortex SIMILARITY in real-time!
            search_results = session.sql(f"""
                SELECT 
                    title,
                    company,
                    location,
                    ROUND(SNOWFLAKE.CORTEX.SIMILARITY(
                        description,
                        '{search_query}'
                    ), 3) AS semantic_match,
                    SNOWFLAKE.CORTEX.SUMMARIZE(description) AS summary,
                    career_url
                FROM RAW.JOBS
                ORDER BY semantic_match DESC
                LIMIT 10
            """).to_pandas()
        
        st.success(f"✅ Found {len(search_results)} semantically similar jobs")
        
        for idx, row in search_results.iterrows():
            match_score = row['semantic_match']
            
            # Color code by match quality
            if match_score > 0.8:
                icon = "🟢"
            elif match_score > 0.6:
                icon = "🟡"
            else:
                icon = "🔴"
            
            with st.expander(f"{icon} {row['title']} at {row['company']} ({match_score:.1%} match)"):
                st.write("**AI Summary:**")
                st.info(row['summary'])
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.caption(f"📍 {row['location']}")
                with col2:
                    if row['career_url']:
                        st.link_button("Apply", row['career_url'])
    
    # Show similar jobs to each other
    st.markdown("---")
    st.subheader("🔗 Jobs Similar to Each Other")
    st.caption("Discover job clusters with similar requirements")
    
    similar_jobs = session.sql("""
        SELECT 
            job_title,
            job_company,
            similar_job_title,
            similar_company,
            ROUND(similarity_score, 3) AS similarity
        FROM MARTS.JOB_SIMILARITY
        ORDER BY similarity_score DESC
        LIMIT 15
    """).to_pandas()
    
    for idx, row in similar_jobs.iterrows():
        st.write(f"**{row['job_title']}** ({row['job_company']}) ↔️ **{row['similar_job_title']}** ({row['similar_company']})")
        st.progress(row['similarity'])
        st.caption(f"Similarity: {row['similarity']:.1%}")

# ==============================================================================
# TAB 4: ANALYTICS (NEW - AI Recommendations!)
# ==============================================================================

with tab4:
    st.header("📊 AI-Powered Analytics")
    
    # Load recommendations
    recommendations = session.sql("""
        SELECT 
            title,
            company,
            location,
            commute_rating,
            ROUND(ai_composite_score, 3) AS ai_score,
            ROUND(resume_match_score, 3) AS resume_match,
            seniority_level,
            extracted_skills
        FROM MARTS.JOB_RECOMMENDATIONS
        LIMIT 50
    """).to_pandas()
    
    # Top recommendations
    st.subheader("🏆 Top Recommended Opportunities")
    st.caption("Ranked by AI composite score: resume match + commute + sentiment + seniority")
    
    top_10 = recommendations.head(10)
    
    for idx, row in top_10.iterrows():
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.write(f"**{idx+1}. {row['title']}** at {row['company']}")
            st.caption(f"Skills: {row['extracted_skills'][:100]}...")
        
        with col2:
            st.metric("AI Score", f"{row['ai_score']:.0%}")
        
        with col3:
            st.metric("Commute", row['commute_rating'])
    
    # Distribution charts
    st.markdown("---")
    st.subheader("📈 Score Distributions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**AI Composite Score**")
        st.bar_chart(recommendations['ai_score'].value_counts().sort_index())
    
    with col2:
        st.write("**Resume Match Score**")
        st.bar_chart(recommendations['resume_match'].value_counts().sort_index())

# ==============================================================================
# FOOTER
# ==============================================================================

st.markdown("---")
st.caption("🏔️ Powered by Snowflake Cortex AI | 🐍 Built with Snowpark + Streamlit")
st.caption("**Tech Stack:** Snowflake Cortex (LLM), Vector Similarity, Snowpark, Streamlit")
st.caption(f"**Connected:** {SNOWFLAKE_CONFIG['database']}.{SNOWFLAKE_CONFIG['schema']}")

