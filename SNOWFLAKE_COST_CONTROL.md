# Snowflake Cost Control Guide

## 🎯 Goal: $0 Out-of-Pocket (Use Free Trial Credits Only)

You have **$400 free trial credits** from Snowflake. Here's how to make them last for your portfolio:

---

## ✅ FREE TIER STRATEGY

### 1. **Use X-SMALL Warehouse** (Cheapest Option)
```sql
-- Set warehouse size to X-SMALL (2 credits/hour = $4/hour)
ALTER WAREHOUSE COMPUTE_WH SET WAREHOUSE_SIZE = 'X-SMALL';

-- Enable auto-suspend after 1 minute of inactivity
ALTER WAREHOUSE COMPUTE_WH SET AUTO_SUSPEND = 60;

-- Enable auto-resume
ALTER WAREHOUSE COMPUTE_WH SET AUTO_RESUME = TRUE;
```

### 2. **Suspend Warehouse When Not in Use**
```sql
-- Manual suspend (do this when done working)
ALTER WAREHOUSE COMPUTE_WH SUSPEND;

-- Check warehouse status
SHOW WAREHOUSES LIKE 'COMPUTE_WH';
```

### 3. **Cortex AI Costs** (Very Cheap)
- **Cortex Complete**: ~$0.002 per 1K tokens
- **Cortex Embed**: ~$0.0001 per 1K tokens
- **For portfolio demo**: ~$0.10 total for 1000 queries

---

## 💰 COST BREAKDOWN (X-SMALL Warehouse)

| Activity | Cost per Hour | Free Trial Usage |
|----------|---------------|------------------|
| **X-SMALL Warehouse** | $4/hour | 100 hours on $400 credit |
| **Cortex AI queries** | $0.002/1K tokens | ~200K queries on $400 credit |
| **Storage** | $23/TB/month | FREE for < 1GB |

---

## 🚨 COST ALERTS (Set These Up!)

### In Snowflake UI:
1. Go to **Admin** → **Cost Management** → **Budgets**
2. Create budget:
   - **Name**: `Portfolio Demo Budget`
   - **Amount**: `$50` (or whatever threshold you want)
   - **Email Alert**: When 80% used

### SQL Alert (Optional):
```sql
-- Create resource monitor to auto-suspend at $50
CREATE RESOURCE MONITOR portfolio_budget WITH 
  CREDIT_QUOTA = 25  -- $50 at $2/credit
  TRIGGERS
    ON 80 PERCENT DO NOTIFY
    ON 100 PERCENT DO SUSPEND;

-- Assign to warehouse
ALTER WAREHOUSE COMPUTE_WH SET RESOURCE_MONITOR = portfolio_budget;
```

---

## 🎯 PORTFOLIO USAGE ESTIMATE

**For Streamlit demo + recruiter testing:**
- **Development**: 10 hours × $4 = $40
- **Demo runs**: 50 runs × 1 min × $0.067 = $3.35
- **Cortex AI queries**: 1000 queries × $0.002 = $2
- **Storage**: < 1GB = $0
- **TOTAL**: ~$45 (leaves $355 credit for safety)

---

## ⚡ OPTIMIZATION TIPS

### 1. **Query Result Caching**
```sql
-- Enable result caching (free repeated queries)
ALTER ACCOUNT SET USE_CACHED_RESULT = TRUE;
```

### 2. **Limit Query Rows**
```python
# In your Streamlit app, always limit results
df = session.sql("SELECT * FROM jobs LIMIT 100").to_pandas()
```

### 3. **Batch Cortex Queries**
```python
# Instead of 100 separate Cortex calls, batch them
queries = ["query1", "query2", ...]
results = session.sql(f"""
    SELECT 
        SNOWFLAKE.CORTEX.COMPLETE('mistral-7b', query)
    FROM (VALUES {', '.join([f"('{q}')" for q in queries])}) AS t(query)
""").collect()
```

---

## 📊 MONITORING YOUR SPEND

### Check Credit Usage:
```sql
-- See warehouse credit usage
SELECT 
    WAREHOUSE_NAME,
    START_TIME,
    END_TIME,
    CREDITS_USED
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE START_TIME >= DATEADD(day, -7, CURRENT_TIMESTAMP())
ORDER BY START_TIME DESC;

-- See total credits remaining
SHOW ORGANIZATION ACCOUNTS;
```

### Check Cortex AI Usage:
```sql
-- Monitor Cortex query costs
SELECT 
    DATE_TRUNC('day', START_TIME) as day,
    COUNT(*) as query_count,
    SUM(CREDITS_USED) as credits
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE QUERY_TEXT LIKE '%CORTEX%'
GROUP BY day
ORDER BY day DESC;
```

---

## 🛡️ SAFETY CHECKLIST

Before deploying to Streamlit Cloud:

- [ ] Warehouse set to X-SMALL
- [ ] Auto-suspend set to 60 seconds
- [ ] Resource monitor created with $50 limit
- [ ] Cost alert email configured
- [ ] Query limits in app (LIMIT 100)
- [ ] Result caching enabled
- [ ] Password in environment variables (not hardcoded)

---

## 🎓 WHAT TO TELL RECRUITERS

**"Free Tier Portfolio Demo"**
> "This project uses Snowflake's $400 free trial credits. I've optimized costs with X-SMALL warehouse, auto-suspend, query caching, and resource monitors. Total cost for portfolio demo: < $50, leaving $350 credit buffer. Production-ready cost optimization strategies implemented."

**ATS Keywords:**
- Snowflake Cost Optimization
- Resource Monitoring
- Credit Management
- Warehouse Scaling
- Query Performance Tuning
- Budget Alerts

---

## 📞 IF YOU GO OVER BUDGET

1. **Immediate Actions:**
   ```sql
   ALTER WAREHOUSE COMPUTE_WH SUSPEND;
   ```

2. **Contact Snowflake Support:**
   - Email: support@snowflake.com
   - Mention it's a portfolio/learning project
   - They often extend trial credits for students/job seekers

3. **Fallback:**
   - Switch to DuckDB version (`app_duckdb.py`) - 100% free
   - Keep Snowflake as "proof of experience"

---

**Last Updated**: 2025-11-17  
**Status**: ✅ Cost-Optimized for Free Trial


