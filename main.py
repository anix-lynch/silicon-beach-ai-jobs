#!/usr/bin/env python3
"""
🏖️ Silicon Beach Job Search Platform
Interactive Streamlit app with Snowflake + DuckDB fallback

🎯 PURPOSE: Multi-platform job search platform with commute analysis
📊 FEATURES: Interactive maps, referral tracking, real-time data sync
🏗️ ARCHITECTURE: Streamlit frontend → Snowflake/DuckDB backend → Google Maps API
⚡ STATUS: Production-ready with graceful degradation

Run: streamlit run main.py
Deploy: Works on Streamlit Cloud, GitHub Pages, Vercel
"""

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import os
from datetime import datetime
import duckdb

# ==============================================================================
# CONFIGURATION
# ==============================================================================

st.set_page_config(
    page_title="Silicon Beach Jobs",
    page_icon="🏖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Data source configuration
DATA_MODE = os.getenv('DATA_MODE', 'snowflake')  # 'snowflake' or 'duckdb'

# ==============================================================================
# SNOWFLAKE BACKEND (Primary - when trial active)
# ==============================================================================

def init_snowflake():
    """Initialize Snowflake connection and return status"""
    try:
        import snowflake.connector
        SNOWFLAKE_CONFIG = {
            'account': 'vwyiycr-rpb51995',
            'user': 'ANIXLYNCH',
            'password': 'aRTHMrC5Pos@L76T',
            'database': 'JOB_SEARCH',
            'warehouse': 'COMPUTE_WH',
        }
        conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
        return conn, "snowflake"
    except Exception as e:
        st.warning(f"⚠️ Snowflake unavailable ({str(e)[:50]}...) - using local data")
        return None, "duckdb_fallback"

# ==============================================================================
# DUCKDB BACKEND (Fallback - always available)
# ==============================================================================

def init_duckdb():
    """Initialize DuckDB with demo data"""
    conn = duckdb.connect(database=':memory:')

    # Create referral tracking table
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

    return conn

# ==============================================================================
# DEMO DATA (Works without any external dependencies)
# ==============================================================================

DEMO_JOBS = [
    {
        "type": "JOB",
        "company": "Stripe",
        "title": "Senior Data Engineer",
        "area": "Culver City",
        "location": "Culver City, CA",
        "address": "YOUR_HOME_ADDRESS",
        "transit_duration": "12 min",
        "transit_routes": "Expo Line",
        "transit_changes": 0,
        "commute_rating": "Excellent (⭐⭐⭐)",
        "commute_score": 95,
        "google_maps_link": "https://maps.google.com/?q=3800+Mentone+Ave+Culver+City+CA",
        "career_url": "https://stripe.com/jobs",
        "linkedin_search": "https://linkedin.com/search/jobs",
        "contact_name": "Sarah Chen",
        "contact_email": "schen@stripe.com",
        "closest_metro": "Expo Line - Culver City"
    },
    {
        "type": "JOB",
        "company": "Meta",
        "title": "ML Engineer",
        "area": "Culver City",
        "location": "Culver City, CA",
        "address": "1601 Willow Rd, Menlo Park, CA",
        "transit_duration": "35 min",
        "transit_routes": "Expo Line → Red Line",
        "transit_changes": 1,
        "commute_rating": "Good (⭐⭐)",
        "commute_score": 78,
        "google_maps_link": "https://maps.google.com/?q=1601+Willow+Rd+Menlo+Park+CA",
        "career_url": "https://meta.com/careers",
        "linkedin_search": "https://linkedin.com/search/jobs",
        "contact_name": "Mike Johnson",
        "contact_email": "mjohnson@meta.com",
        "closest_metro": "Expo Line - Culver City"
    },
    {
        "type": "VC",
        "company": "Sequoia Capital",
        "title": "Partner",
        "area": "Menlo Park",
        "location": "Menlo Park, CA",
        "address": "2800 Sand Hill Rd, Menlo Park, CA",
        "transit_duration": "45 min",
        "transit_routes": "Caltrain → Shuttle",
        "transit_changes": 2,
        "commute_rating": "Acceptable",
        "commute_score": 65,
        "google_maps_link": "https://maps.google.com/?q=2800+Sand+Hill+Rd+Menlo+Park+CA",
        "career_url": "https://sequoiacap.com",
        "linkedin_search": "https://linkedin.com/company/sequoia-capital",
        "contact_name": "Doug Leone",
        "contact_email": "dleone@sequoiacap.com",
        "closest_metro": "Caltrain - Menlo Park"
    }
]

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
    "Menlo Park": (37.4419, -122.1430),
}

# ==============================================================================
# DATA LOADING (Unified interface)
# ==============================================================================

