#!/usr/bin/env python3
"""
LA Tech Job Map + Network Tracker (Snowflake Edition)
Interactive Streamlit app reading from Snowflake
Run: streamlit run app_snowflake.py
"""

import streamlit as st
import pandas as pd
import folium
import os
from streamlit_folium import folium_static
import snowflake.connector
from datetime import datetime
from scripts.get_secret import get_secret

# ==============================================================================
# CONFIG
# ==============================================================================

st.set_page_config(
    page_title="Silicon Beach Companies",
    page_icon="🏖️",
    layout="wide"
)

SNOWFLAKE_CONFIG = {
    'account': get_secret('SNOWFLAKE_ACCOUNT', 'vwyiycr-rpb51995'),
    'user': get_secret('SNOWFLAKE_USER', 'ANIXLYNCH'),
    'password': get_secret('SNOWFLAKE_PASSWORD'),  # REQUIRED - uses universal secret loader
    'database': get_secret('SNOWFLAKE_DATABASE', 'JOB_SEARCH'),
    'warehouse': get_secret('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
}
if not SNOWFLAKE_CONFIG['password']:
    st.error("❌ SNOWFLAKE_PASSWORD environment variable is required")
    st.stop()

# ==============================================================================
# DATABASE CONNECTION
# ==============================================================================

@st.cache_resource
def get_snowflake_connection():
    """Create Snowflake connection"""
    return snowflake.connector.connect(**SNOWFLAKE_CONFIG)

def add_referral(company, target_person, target_title, connector_name, relationship, tier, notes):
    """Add a referral path to Snowflake"""
    conn = get_snowflake_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO MARTS.REFERRAL_PATHS 
            (company, target_person, target_title, connector_name, 
             connector_relationship, connection_tier, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [company, target_person, target_title, connector_name, relationship, tier, notes])
        conn.commit()
    finally:
        cursor.close()

def get_referrals(company=None):
    """Get all referral paths from Snowflake"""
    conn = get_snowflake_connection()
    cursor = conn.cursor()
    if company:
        query = "SELECT * FROM MARTS.REFERRAL_PATHS WHERE company = ? ORDER BY created_at DESC"
        cursor.execute(query, [company])
    else:
        query = "SELECT * FROM MARTS.REFERRAL_PATHS ORDER BY created_at DESC"
        cursor.execute(query)
    
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=columns)
    cursor.close()
    return df

