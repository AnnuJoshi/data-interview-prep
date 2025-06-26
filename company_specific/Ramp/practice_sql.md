```sql
-- Error while using Range in this - Range only works with unbounded 
-- forgot ::numeric , where to place it , was using ::integer after avg

/* Using this dataset, show the SQL query to find the rolling 3 day average transaction amount for each day in January 2021. */

WITH all_dates AS (
    SELECT generate_series('2021-01-01'::DATE, '2021-01-31'::DATE, '1 day'::INTERVAL)::DATE AS trans_day
),
daily_totals AS (
    SELECT 
        d.trans_day,
        COALESCE(SUM(t.transaction_amount), 0) AS daily_amount
    FROM all_dates d
    LEFT JOIN transactions t
        ON d.trans_day = t.transaction_time::DATE
        AND t.transaction_time >= '2021-01-01'
        AND t.transaction_time < '2021-02-01'
    GROUP BY d.trans_day
)
SELECT 
    trans_day,
    daily_amount,
    ROUND(AVG(daily_amount)  OVER ( ORDER BY trans_day
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    )::numeric ,2) AS rolling_3_day_avg
FROM daily_totals
ORDER BY trans_day;
```