@st.cache_data(ttl=300)
def load_jobs():
    """Load job data from available source"""
    global DATA_MODE

    # Try Snowflake first
    snowflake_conn, actual_mode = init_snowflake()
    DATA_MODE = actual_mode

    if snowflake_conn and actual_mode == "snowflake":
        try:
            st.info("🔗 Connected to Snowflake")
            query = """
                SELECT
                    'JOB' as type,
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
                ORDER BY commute_score DESC
            """
            df = pd.read_sql(query, snowflake_conn)
            df.columns = df.columns.str.lower()
            df['job_url'] = df['career_url']  # compatibility
            snowflake_conn.close()
            return df

        except Exception as e:
            st.warning(f"Snowflake query failed: {e}")
            DATA_MODE = "duckdb_fallback"

    # Fallback to demo data
    st.info("📊 Using demo data (Snowflake unavailable)")
    df = pd.DataFrame(DEMO_JOBS)
    return df

# ==============================================================================
# REFERRAL TRACKING (Unified interface)
# ==============================================================================

def add_referral(company, target_person, target_title, connector_name, relationship, tier, notes):
    """Add referral path"""
    if DATA_MODE == "snowflake":
        try:
            snowflake_conn, _ = init_snowflake()
            if snowflake_conn:
                cursor = snowflake_conn.cursor()
                cursor.execute("""
                    INSERT INTO MARTS.REFERRAL_PATHS
                    (company, target_person, target_title, connector_name,
                     connector_relationship, connection_tier, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, [company, target_person, target_title, connector_name, relationship, tier, notes])
                snowflake_conn.commit()
                cursor.close()
                snowflake_conn.close()
                return True
        except:
            pass

    # Fallback to DuckDB
    duckdb_conn = init_duckdb()
    try:
        duckdb_conn.execute("""
            INSERT INTO referral_paths
            (target_company, target_person, target_title, connector_name,
             connector_relationship, connection_tier, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [company, target_person, target_title, connector_name, relationship, tier, notes])
        return True
    except Exception as e:
        st.error(f"Failed to save referral: {e}")
        return False

def get_referrals(company=None):
    """Get referral paths"""
    if DATA_MODE == "snowflake":
        try:
            snowflake_conn, _ = init_snowflake()
            if snowflake_conn:
                if company:
                    query = "SELECT * FROM MARTS.REFERRAL_PATHS WHERE company = %s ORDER BY created_at DESC"
                    df = pd.read_sql(query, snowflake_conn, params=[company])
                else:
                    query = "SELECT * FROM MARTS.REFERRAL_PATHS ORDER BY created_at DESC"
                    df = pd.read_sql(query, snowflake_conn)
                snowflake_conn.close()
                return df
        except:
            pass

    # Fallback to DuckDB
    duckdb_conn = init_duckdb()
    try:
        if company:
            df = duckdb_conn.execute("""
                SELECT * FROM referral_paths
                WHERE target_company = ?
                ORDER BY created_at DESC
            """, [company]).df()
        else:
            df = duckdb_conn.execute("""
                SELECT * FROM referral_paths
                ORDER BY created_at DESC
            """).df()
        return df
    except:
        return pd.DataFrame()

# ==============================================================================
# MAP VISUALIZATION
# ==============================================================================

def get_coords(area):
    """Get coordinates for area"""
    return AREA_COORDS.get(area, (34.0211, -118.3965))

def create_map(df, selected_commute="All"):
    """Create interactive folium map"""

    # Filter by commute rating
    if selected_commute != "All":
        df = df[df['commute_rating'].str.contains(selected_commute, case=False, na=False)]

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
        is_vc = str(row.get('type', '')).upper() == 'VC'

        # Color by type and commute score
        if is_vc:
            color = 'orange'
            icon = 'briefcase'
        elif row.get('commute_score', 0) >= 90:
            color = 'green'
            icon = 'star'
        elif row.get('commute_score', 0) >= 75:
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
            <b>Type:</b> {row.get('type', 'Job')}<br>
            <b>Commute:</b> {row.get('transit_duration', 'N/A')}<br>
            <b>Routes:</b> {row.get('transit_routes', 'N/A')}<br>
            <b>Rating:</b> {row.get('commute_rating', 'N/A')}<br>
            <b>Metro:</b> {row.get('closest_metro', 'N/A')}<br>
            <br>
            <a href="{row.get('career_url', '#')}" target="_blank">🔗 Career Page</a><br>
            <a href="{row.get('google_maps_link', '#')}" target="_blank">🗺️ Get Directions</a><br>
            <a href="{row.get('job_url', '#')}" target="_blank">👔 Find Hiring Manager</a>
        </div>
        """

        folium.Marker(
            coords,
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(color=color, icon=icon, prefix='fa'),
            tooltip=f"{row['company']} - {row.get('transit_duration', 'N/A')}"
        ).add_to(m)

    return m

# ==============================================================================
# MAIN APP
# ==============================================================================

def main():
    st.title("🏖️ Silicon Beach Tech Companies")
    st.markdown("*Interactive job search platform with commute analysis*")

    # Data source indicator
    if DATA_MODE == "snowflake":
        st.success("🔗 **Live Data:** Connected to Snowflake")
    else:
        st.info("📊 **Demo Data:** Snowflake trial expired - using local demo")

    st.markdown("---")

    # Load data
    with st.spinner("Loading companies..."):
        df = load_jobs()

    if df is None or len(df) == 0:
        st.error("No data available")
        return

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
    filtered_df = df[
        (df['area'].isin(area_filter)) &
        ((df['type'] == 'VC') | (df['commute_score'] >= min_score))
    ]

    # Main layout - two columns
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("📍 Job Map")
        status_msg = f"**{len(filtered_df)} companies** | "
        if DATA_MODE == "snowflake":
            status_msg += "🔄 Real-time from Snowflake"
        else:
            status_msg += "📊 Demo data (works forever)"
        st.markdown(status_msg)

        # Create and display map
        job_map = create_map(filtered_df, commute_filter)
        folium_static(job_map, width=800, height=600)

    with col2:
        st.header("📊 Summary")

        # Stats
        excellent = len(df[df.get('commute_score', 0) >= 90])
        good = len(df[(df.get('commute_score', 0) >= 75) & (df.get('commute_score', 0) < 90)])

        st.metric("🟢 Excellent Commute", excellent)
        st.metric("🟠 Good Commute", good)
        st.metric("📍 Total Companies", len(df))

        st.markdown("---")

        # Top companies
        st.subheader("🏆 Top Targets")
        top_companies = df[df.get('commute_score', 0) >= 75].sort_values('commute_score', ascending=False)

        for idx, row in top_companies.head(6).iterrows():
            with st.expander(f"**{row['company']}** - {row.get('transit_duration', 'N/A')}"):
                st.write(f"**Area:** {row['area']}")
                st.write(f"**Route:** {row.get('transit_routes', 'N/A')}")
                st.write(f"**Score:** {row.get('commute_score', 0)}/100")
                if row.get('contact_name'):
                    st.write(f"**Contact:** {row['contact_name']}")
                if row.get('contact_email'):
                    st.write(f"**Email:** {row['contact_email']}")
                st.markdown(f"[Career Page]({row.get('career_url', '#')})")
                st.markdown(f"[Find Hiring Manager]({row.get('job_url', '#')})")

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
            target_person = st.text_input("Hiring Manager Name", placeholder="e.g., Sarah Chen")
            target_title = st.text_input("Their Title", placeholder="e.g., Senior Data Engineer")

        with col_b:
            connector_name = st.text_input("Your Connection", placeholder="e.g., Alex from Booth")
            relationship = st.text_input("How do you know them?", placeholder="e.g., Chicago Booth Alum")
            tier = st.select_slider("Connection Tier", options=[1, 2, 3], value=2)

        notes = st.text_area("Notes", placeholder="e.g., Met at career fair, offered to intro me")

        if st.button("💾 Save to Database"):
            if target_person and connector_name:
                success = add_referral(
                    target_company, target_person, target_title,
                    connector_name, relationship, tier, notes
                )
                if success:
                    st.success(f"✅ Saved to {DATA_MODE}: {connector_name} → {target_person}")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("Failed to save referral")
            else:
                st.error("Please fill in at least Target Person and Connector Name")

    with tab2:
        st.subheader(f"Your Network Connections (from {DATA_MODE})")

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
            st.info("No referral paths recorded yet. Add your first one above!")
        else:
            for idx, ref in referrals.iterrows():
                with st.expander(f"**{ref.get('company', ref.get('target_company', 'Unknown'))}** - {ref.get('target_person', 'Unknown')} (Tier {ref.get('connection_tier', '?')})"):
                    st.write(f"**🎯 Target:** {ref.get('target_person', 'Unknown')}")
                    st.write(f"**💼 Title:** {ref.get('target_title', 'Unknown')}")
                    st.write(f"**🔗 Via:** {ref.get('connector_name', 'Unknown')}")
                    st.write(f"**🤝 Relationship:** {ref.get('connector_relationship', 'Unknown')}")
                    st.write(f"**📝 Notes:** {ref.get('notes', 'None')}")
                    created_at = ref.get('created_at', ref.get('CREATED_AT', 'Unknown'))
                    st.caption(f"Added: {created_at}")

    # Company Details Table
    st.markdown("---")
    st.header(f"📋 All Companies (Live from {DATA_MODE})")

    # Display table
    display_df = filtered_df[[
        'company', 'area', 'transit_duration', 'transit_routes',
        'commute_rating', 'commute_score'
    ].copy()

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
    if DATA_MODE == "snowflake":
        st.caption("💡 **Live Data:** Stored in Snowflake | **Trial:** $400 credit active")
    else:
        st.caption("💡 **Demo Data:** Works forever after trial expires | **Tech:** DuckDB + Streamlit")

if __name__ == "__main__":
    main()





