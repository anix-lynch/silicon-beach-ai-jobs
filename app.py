#!/usr/bin/env python3
"""
LA Tech Job Map + Network Tracker
Interactive Streamlit app to visualize jobs and track referral paths
Run locally: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import duckdb
from datetime import datetime
import os

# ==============================================================================
# CONFIG
# ==============================================================================

st.set_page_config(
    page_title="LA Tech Job Finder",
    page_icon="🗺️",
    layout="wide"
)

DB_PATH = "data/network.duckdb"
CSV_PATH = "data/raw/silicon_beach_contacts_20251110_174236.csv"

# ==============================================================================
# DATABASE SETUP
# ==============================================================================

def init_database():
    """Initialize DuckDB with tables for tracking referrals"""
    conn = duckdb.connect(DB_PATH)
    
    # Create tables if they don't exist
    conn.execute("""
        CREATE TABLE IF NOT EXISTS referral_paths (
            id INTEGER PRIMARY KEY,
            target_company VARCHAR,
            target_person VARCHAR,
            target_title VARCHAR,
            connector_name VARCHAR,
            connector_relationship VARCHAR,
            connection_tier INTEGER,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.execute("""
        CREATE SEQUENCE IF NOT EXISTS referral_id_seq START 1
    """)
    
    conn.close()

def add_referral(company, target_person, target_title, connector_name, relationship, tier, notes):
    """Add a referral path to database"""
    conn = duckdb.connect(DB_PATH)
    conn.execute("""
        INSERT INTO referral_paths 
        (id, target_company, target_person, target_title, connector_name, 
         connector_relationship, connection_tier, notes)
        VALUES 
        (nextval('referral_id_seq'), ?, ?, ?, ?, ?, ?, ?)
    """, [company, target_person, target_title, connector_name, relationship, tier, notes])
    conn.close()

def get_referrals(company=None):
    """Get all referral paths, optionally filtered by company"""
    conn = duckdb.connect(DB_PATH)
    if company:
        df = conn.execute("""
            SELECT * FROM referral_paths 
            WHERE target_company = ?
            ORDER BY created_at DESC
        """, [company]).df()
    else:
        df = conn.execute("""
            SELECT * FROM referral_paths 
            ORDER BY created_at DESC
        """).df()
    conn.close()
    return df

# ==============================================================================
# LOAD DATA
# ==============================================================================

@st.cache_data
def load_jobs():
    """Load job data from CSV"""
    if not os.path.exists(CSV_PATH):
        st.error(f"CSV not found: {CSV_PATH}")
        return None
    
    df = pd.read_csv(CSV_PATH)
    return df

# ==============================================================================
# GEOCODING (approximate - using area)
# ==============================================================================

AREA_COORDS = {
    "Culver City": (34.0211, -118.3965),
    "Santa Monica": (34.0195, -118.4912),
    "Playa Vista": (33.9777, -118.4198),
    "West LA": (34.0522, -118.4437),
    "Downtown LA": (34.0407, -118.2468),
    "Hollywood": (34.0928, -118.3287),
    "West Hollywood": (34.0900, -118.3617),
    "Hawthorne": (33.9164, -118.3526),
    "El Segundo": (33.9192, -118.4165),
}

def get_coords(area):
    """Get approximate coordinates for an area"""
    return AREA_COORDS.get(area, (34.0211, -118.3965))

# ==============================================================================
# MAP VISUALIZATION
# ==============================================================================

def create_map(df, selected_commute="All"):
    """Create interactive folium map"""
    
    # Filter by commute rating
    if selected_commute != "All":
        df = df[df['commute_rating'].str.contains(selected_commute)]
    
    # Center on Culver City (your home)
    m = folium.Map(
        location=[34.0211, -118.3965],
        zoom_start=11,
        tiles="OpenStreetMap"
    )
    
    # Add home marker
    folium.Marker(
        [34.0211, -118.3965],
        popup="🏠 Your Home<br>Culver City",
        icon=folium.Icon(color="red", icon="home", prefix='fa'),
        tooltip="Your Location"
    ).add_to(m)
    
    # Add company markers
    for idx, row in df.iterrows():
        coords = get_coords(row['area'])
        
        # Color by commute rating
        if '⭐⭐⭐' in str(row['commute_rating']):
            color = 'green'
            icon = 'star'
        elif '⭐⭐' in str(row['commute_rating']):
            color = 'orange'
            icon = 'star-half'
        else:
            color = 'gray'
            icon = 'circle'
        
        # Create popup content
        popup_html = f"""
        <div style="width: 300px">
            <h4>{row['company']}</h4>
            <b>Area:</b> {row['area']}<br>
            <b>Commute:</b> {row['transit_duration']}<br>
            <b>Routes:</b> {row['transit_routes']}<br>
            <b>Rating:</b> {row['commute_rating']}<br>
            <br>
            <a href="{row['career_url']}" target="_blank">🔗 Career Page</a><br>
            <a href="{row['google_maps_link']}" target="_blank">🗺️ Get Directions</a><br>
            <a href="{row['linkedin_url']}" target="_blank">👔 Find Hiring Manager</a>
        </div>
        """
        
        folium.Marker(
            coords,
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(color=color, icon=icon, prefix='fa'),
            tooltip=f"{row['company']} - {row['transit_duration']}"
        ).add_to(m)
    
    return m

# ==============================================================================
# MAIN APP
# ==============================================================================

def main():
    init_database()
    
    st.title("🗺️ LA Tech Job Finder + Network Tracker")
    st.markdown("---")
    
    # Load data
    df = load_jobs()
    if df is None:
        return
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    commute_filter = st.sidebar.selectbox(
        "Commute Rating",
        ["All", "Excellent", "Good", "Acceptable"]
    )
    
    area_filter = st.sidebar.multiselect(
        "Areas",
        options=df['area'].unique().tolist(),
        default=df['area'].unique().tolist()
    )
    
    # Filter data
    filtered_df = df[df['area'].isin(area_filter)]
    
    # Main layout - two columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📍 Job Map")
        st.markdown(f"**{len(filtered_df)} companies** | 🟢 Excellent (<40 min) | 🟠 Good | ⚫ Acceptable")
        
        # Create and display map
        job_map = create_map(filtered_df, commute_filter)
        folium_static(job_map, width=800, height=600)
    
    with col2:
        st.header("📊 Summary")
        
        # Stats
        excellent = len(df[df['commute_rating'].str.contains('⭐⭐⭐')])
        good = len(df[df['commute_rating'].str.contains('⭐⭐')]) - excellent
        
        st.metric("🟢 Excellent Commute", excellent)
        st.metric("🟠 Good Commute", good)
        st.metric("📍 Total Companies", len(df))
        
        st.markdown("---")
        
        # Top companies
        st.subheader("🏆 Top Companies (Best Commute)")
        top_companies = df[df['commute_rating'].str.contains('⭐⭐⭐')].sort_values('transit_duration')
        
        for idx, row in top_companies.head(6).iterrows():
            with st.expander(f"**{row['company']}** - {row['transit_duration']}"):
                st.write(f"**Area:** {row['area']}")
                st.write(f"**Route:** {row['transit_routes']}")
                st.markdown(f"[Career Page]({row['career_url']})")
                st.markdown(f"[Find Hiring Manager]({row['linkedin_url']})")
    
    # Network Tracker Section
    st.markdown("---")
    st.header("🔗 Network Tracker")
    
    tab1, tab2 = st.tabs(["➕ Add Referral Path", "📋 View Connections"])
    
    with tab1:
        st.subheader("Record a Warm Intro Path")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            target_company = st.selectbox(
                "Target Company",
                options=df['company'].tolist()
            )
            target_person = st.text_input("Hiring Manager Name", placeholder="e.g., David Shi")
            target_title = st.text_input("Their Title", placeholder="e.g., Data Engineering Manager")
        
        with col_b:
            connector_name = st.text_input("Your Connection", placeholder="e.g., Elise Sha")
            relationship = st.text_input("How do you know them?", placeholder="e.g., Chicago Booth Alum")
            tier = st.select_slider("Connection Tier", options=[1, 2, 3], value=2)
        
        notes = st.text_area("Notes", placeholder="e.g., Met at Booth mixer 2023, she offered to intro me")
        
        if st.button("💾 Save Referral Path"):
            if target_person and connector_name:
                add_referral(
                    target_company, target_person, target_title,
                    connector_name, relationship, tier, notes
                )
                st.success(f"✅ Saved: {connector_name} → {target_person} at {target_company}")
                st.rerun()
            else:
                st.error("Please fill in at least Target Person and Connector Name")
    
    with tab2:
        st.subheader("Your Network Connections")
        
        # Filter by company
        company_filter = st.selectbox(
            "Filter by Company (optional)",
            options=["All"] + df['company'].tolist()
        )
        
        if company_filter == "All":
            referrals = get_referrals()
        else:
            referrals = get_referrals(company_filter)
        
        if len(referrals) == 0:
            st.info("No referral paths recorded yet. Add your first one above!")
        else:
            for idx, ref in referrals.iterrows():
                with st.expander(f"**{ref['target_company']}** - {ref['target_person']} (Tier {ref['connection_tier']})"):
                    st.write(f"**🎯 Target:** {ref['target_person']}")
                    st.write(f"**💼 Title:** {ref['target_title']}")
                    st.write(f"**🔗 Via:** {ref['connector_name']}")
                    st.write(f"**🤝 Relationship:** {ref['connector_relationship']}")
                    st.write(f"**📝 Notes:** {ref['notes']}")
                    st.caption(f"Added: {ref['created_at']}")
    
    # Company Details Table
    st.markdown("---")
    st.header("📋 All Companies")
    
    # Display table
    display_df = filtered_df[[
        'company', 'area', 'transit_duration', 'transit_routes', 
        'commute_rating', 'career_url'
    ]].copy()
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

if __name__ == "__main__":
    main()

