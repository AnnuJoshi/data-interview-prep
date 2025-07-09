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
> It simply means **“no value / unknown.”** \
> The comparison of NULL with a value will always result in NULL. Additionally, NULL is not equal to NULL.

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
</details>


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
- DATE_TRUNC vs EXTRACT - The use of the EXTRACT function in the WHERE clause has the potential to cause severe issues with performance on larger tables.
</details>

<details> 
<summary>2. DATE_PART </summary>
</details> 

<details> 
<summary>3. EXTRACT </summary>
 EXTRACT(MONTH FROM customers.signup_timestamp) = 6
 
 - EXTRACT(EPOCH FROM timestamp), it converts the given timestamp into the number of seconds since the Unix epoch, which is defined as January 1, 1970, 00:00:00 UTC. So, it’s essentially giving you a single numeric value representing how many seconds have passed from that starting point up to the timestamp you provide.
 - EXTRACT(EPOCH FROM (delivered_to_consumer_datetime - customer_placed_order_datetime)), you’re first subtracting two timestamps, which results in an interval (a duration of time). Then, EXTRACT(EPOCH FROM ...) converts that interval into the total number of seconds in that duration.
 - Extract minute from Interval 
 EXTRACT(MINUTE FROM (delivered_to_consumer_datetime - customer_placed_order_datetime))


</details> 

<details> 
<summary>4. DATE </summary>
 EXTRACT(MONTH FROM customers.signup_timestamp) = 6
</details>

<details> 
<summary>5. Interval </summary>

**Conceptually** An interval is a span of time, not a point in time.\
Native INTERVAL type that internally keeps
    • months,\
    • days,\
    • microseconds.\
    • Literals:

    interval '2 hours 30 minutes'
    interval '3 days'
    interval '1 year -4 months

    INTERVAL '45 minutes' is a literal interval value in PostgreSQL, which you can use for comparison.

    To ease any doubts, let’s think about how PostgreSQL handles this internally. The database normalizes intervals for comparison, so whether the actual time difference comes out as '30 minutes' or '1800 seconds', it will accurately evaluate against '45 minutes'. For example, if a delivery took 40 minutes, the interval comparison will return true for <= INTERVAL '45 minutes'.
    It’s very reliable and doesn’t require manual conversion to seconds or minutes.
    
    It’s flexible with the syntax and understands 'minute' or 'minutes', 'hour' or 'hours', etc. So, no issue there.

```sql

-- duration between two events
SELECT delivery_end - delivery_start AS trip_interval

-- average trip length in minutes
SELECT AVG(EXTRACT(epoch FROM (delivery_end - delivery_start)) / 60) AS avg_minutes
FROM deliveries;

-- add 90 minutes to all start times
UPDATE events
SET starts_at = starts_at + interval '90 minutes';

-- Understanding default interval values in postgres 
-- NO default defined ; decided based on input 
SELECT INTERVAL '1';  -- Output: 1 day
SELECT INTERVAL '1:30';  -- Output: 01:30:00 (1 hour 30 minutes)

-- epoch - which returns total seconds as a numeric value)
SELECT EXTRACT(epoch FROM INTERVAL '1 hour');  -- Output: 3600 (seconds)
SELECT EXTRACT(hour FROM INTERVAL '1 day 2 hours');  -- Output: 2 (just the hour part)

```

Quick mnemonic:\
• TIMESTAMP / DATETIME → “When?”\
• INTERVAL → “How long?”
</details>

<details>
<summary> 6. Explain what an index is and the various types of indexes?
</summary>
</details>


<details>
<summary> 7.You can replicate LAG/LEAD window functions with a self-join
https://blog.dataengineer.io/p/how-to-pass-data-engineering-sql
</summary>
</details>

<details>
<summary> 8. Ntile </summary>

 - NTILE groups values into a passed-in number of groups, as evenly as possible. 
 - It distributes rows into the specified number of buckets (100 in this case) as evenly as possible. If the number of restaurants(rows) isn’t perfectly divisible by 100, some buckets might have one more row than others, but it’ll still approximate the bottom 2% pretty well by taking buckets 1 and 2. For example, if you have 1000 restaurants, buckets 1 and 2 would cover roughly 20 restaurants (bottom 2%), which is what we want.

</details>

<details>
<summary> 9. TO_CHAR </summary>

- Purpose: Converts values (dates, timestamps, numbers) into formatted strings.
- Syntax: `TO_CHAR(value, format_mask)` <br>
  - `value`: Data to format (date, number, etc.).<br>
  - `format_mask`: String defining output format using specific codes.


### Use Cases

