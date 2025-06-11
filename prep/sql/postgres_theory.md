| Task               | Snippet                              |
|--------------------|--------------------------------------|
| Last n days        | WHERE ts >= CURRENT_DATE - INTERVAL '30 days'|
| First day of month | DATE_TRUNC('month', ts)              |
| Last day of month  | (ts + INTERVAL '1 month')::date - 1  |
| Age in days        | (CURRENT_DATE - ts::date);  -- integer days|
| 7-day rolling      | RANGE BETWEEN INTERVAL '6 days' PRECEDING AND CURRENT ROW |
| Row number reset per group | row_number() OVER (PARTITION BY grp ORDER BY id)|	
|Running total	     |sum(val) OVER (ORDER BY ts)|
|Gap detection	     |lag(ts) OVER w then ts - lag_ts > '1 hour'|
|Percent of total	 |100.0 * val / sum(val) OVER ()|
|Integer vs Numeric Division| SELECT 1 / 3; -- returns int( wrong) <br> SELECT 1.0 / 3; -- yields 0.3333 <br> SELECT 1::NUMERIC / 3; -- explicit cast 


#### Generating Series / Calendar Tables
```sql
SELECT d::date AS day
FROM generate_series('2025-01-01', '2025-12-31', INTERVAL '1 day') AS d;
```

<details>
<summary> What is Null in SQL </summary>

> **NULL ≠ 0 ≠ empty string ("") ≠ 'NULL'**  
> It simply means **“no value / unknown.”**

### 1. SQL has Three-Valued Logic

| Expression        | Result    |
|-------------------|-----------|
| 5 = 5             | `TRUE`    |
| 5 = 7             | `FALSE`   |
| 5 = NULL          | `UNKNOWN` |
| NULL = NULL       | `UNKNOWN` |

`WHERE` filters out rows that evaluate to `FALSE` **or** `UNKNOWN`.

### 2. Testing for NULL
```sql
-- Correct
col IS NULL
col IS NOT NULL

COUNT(*)      -- counts ALL rows
COUNT(col)    -- skips NULLs
SUM / AVG     -- skip NULL values

Inner join: NULL in join key never matches.
Outer join: produces NULLs on the “missing” side.

ORDER BY col            -- engine default (NULL first/last)
ORDER BY col NULLS LAST -- explicit control
```

| Function                | Purpose                              | Example                              |
|-------------------------|--------------------------------------|--------------------------------------|
| COALESCE(a, b, …)       | First non-NULL value                | COALESCE(phone, mobile, 'N/A')     |
| ISNULL(a, b)  (not in postgress only in MySQL)  | Same as above                        | ISNULL(bonus, 0)                   |
| IFNULL(a, b)  (not in postgress only in MySQL)  | Same as above                        | IFNULL(bonus, 0)                  |
| NULLIF(a, b)         | Return NULL if `a = b`; otherwise `a`| NULLIF(col1, col2)                |






### Top Gotchas to Verbally Call Out

- “I’m casting to NUMERIC so integer division doesn’t bite us.”
- “Filtering in HAVING because it depends on the aggregate.”
- “Using IS DISTINCT FROM for NULL-safe diff.”
- “Index can’t be used if we wrap the column in a function—so I rewrote the predicate.”
- “Window frame defaults to RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW; I override to 6-day range so it’s calendar-correct.”


### Read up if you need 
<details> 
<summary>1. DATE_TRUNC </summary>
**Output** - The returned value is a TIMESTAMP (or TIMESTAMPTZ if the input is), not a string or partial date.
    
**Use** - used to truncate a timestamp or date to a specified level of precision. 

If, you're using 'month' as the precision level, it will truncate the date or timestamp to the first day of the month, removing the day, hour, minute, second, and any fractional seconds from the value.

It keeps the year and month intact but sets the day to 01 and the time components to midnight (00:00:00).
```sql
DATE_TRUNC('month', t.Order_Date_Time)  --2023-08-15 14:30:00 returns 2023-08-01 00:00:00
DATE_TRUNC('month', t.Order_Date_Time) = '2023-08-01'::date
``` 
- Be mindful of timezone settings if Order_Date_Time includes timezone info (TIMESTAMPTZ), as DATE_TRUNC respects the timezone.
- Sometimes prevent the use of an index on Order_Date_Time unless you have a functional index on DATE_TRUNC('month', Order_Date_Time)
- Consider alternative range queries like Order_Date_Time >= '2023-08-01' AND Order_Date_Time < '2023-09-01', which are often more index-friendly.