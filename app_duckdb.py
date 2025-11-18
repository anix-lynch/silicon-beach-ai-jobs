#!/usr/bin/env python3
"""
Silicon Beach Tech Companies (DuckDB Edition - FREE FOREVER!)
Same beautiful app, but uses local DuckDB instead of Snowflake
Perfect for portfolio / long-term use
"""

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import duckdb
from datetime import datetime

# ==============================================================================
# CONFIG
# ==============================================================================

st.set_page_config(
    page_title="Silicon Beach Companies",
    page_icon="🏖️",
    layout="wide"
)

DUCKDB_FILE = "data/silicon_beach.duckdb"

# ==============================================================================
# DATABASE CONNECTION
# ==============================================================================

@st.cache_resource
def get_duckdb_connection():
    """Create DuckDB connection and ensure tables exist"""
    conn = duckdb.connect(DUCKDB_FILE, read_only=False)
    
    # Check if jobs_cleaned exists (table or view), if not create from CSV or empty table
    try:
        # Try to query it - works for both tables and views
        conn.execute("SELECT COUNT(*) FROM jobs_cleaned").fetchone()
    except Exception as e:
        # Table/view doesn't exist, try to create from CSV files
        import os
        csv_files = [
            "data/la_vcs_20251111_083756_enriched.csv",
            "data/builtinla_mcp_20251111_085045.csv",
        ]
        
        for csv_file in csv_files:
            if os.path.exists(csv_file):
                try:
                    df = pd.read_csv(csv_file)
                    # Standardize column names
                    df.columns = df.columns.str.lower()
                    # Create table from first CSV found
                    conn.execute("CREATE TABLE IF NOT EXISTS jobs_cleaned AS SELECT * FROM df")
                    break
                except Exception as e:
                    # Can't use st.warning in cache_resource, just continue
                    pass
        
        # If still no table, create empty one with expected schema
        try:
            conn.execute("SELECT COUNT(*) FROM jobs_cleaned").fetchone()
        except:
            # Create empty table with all possible columns
            conn.execute("""
                CREATE TABLE IF NOT EXISTS jobs_cleaned (
                    type VARCHAR,
                    company VARCHAR,
                    title VARCHAR,
                    area VARCHAR,
                    location VARCHAR,
                    address VARCHAR,
                    stage VARCHAR,
                    focus VARCHAR,
                    transit_duration VARCHAR,
                    transit_routes VARCHAR,
                    transit_changes INTEGER,
                    commute_rating VARCHAR,
                    commute_score INTEGER,
                    google_maps_link VARCHAR,
                    career_url VARCHAR,
                    job_url VARCHAR,
                    linkedin_search VARCHAR,
                    contact_name VARCHAR,
                    contact_email VARCHAR,
                    closest_metro VARCHAR
                )
            """)
        
        # Also ensure referral_paths table exists
        try:
            conn.execute("SELECT COUNT(*) FROM referral_paths").fetchone()
        except:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS referral_paths (
                    company VARCHAR,
                    target_person VARCHAR,
                    target_title VARCHAR,
                    connector_name VARCHAR,
                    connector_relationship VARCHAR,
                    connection_tier INTEGER,
                    notes VARCHAR,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    return conn

def add_referral(company, target_person, target_title, connector_name, relationship, tier, notes):
    """Add a referral path to DuckDB"""
    conn = get_duckdb_connection()
    conn.execute("""
        INSERT INTO referral_paths 
        (company, target_person, target_title, connector_name, 
         connector_relationship, connection_tier, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, [company, target_person, target_title, connector_name, relationship, tier, notes])

def get_referrals(company=None):
    """Get all referral paths from DuckDB"""
    conn = get_duckdb_connection()
    if company:
        df = conn.execute("""
            SELECT * FROM referral_paths 
            WHERE company = ? 
            ORDER BY created_at DESC
        """, [company]).df()
    else:
        df = conn.execute("""
            SELECT * FROM referral_paths 
            ORDER BY created_at DESC
        """).df()
    return df

# ==============================================================================
# LOAD DATA
# ==============================================================================

@st.cache_data(ttl=300)
def load_jobs():
    """Load job and VC data from DuckDB"""
    conn = get_duckdb_connection()
    
    # First, check what columns actually exist
    try:
        columns_info = conn.execute("DESCRIBE jobs_cleaned").fetchall()
        available_columns = [col[0].lower() for col in columns_info]
    except:
        # If describe fails, try to get columns from a sample query
        try:
            sample = conn.execute("SELECT * FROM jobs_cleaned LIMIT 1").df()
            available_columns = [col.lower() for col in sample.columns]
        except:
            # Table doesn't exist or is empty, return empty dataframe
            return pd.DataFrame()
    
    # Build SELECT with only columns that exist
    select_cols = []
    column_map = {
        'type': "COALESCE(type, 'JOB') as type",
        'company': 'company',
        'title': 'title',
        'area': 'area',
        'location': 'location',
        'address': 'address',
        'stage': 'stage',
        'focus': 'focus',
        'transit_duration': 'transit_duration',
        'transit_routes': 'transit_routes',
        'transit_changes': 'transit_changes',
        'commute_rating': 'commute_rating',
        'commute_score': 'commute_score',
        'google_maps_link': 'google_maps_link',
        'career_url': 'career_url',
        'job_url': 'job_url',
        'linkedin_search': 'linkedin_search',
        'contact_name': 'contact_name',
        'contact_email': 'contact_email',
        'closest_metro': 'closest_metro'
    }
    
    for col_name, col_expr in column_map.items():
        if col_name in available_columns:
            select_cols.append(col_expr)
        else:
            # Add NULL for missing columns
            if 'as' in col_expr:
                select_cols.append(f"NULL as {col_expr.split(' as ')[1]}")
            else:
                select_cols.append(f"NULL as {col_name}")
    
    query = f"""
        SELECT {', '.join(select_cols)}
        FROM jobs_cleaned
        ORDER BY COALESCE(type, 'JOB') DESC, COALESCE(commute_score, 0) DESC
    """
    
    try:
        df = conn.execute(query).df()
        # Ensure all expected columns exist (fill with None if missing)
        expected_cols = ['type', 'company', 'title', 'area', 'location', 'address', 
                       'stage', 'focus', 'transit_duration', 'transit_routes', 
                       'transit_changes', 'commute_rating', 'commute_score',
                       'google_maps_link', 'career_url', 'job_url', 'linkedin_search',
                       'contact_name', 'contact_email', 'closest_metro']
        for col in expected_cols:
            if col not in df.columns:
                df[col] = None
        return df
    except Exception as e:
        st.error(f"Error loading jobs: {str(e)}")
        return pd.DataFrame()

# ==============================================================================
# GEOCODING
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
    return AREA_COORDS.get(area, (34.0211, -118.3965))

# ==============================================================================
# MAP
# ==============================================================================

def create_map(df, selected_commute="All", show_jobs=True, show_vcs=True):
    if selected_commute != "All":
        df = df[df['commute_rating'].str.contains(selected_commute)]
    
    # Filter by type
    if not show_jobs:
        df = df[df['type'] == 'VC']
    if not show_vcs:
        df = df[df['type'] != 'VC']
    
    m = folium.Map(
        location=[34.0211, -118.3965],
        zoom_start=11,
        tiles="OpenStreetMap"
    )
    
    folium.Marker(
        [34.0211, -118.3965],
        popup="🏠 Your Home<br>Culver City",
        icon=folium.Icon(color="red", icon="home", prefix='fa'),
        tooltip="Your Location"
    ).add_to(m)
    
    for idx, row in df.iterrows():
        coords = get_coords(row['area'])
        
        # Different colors for VCs vs Jobs
        is_vc = row.get('type') == 'VC'
        
        if is_vc:
            # Orange pins for VCs
            if row['commute_score'] >= 100:
                color = 'orange'
                icon = 'briefcase'
            elif row['commute_score'] >= 75:
                color = 'beige'
                icon = 'briefcase'
            else:
                color = 'lightgray'
                icon = 'briefcase'
        else:
            # Green pins for Jobs
            if row['commute_score'] >= 100:
                color = 'green'
                icon = 'star'
            elif row['commute_score'] >= 75:
                color = 'lightgreen'
                icon = 'star-half'
            else:
                color = 'gray'
                icon = 'circle'
        
        if is_vc:
            popup_html = f"""
            <div style="width: 300px">
                <h4>💼 {row['company']}</h4>
                <b>Type:</b> VC Firm<br>
                <b>Stage:</b> {row.get('stage', 'N/A')}<br>
                <b>Focus:</b> {row.get('focus', 'N/A')}<br>
                <b>Area:</b> {row['area']}<br>
                <b>Commute:</b> {row['transit_duration']}<br>
                <b>Routes:</b> {row['transit_routes']}<br>
                <b>Rating:</b> {row['commute_rating']}<br>
                <br>
                <a href="{row['career_url']}" target="_blank">🔗 Search Careers</a><br>
                <a href="{row['google_maps_link']}" target="_blank">🗺️ Get Directions</a><br>
                <a href="{row.get('linkedin_search', '#')}" target="_blank">🔍 Find Partners</a>
            </div>
            """
        else:
            popup_html = f"""
            <div style="width: 300px">
                <h4>💻 {row['company']}</h4>
                <b>Type:</b> Tech Job<br>
                <b>Area:</b> {row['area']}<br>
                <b>Commute:</b> {row['transit_duration']}<br>
                <b>Routes:</b> {row['transit_routes']}<br>
                <b>Rating:</b> {row['commute_rating']}<br>
                <b>Metro:</b> {row['closest_metro']}<br>
                <br>
                <a href="{row['career_url']}" target="_blank">🔗 Career Page</a><br>
                <a href="{row['google_maps_link']}" target="_blank">🗺️ Get Directions</a><br>
                <a href="{row.get('job_url', '#')}" target="_blank">👔 Find Hiring Manager</a>
            </div>
            """
        
        folium.Marker(
            coords,
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(color=color, icon=icon, prefix='fa'),
            tooltip=f"{'💼' if is_vc else '💻'} {row['company']} - {row['transit_duration']}"
        ).add_to(m)
    
    return m

# ==============================================================================
# MAIN APP
# ==============================================================================

def main():
    st.title("🏖️ Silicon Beach Tech Companies")
    st.markdown("*Tech companies in LA's Silicon Beach area*")
    st.markdown("---")
    
    df = load_jobs()
    
    # Sidebar
    st.sidebar.header("🔍 Filters")
    
    # Type filter
    show_jobs = st.sidebar.checkbox("💻 Show Tech Jobs", value=True)
    show_vcs = st.sidebar.checkbox("💼 Show VC Firms", value=True)
    
    commute_filter = st.sidebar.selectbox(
        "Commute Rating",
        ["All", "Excellent", "Good", "Acceptable"]
    )
    
    area_filter = st.sidebar.multiselect(
        "Areas",
        options=sorted(df['area'].unique().tolist()),
        default=df['area'].unique().tolist()
    )
    
    min_score = st.sidebar.slider(
        "Minimum Commute Score",
        min_value=0,
        max_value=100,
        value=50
    )
    
    filtered_df = df[
        (df['area'].isin(area_filter)) &
        (df['commute_score'] >= min_score)
    ]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📍 Job Map")
        
        num_jobs = len(filtered_df[filtered_df['type'] != 'VC']) if 'type' in filtered_df.columns else len(filtered_df)
        num_vcs = len(filtered_df[filtered_df['type'] == 'VC']) if 'type' in filtered_df.columns else 0
        
        st.markdown(f"**{num_jobs} tech jobs | {num_vcs} VC firms** | 🟢 Green = Jobs | 🟠 Orange = VCs")
        
        job_map = create_map(filtered_df, commute_filter, show_jobs, show_vcs)
        folium_static(job_map, width=800, height=600)
    
    with col2:
        st.header("📊 Summary")
        
        excellent = len(df[df['commute_score'] >= 100])
        good = len(df[df['commute_score'] >= 75]) - excellent
        
        st.metric("🟢 Excellent Commute", excellent)
        st.metric("🟠 Good Commute", good)
        st.metric("📍 Total Companies", len(df))
        
        st.markdown("---")
        st.subheader("🏆 Top Targets")
        
        for idx, row in filtered_df.head(6).iterrows():
            with st.expander(f"**{row['company']}** - {row['transit_duration']}"):
                st.write(f"**Area:** {row['area']}")
                st.write(f"**Route:** {row['transit_routes']}")
                st.write(f"**Score:** {row['commute_score']}/100")
                if row['contact_name']:
                    st.write(f"**Contact:** {row['contact_name']}")
                if row['contact_email']:
                    st.write(f"**Email:** {row['contact_email']}")
                st.markdown(f"[Career Page]({row['career_url']})")
                st.markdown(f"[Find Hiring Manager]({row['job_url']})")
    
    # Network Tracker
    st.markdown("---")
    st.header("🔗 Network Tracker")
    
    tab1, tab2 = st.tabs(["➕ Add Referral Path", "📋 View Connections"])
    
    with tab1:
        st.subheader("Record a Warm Intro Path")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            target_company = st.selectbox("Target Company", options=sorted(df['company'].tolist()))
            target_person = st.text_input("Hiring Manager Name", placeholder="e.g., David Shi")
            target_title = st.text_input("Their Title", placeholder="e.g., Data Engineering Manager")
        
        with col_b:
            connector_name = st.text_input("Your Connection", placeholder="e.g., Elise Sha")
            relationship = st.text_input("How do you know them?", placeholder="e.g., Chicago Booth Alum")
            tier = st.select_slider("Connection Tier", options=[1, 2, 3], value=2)
        
        notes = st.text_area("Notes", placeholder="e.g., Met at Booth mixer 2023")
        
        if st.button("💾 Save Referral Path"):
            if target_person and connector_name:
                add_referral(target_company, target_person, target_title, connector_name, relationship, tier, notes)
                st.success(f"✅ Saved: {connector_name} → {target_person} at {target_company}")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("Please fill in at least Target Person and Connector Name")
    
    with tab2:
        st.subheader("Your Network Connections")
        
        company_filter = st.selectbox(
            "Filter by Company (optional)",
            options=["All"] + sorted(df['company'].tolist())
        )
        
        referrals = get_referrals() if company_filter == "All" else get_referrals(company_filter)
        
        if len(referrals) == 0:
            st.info("No referral paths recorded yet. Add your first one above!")
        else:
            for idx, ref in referrals.iterrows():
                with st.expander(f"**{ref['company']}** - {ref['target_person']} (Tier {ref['connection_tier']})"):
                    st.write(f"**🎯 Target:** {ref['target_person']}")
                    st.write(f"**💼 Title:** {ref['target_title']}")
                    st.write(f"**🔗 Via:** {ref['connector_name']}")
                    st.write(f"**🤝 Relationship:** {ref['connector_relationship']}")
                    st.write(f"**📝 Notes:** {ref['notes']}")
                    st.caption(f"Added: {ref['created_at']}")
    
    # Table
    st.markdown("---")
    st.header("📋 All Companies")
    
    display_df = filtered_df[['company', 'area', 'transit_duration', 'transit_routes', 'commute_rating', 'commute_score']].copy()
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "commute_score": st.column_config.ProgressColumn(
                "Score",
                format="%d",
                min_value=0,
                max_value=100,
            ),
        }
    )
    
    st.markdown("---")
    st.caption("💡 Data stored in local DuckDB | Free forever | Deploy to Streamlit Cloud")

if __name__ == "__main__":
    main()


