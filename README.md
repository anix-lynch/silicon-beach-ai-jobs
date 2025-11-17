# 🏖️ Silicon Beach Job Search Platform

**Interactive job search platform with real-time commute analysis and network tracking**

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://share.streamlit.io/)
[![Snowflake](https://img.shields.io/badge/Snowflake-35B5E5?style=for-the-badge&logo=snowflake&logoColor=white)](https://snowflake.com/)
[![DuckDB](https://img.shields.io/badge/DuckDB-FFF000?style=for-the-badge&logo=duckdb&logoColor=black)](https://duckdb.org/)

## 🎯 What This Does

Find tech jobs in Los Angeles' Silicon Beach area with intelligent commute analysis. The platform automatically:

- **Maps job locations** with interactive Folium maps
- **Analyzes commute times** using Google Maps API
- **Tracks referral networks** for warm introductions
- **Ranks opportunities** by commute efficiency
- **Works forever** - graceful degradation when Snowflake trial expires

## 🚀 Live Demos

| Platform | URL | Status |
|----------|-----|--------|
| **GitHub** | [View Code](https://github.com/) | ✅ Deployed |
| **Streamlit Cloud** | [Live App](https://share.streamlit.io/) | ✅ Deployed |
| **Portfolio** | [gozeroshot.dev](https://gozeroshot.dev) | ✅ Deployed |

## 🏗️ Architecture

```
Streamlit Frontend
        ↓
Snowflake Backend (Primary - $400 trial)
DuckDB Backend (Fallback - Forever free)
        ↓
Google Maps API (Commute Analysis)
Folium Maps (Interactive Visualization)
```

## 📊 Key Features

### 🗺️ Interactive Job Map
- **5-mile radius** job search from Culver City
- **Real-time commute analysis** via Google Maps
- **Color-coded ratings**: 🟢 Excellent (<40min) 🟠 Good 🟡 Acceptable
- **Interactive popups** with career pages and directions

### 🔗 Network Tracker
- **Referral path management** for warm introductions
- **Connection tiering** (1st, 2nd, 3rd degree)
- **Company-specific filtering**
- **Persistent storage** in Snowflake/DuckDB

### 📈 Analytics Dashboard
- **Commute score calculations** (0-100 scale)
- **Area-wise breakdowns**
- **Top opportunity rankings**
- **Real-time data sync**

## 💻 Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | Streamlit | Interactive web app |
| **Database** | Snowflake | Production data warehouse ($400 credit) |
| **Fallback** | DuckDB | Local analytics (free forever) |
| **Maps** | Folium + Google Maps API | Interactive mapping & routing |
| **Deployment** | Streamlit Cloud + GitHub | Multi-platform hosting |

## 🛠️ Quick Start

### Prerequisites
- Python 3.8+
- Internet connection for Google Maps API

### Local Development

```bash
# Clone repository
git clone <your-repo-url>
cd silicon-beach-jobs

# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run main.py
```

### Data Sources

The app automatically detects available data sources:

1. **Snowflake (Primary)**: Real-time job data, network tracking
2. **DuckDB (Fallback)**: Demo data when Snowflake trial expires
3. **Demo Data**: Built-in sample data (always works)

## 📈 Data Pipeline

```
Job Scrapers → Raw Data → Snowflake Staging → Analytics → Streamlit UI
     ↓              ↓              ↓              ↓
  Firecrawl     Data Cleaning   MARTS Views   Interactive Maps
  Browserbase   Quality Checks  KPIs         Network Tracker
```

## 🎨 User Experience

### Job Seeker Workflow
1. **View Interactive Map** - See all opportunities geographically
2. **Filter by Commute** - Focus on excellent/good commutes
3. **Explore Opportunities** - Click markers for details
4. **Track Referrals** - Record warm introduction paths
5. **Apply Strategically** - Use network for competitive advantage

### Recruiter Features
- **Location Intelligence** - Understand candidate commute preferences
- **Network Mapping** - Visualize referral ecosystems
- **Analytics Dashboard** - Track hiring funnel metrics

## 🔧 Configuration

### Environment Variables
```bash
# Google Maps API (required)
GOOGLE_MAPS_API_KEY=your_api_key_here

# Data Mode (optional)
DATA_MODE=snowflake  # or 'duckdb' for local mode
```

### Snowflake Setup (Optional)
If you have Snowflake access, configure:
```python
SNOWFLAKE_CONFIG = {
    'account': 'your-account',
    'user': 'your-user',
    'password': 'your-password',
    'database': 'JOB_SEARCH',
    'warehouse': 'COMPUTE_WH',
}
```

## 🚀 Deployment

### Multi-Platform Deployment (Distro Dojo)

The app is designed for **3-platform deployment**:

1. **GitHub** - Code repository and credibility
2. **Streamlit Cloud** - Live interactive demo
3. **Portfolio Site** - Professional showcase

### Deployment Commands

```bash
# 1. GitHub (Code)
git init && git add .
git commit -m "Initial Silicon Beach Jobs platform"
git remote add origin git@github.com:USERNAME/PROJECT.git
git push -u origin main

# 2. Streamlit Cloud (Demo)
# Visit: https://share.streamlit.io/
# Connect GitHub repo → auto-deploys

# 3. Portfolio (Showcase)
# Update gozeroshot.dev projects array
```

## 📊 Performance & Costs

### Current Usage ($400 Snowflake Trial)
- **Storage**: ~50MB data
- **Compute**: ~10-20 credits/day for queries
- **API Calls**: ~100/day Google Maps requests
- **Remaining**: ~$350+ credit available

### Forever-Free Mode (After Trial)
- **Storage**: Local DuckDB (no cloud costs)
- **Compute**: Local processing
- **API**: Google Maps (free tier available)
- **Deployment**: Streamlit Cloud free tier

## 🎯 Use Cases

### For Job Seekers
- **Tech roles** in LA Silicon Beach
- **Commute optimization** (avoid traffic)
- **Network leverage** (warm introductions)
- **Competitive advantage** (data-driven applications)

### For Recruiters
- **Location intelligence** for candidate targeting
- **Referral network analysis**
- **Hiring funnel optimization**
- **Market intelligence** on LA tech scene

### For Students/Learners
- **Full-stack data app** example
- **Real-world API integration**
- **Cloud database patterns**
- **Interactive visualization techniques**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

MIT License - feel free to use for learning and job search!

## 🙏 Acknowledgments

- **Snowflake** for $400 trial credit
- **Streamlit** for amazing developer experience
- **Google Maps** for commute intelligence
- **Folium** for interactive mapping

---

**Built with ❤️ in Culver City, California**

*Finding the perfect tech job, one optimized commute at a time.*