# ==============================================================================
# LOAD DATA
# ==============================================================================

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_jobs():
    """Load job data from Snowflake"""
    conn = get_snowflake_connection()
    cursor = conn.cursor()
    query = """
        SELECT 
            type,
            company,
            title,
            area,
            location,
            address,
            transit_duration,
            transit_routes,
            transit_changes,
            commute_rating,
            commute_score,
            google_maps_link,
            career_url,
            linkedin_search,
            contact_name,
            contact_email,
            closest_metro
        FROM STAGING.JOBS_CLEANED
        ORDER BY type DESC, commute_score DESC
    """
    cursor.execute(query)
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=columns)
    cursor.close()
    
    df.columns = df.columns.str.lower()
    
    # Add job_url as alias to career_url for compatibility
    df['job_url'] = df['career_url']
    
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
    "Venice": (33.9850, -118.4695),
    "Los Angeles": (34.0522, -118.2437),
    "Beverly Hills": (34.0736, -118.4004),
    "Century City": (34.0583, -118.4170),
    "Pasadena": (34.1478, -118.1445),
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
        
        # Check if it's a VC or Job
        is_vc = row.get('type') == 'VC'
        
        # Color by type and commute score
        if is_vc:
            # VCs always orange
            color = 'orange'
            icon = 'briefcase'
        elif row['commute_score'] >= 100:
            color = 'green'
            icon = 'star'
        elif row['commute_score'] >= 75:
            color = 'lightgreen'
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
            <b>Metro:</b> {row['closest_metro']}<br>
            <br>
            <a href="{row['career_url']}" target="_blank">🔗 Career Page</a><br>
            <a href="{row['google_maps_link']}" target="_blank">🗺️ Get Directions</a><br>
            <a href="{row['job_url']}" target="_blank">👔 Find Hiring Manager</a>
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
    st.title("🏖️ Silicon Beach Tech Companies")
    st.markdown("*Tech companies in LA's Silicon Beach area*")
    st.markdown("---")
    
    # Load data
    with st.spinner("Loading companies..."):
        df = load_jobs()
    
    # Fix column names (Snowflake uppercases them)
    df.columns = df.columns.str.lower()
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
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
    
    # Filter data
    # Include VCs (which may have NULL commute_score) OR jobs that meet commute score
    filtered_df = df[
        (df['area'].isin(area_filter)) &
        ((df['type'] == 'VC') | (df['commute_score'] >= min_score))
    ]
    
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
        
        # Stats from Snowflake
        excellent = len(df[df['commute_score'] >= 100])
        good = len(df[df['commute_score'] >= 75]) - excellent
        
        st.metric("🟢 Excellent Commute", excellent)
        st.metric("🟠 Good Commute", good)
        st.metric("📍 Total Companies", len(df))
        
        st.markdown("---")
        
        # Top companies from MY_TARGETS view
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
                options=sorted(df['company'].tolist())
            )
            target_person = st.text_input("Hiring Manager Name", placeholder="e.g., David Shi")
            target_title = st.text_input("Their Title", placeholder="e.g., Data Engineering Manager")
        
        with col_b:
            connector_name = st.text_input("Your Connection", placeholder="e.g., Elise Sha")
            relationship = st.text_input("How do you know them?", placeholder="e.g., Chicago Booth Alum")
            tier = st.select_slider("Connection Tier", options=[1, 2, 3], value=2)
        
        notes = st.text_area("Notes", placeholder="e.g., Met at Booth mixer 2023, she offered to intro me")
        
        if st.button("💾 Save to Snowflake"):
            if target_person and connector_name:
                add_referral(
                    target_company, target_person, target_title,
                    connector_name, relationship, tier, notes
                )
                st.success(f"✅ Saved to Snowflake: {connector_name} → {target_person} at {target_company}")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("Please fill in at least Target Person and Connector Name")
    
    with tab2:
        st.subheader("Your Network Connections (from Snowflake)")
        
        # Filter by company
        company_filter = st.selectbox(
            "Filter by Company (optional)",
            options=["All"] + sorted(df['company'].tolist())
        )
        
        if company_filter == "All":
            referrals = get_referrals()
        else:
            referrals = get_referrals(company_filter)
        
        if len(referrals) == 0:
            st.info("No referral paths in Snowflake yet. Add your first one above!")
        else:
            # Convert column names to handle Snowflake's uppercase
            referrals.columns = referrals.columns.str.upper()
            for idx, ref in referrals.iterrows():
                company = ref.get('COMPANY', 'Unknown')
                target = ref.get('TARGET_PERSON', 'Unknown')
                tier = ref.get('CONNECTION_TIER', '?')
                with st.expander(f"**{company}** - {target} (Tier {tier})"):
                    st.write(f"**🎯 Target:** {ref.get('TARGET_PERSON', 'N/A')}")
                    st.write(f"**💼 Title:** {ref.get('TARGET_TITLE', 'N/A')}")
                    st.write(f"**🔗 Via:** {ref.get('CONNECTOR_NAME', 'N/A')}")
                    st.write(f"**🤝 Relationship:** {ref.get('CONNECTOR_RELATIONSHIP', 'N/A')}")
                    st.write(f"**📝 Notes:** {ref.get('NOTES', 'N/A')}")
                    st.caption(f"Added: {ref.get('CREATED_AT', 'N/A')}")
    
    # Company Details Table
    st.markdown("---")
    st.header("📋 All Companies (Live from Snowflake)")
    
    # Display table
    display_df = filtered_df[[
        'company', 'area', 'transit_duration', 'transit_routes', 
        'commute_rating', 'commute_score'
    ]].copy()
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "commute_score": st.column_config.ProgressColumn(
                "Score",
                help="Commute score (0-100)",
                format="%d",
                min_value=0,
                max_value=100,
            ),
        }
    )
    
    # Footer
    st.markdown("---")
    st.caption("💡 Data stored in Snowflake | Query anytime via SQL")

if __name__ == "__main__":
    main()