#### 1. Dates and Timestamps
- Formats dates/timestamps for readable output.
- **Example**: Turn `2023-05-15 14:30:00` into `15-May-2023`.
  - Query: `SELECT TO_CHAR(created_at, 'DD-Mon-YYYY') AS formatted_date FROM your_table;`
  - Format Codes: `DD` (day 01-31), `Mon` (abbreviated month), `YYYY` (4-digit year).
  - `TO_CHAR(trans_date, 'YYYY-MM')`
- Other Codes: `HH24` (hours 00-23), `MI` (minutes), `AM` (a.m./p.m.).

#### 2. Numbers
- Formats numbers for currency, decimals, or padding.
- **Example**: Turn `1234.567` into `$1,234.57`.
  - Query: `SELECT TO_CHAR(price, 'FM$9,999.99') AS formatted_price FROM products;`
  - Format Codes: `FM` (no extra spaces), `$` (literal), `9` (digit or space), `,` (thousands separator), `.` (decimal).

- **Example**: 
`trim(to_char(sum(bks.slots)/2.0, '99999D9999'))as "Total Hours"`
  - 9 represents a digit position. If no digit in that position, it will be filled with a space (not a zero).
  - D represents the decimal point. In PostgreSQL, D is used to indicate where the decimal separator (usually a dot .) should appear in the formatted output.
  - So, '99999D9999' means the number will be formatted with up to 5 digits before the decimal point and up to 4 digits after it


## Key Points
- **Output**: Always returns a text string (no math or comparisons on result).
- **Errors**: Mismatched format mask and data type will cause errors.
- **Tip**: Keep original value for calculations; use `TO_CHAR` for display only.

## Quick Tip for Interview
- Mention use for formatting dates or currency in reports.
- Highlight flexibility with custom format masks.
</details>

<details>
<summary> 10.Aggregation Function </summary>

```sql
-- ARRAY_AGG (first_name || ' ' || last_name) actors 
-- string_agg(expression, separator, order by)
-- The AVG() function ignores NULL in the calculation.
-- SUM() function ignores NULL
-- COUNT(*) function returns the number of rows returned by a  SELECT statement including NULL and duplicates
-- COUNT(column_name)
-- COUNT, SUM, AVG CAN BE USED IN HAVING 
-- MAX and MAX CAN BE USED WITH WHERE AND HAVING - ignores NULL values in the computation.

-- COUNT(*) simply returns the number of rows
-- COUNT(address) counts the number of non-null addresses in the result set.
-- COUNT(DISTINCT address) counts the number of different addresses in the facilities table.
```

</details>

<details>
<summary> 11. Concat </summary>

- concat in sql using pipe 
- concat()
- mems.firstname || ' ' || mems.surname as member
</details>



<details>
<summary> 12. General Postgres Facts </summary>

- Postgres doesn't support putting column names in the HAVING clause.
- STRING functions in SQL are based on 1-indexing
- WINDOW Function always performs the calculation on the result set after the JOIN, WHERE, GROUP BY and HAVING clause and before the final ORDER BY. 
- [Window functions operate on the result set of your (sub-)query after the WHERE clause and all standard aggregation.](
https://pgexercises.com/questions/aggregates/countmembers.html)

The ORDER BY changes the window again. 
- [CORRELATED SUBQUERIES](https://neon.tech/postgresql/postgresql-tutorial/postgresql-correlated-subquery)
  - A CORRELATED SUBQUERY is a subquery that uses values from the outer query. This means that it gets executed once for each result row in the outer query

- NOT EXISTS typically performs better for large datasets
  - checks the existence of rows in a subquery
  - [if the subquery returns NULL, the EXISTS operator returns true](https://neon.tech/postgresql/postgresql-tutorial/postgresql-exists)
  - Only executes subquery long enough to determine if at least one row exists
  - Doesn't need to retrieve the complete subquery result set

- EXCEPT version is more readable but might be less efficient
- Both avoid the potential NULL issues that can occur with NOT IN
-  correlation conditions should be in where not join 
- EXCEPT removes duplicates - NOT EXISTS keeps them unless EXCEPT ALL
- EXCEPT Requires sorting/hashing of both result sets
- EXCEPT Performs full comparison between sets
- Takes two result sets with compatible schemas
- EXCEPT Treats NULLs as equal values

- SELECT 1 is more efficient in subqueries as compared to select * or select column name as No actual data needs to be returned.
</details>

<details>
<summary> 13. ROLLUP and CUBE </summary>

## aggregations in SQL 
# Roll up ROLLUP produces a hierarchy of aggregations in the order passed into it
# ROLLUP and CUBE are special cases of GROUPING SETS. GROUPING SETS allow you to specify the exact aggregation permutations you want: you could, for example, ask for just (facid, month) and (facid), skipping the top-level aggregation.
</details>

<details>
<summary> 14.  </summary>


</details>

