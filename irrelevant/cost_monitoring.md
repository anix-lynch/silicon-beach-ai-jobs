# 🏖️ Cost Monitoring Commands for Snowflake Trial

## Check Current Credit Usage (Run in Snowflake SQL Worksheet)

```sql
-- CURRENT CREDIT BALANCE ( trial)
SELECT 
  SUM(CREDITS_USED) * 2 AS total_cost_usd,
  400 - (SUM(CREDITS_USED) * 2) AS remaining_credit_usd,
  ROUND((SUM(CREDITS_USED) * 2) / 400 * 100, 2) AS percent_used
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE START_TIME >= DATEADD(day, -30, CURRENT_TIMESTAMP());

-- TODAY'S USAGE
SELECT 
  SUM(CREDITS_USED) * 2 AS today_cost_usd
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE START_TIME >= DATEADD(day, 0, CURRENT_DATE);

-- REAL-TIME MONITORING (last hour)
SELECT 
  SUM(CREDITS_USED) * 2 AS last_hour_cost_usd
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE START_TIME >= DATEADD(hour, -1, CURRENT_TIMESTAMP());
```

## Cost Control Commands

```sql
-- IMMEDIATE COST CONTROL
ALTER WAREHOUSE COMPUTE_WH SUSPEND;  -- Stop spending NOW

-- PERMANENT COST PROTECTION
ALTER WAREHOUSE COMPUTE_WH SET WAREHOUSE_SIZE = 'X-SMALL';  -- /hour max
ALTER WAREHOUSE COMPUTE_WH SET AUTO_SUSPEND = 60;           -- Suspend after 60s idle
ALTER WAREHOUSE COMPUTE_WH SET AUTO_RESUME = TRUE;          -- Resume when needed

-- CHECK WAREHOUSE STATUS
SHOW WAREHOUSES;
```

## Cost Limits (Account Level)

Unfortunately, Snowflake doesn't have built-in spending caps in the free trial.
You'll need to monitor manually and suspend when approaching limits.

## Our Speedrun Budget: < Target
- SQL Setup: -5
- App Testing: -7  
- Recording: -3
- TOTAL: < (safe within  trial)

Monitor with the queries above!
