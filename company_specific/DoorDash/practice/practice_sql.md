<details>
<summary> Mock 1 </summary>

Schema 

`restaurants`       (restaurant_id PK, name, city, signup_date)\
`orders`            (order_id PK, restaurant_id FK, customer_id FK,
                   placed_at TIMESTAMP, status VARCHAR,
                   subtotal_cents INT, delivery_fee_cents INT,
                   courier_id FK, cancelled_at TIMESTAMP NULL)\
`order_items`       (order_id FK, item_id FK, quantity INT, price_cents INT)\
`couriers`          (courier_id PK, name)\
`customers`         (customer_id PK, name, city, signup_date)\

Statuses are ‘PLACED’, ‘DELIVERED’, ‘CANCELLED’.
Assume data spans multiple years and CURRENT_DATE is 2025-06-11.

### SQL Practice (4 Qs)
Suggested timing: 6–8 min each\
Recommended features: DATE_TRUNC, INTERVAL arithmetic, JOINs, conditional aggregation, window functions, CTEs.

#### A-1 Year-over-Year January Order Declines (Easy)
Return restaurant_id, this_year_orders, last_year_orders, percent_change for every restaurant whose January order count this year < January order count last year.

Requirements

Compare January 2025 vs January 2024.
Percent change = (this_year − last_year) / last_year.
Order by percent_change ASC (biggest drop first).

```sql
-- Select  '2022-09-01'::date -- will cast as date 
-- Select  '2022-09-01' not sure
-- Select  DATE '2022-09-01' -- will cast as date 

WITH jan24 AS (
    SELECT restaurant_id, COUNT(*) AS last_year
    FROM orders
    WHERE placed_at >= DATE '2024-01-01'
      AND placed_at  < DATE '2024-02-01'
    GROUP BY restaurant_id
),
jan25 AS (
    SELECT restaurant_id, COUNT(*) AS this_year
    FROM orders
    WHERE placed_at >= DATE '2025-01-01'
      AND placed_at  < DATE '2025-02-01'
    GROUP BY restaurant_id
)
SELECT j25.restaurant_id,
       j25.this_year,
       j24.last_year,
       ROUND( (j25.this_year - j24.last_year)::NUMERIC / j24.last_year, 4) AS percent_change
FROM jan25 j25
JOIN jan24 j24 USING (restaurant_id)
WHERE j25.this_year < j24.last_year
ORDER BY percent_change ASC;


--- optimized solution with just one scan of the table 

SELECT 
    restaurant_id,
    COUNT(CASE WHEN placed_at >= DATE '2025-01-01' AND placed_at < DATE '2025-02-01' THEN 1 END) AS this_year,
    COUNT(CASE WHEN placed_at >= DATE '2024-01-01' AND placed_at < DATE '2024-02-01' THEN 1 END) AS last_year,
    ROUND(
        (COUNT(CASE WHEN placed_at >= DATE '2025-01-01' AND placed_at < DATE '2025-02-01' THEN 1 END) - 
         COUNT(CASE WHEN placed_at >= DATE '2024-01-01' AND placed_at < DATE '2024-02-01' THEN 1 END))::NUMERIC /
         COUNT(CASE WHEN placed_at >= DATE '2024-01-01' AND placed_at < DATE '2024-02-01' THEN 1 END), 
        4
    ) AS percent_change
FROM orders
WHERE placed_at >= DATE '2024-01-01' AND placed_at < DATE '2025-02-01'
GROUP BY restaurant_id
HAVING COUNT(CASE WHEN placed_at >= DATE '2025-01-01' AND placed_at < DATE '2025-02-01' THEN 1 END) <
       COUNT(CASE WHEN placed_at >= DATE '2024-01-01' AND placed_at < DATE '2024-02-01' THEN 1 END)
ORDER BY percent_change ASC;
```

#### A-2 30-Day Cancellation Rate per Restaurant (Easy/Medium)
For each restaurant that had ≥ 30 total orders in the past 30 days (relative to CURRENT_DATE), output:\
restaurant_id | total_orders | cancelled_orders | cancel_pct\
Cancel % = cancelled_orders / total_orders, rounded to 2 decimal places.\
Order by cancel_pct DESC, break ties by total_orders DESC.\
Hint: status = 'CANCELLED' OR cancelled_at IS NOT NULL.\

```sql
-- Alternate code 
-- SUM(CASE WHEN status = 'CANCELLED' OR cancelled_at IS NOT NULL THEN 1 ELSE 0 END) AS cancelled_orders
-- FILTER is Postgres specific, but same performance

WITH last_30 AS (
    SELECT restaurant_id,
           COUNT(*) AS total_orders,
           COUNT(*) FILTER (
               WHERE status='CANCELLED' OR cancelled_at IS NOT NULL
           )  AS cancelled_orders
    FROM orders
    WHERE placed_at >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY restaurant_id
    HAVING COUNT(*) >= 30
)
SELECT restaurant_id,
       total_orders,
       cancelled_orders,
       ROUND(cancelled_orders::NUMERIC / total_orders, 2) AS cancel_pct
FROM last_30
ORDER BY cancel_pct DESC, total_orders DESC;

-- can do in one query, if don't need cte for readability or reuse
SELECT 
    restaurant_id,
    COUNT(*) AS total_orders,
    COUNT(*) FILTER (WHERE status = 'CANCELLED' OR cancelled_at IS NOT NULL) AS cancelled_orders,
    ROUND((COUNT(*) FILTER (WHERE status = 'CANCELLED' OR cancelled_at IS NOT NULL))::NUMERIC / COUNT(*), 2) AS cancel_pct
FROM orders
WHERE placed_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY restaurant_id
HAVING COUNT(*) >= 30
ORDER BY cancel_pct DESC, total_orders DESC;
```

#### A-3 7-Day Rolling Avg Delivery Fee by City (Medium)

Produce a result set with columns\
window_start (DATE) | city | avg_delivery_fee_cents
for every city and every 7-day window (inclusive) in the past 90 days.\
    • A window starts each day, so windows will overlap.\
    • Use window functions, not self-joins.\
    • Exclude cities with < 100 orders in that 7-day window.\
    • Order by window_start, then city.

```sql 
-- NOTE : You cannot use LAG have to use Range Between 
-- DATE_TRUNC('day', placed_at) achieves the same result as CAST AS DATE by truncating the time to the start of the day

-- 1. compact orders into one row per (city, day)
WITH daily AS (             
    SELECT
        CAST(o.placed_at AS DATE)          AS order_date,
        r.city,
        COUNT(*)                           AS day_orders,
        SUM(o.delivery_fee_cents)          AS day_fee_cents
    FROM   orders       o
    JOIN   restaurants  r ON r.restaurant_id = o.restaurant_id
    -- 90-day horizon + 6 extra days so every window is complete
    WHERE  o.placed_at >= CURRENT_DATE - INTERVAL '96 days'
      AND  (o.status <> 'cancelled' OR o.cancelled_at IS NULL)   -- ignore cancelled orders
    GROUP  BY 1, 2
),
-- 2. 7-day window that starts ON EACH order_date

    -- RANGE Between vs ROW Between
        -- RANGE will include all rows where the order_date falls within the 6 days before the current row’s order_date, up to and including the current row’s date.
        -- USE RANGE if you want the window to strictly cover a 7-day period based on date values, and ROWS if you’re okay with counting 7 rows regardless of the actual dates they represent.

rolling AS (            
    SELECT
        order_date                            AS window_start,
        city,
        /* number of orders in the 7-day span [window_start, window_start+6] */
        SUM(day_orders)    OVER (
            PARTITION BY city
            ORDER BY order_date
            RANGE BETWEEN 6 PRECEDING AND CURRENT ROW
            --RANGE BETWEEN CURRENT ROW AND INTERVAL '6 days' FOLLOWING
        ) AS window_orders,
        /* total delivery fees in that same span */
        SUM(day_fee_cents) OVER (
            PARTITION BY city
            ORDER BY order_date
            RANGE BETWEEN CURRENT ROW AND INTERVAL '6 days' FOLLOWING
        ) AS window_fee_cents
    FROM daily
)
SELECT
    window_start,
    city,
    ROUND(window_fee_cents::NUMERIC / window_orders, 2) AS avg_delivery_fee_cents
FROM   rolling
/* keep only windows whose START lies in the past 90 days
   and for which the trailing 6 days are already in the data set            */
WHERE  window_start BETWEEN CURRENT_DATE - INTERVAL '90 days'
                        AND     CURRENT_DATE - INTERVAL '6 days'
  AND  window_orders >= 100          -- ≥ 100 orders in that 7-day window
ORDER  BY window_start, city;

--BETWEEN operator is indeed inclusive of both the start and end values
```

#### A-4 Likely Churned Customers (Medium)

Find customers who
placed ≥ 3 orders lifetime, and
have no orders in the last 60 days.\
Return: customer_id, lifetime_orders, days_since_last_order
Sort descending by days_since_last_order.

```sql 
with cust_stats AS (
SELECT count(order_id) as lifetime_orders, 
       customer_id, 
       MAX(placed_at)::date as last_order_placed
FROM
orders  
GROUP BY customer_id
)
SELECT customer_id, 
lifetime_orders,
(CURRENT_DATE - last_order_placed::date) AS days_since_last_order
FROM 
cust_stats
where lifetime_orders >= 3
and CURRENT_DATE - INTERVAL '60 days' > last_order_placed 


-- In one query 
SELECT
    customer_id,
    COUNT(*)                                             AS lifetime_orders,
    (CURRENT_DATE - MAX(placed_at)::date)::int           AS days_since_last_order
FROM orders
GROUP BY customer_id
HAVING COUNT(*) >= 3
   AND MAX(placed_at) <= CURRENT_DATE - INTERVAL '60 days'
ORDER BY days_since_last_order DESC;
```
</details>

<details>
<summary> Day 2 Practice </summary>

####  [App Click-through Rate (CTR)](https://datalemur.com/questions/click-through-rate) (6 min)

```sql
-- issue with DATE_TRUNC, its for truncation not part
-- ended up using > <  logic 
-- round bracket 
-- could have used DATE_PART('year', timestamp::DATE) = 2022
SELECT
  app_id,
  ROUND(100.0 *
    SUM(CASE WHEN event_type = 'click' THEN 1 ELSE 0 END) /
    SUM(CASE WHEN event_type = 'impression' THEN 1 ELSE 0 END), 2)  AS ctr_rate
FROM events
WHERE timestamp >= '2022-01-01' 
  AND timestamp < '2023-01-01'
GROUP BY app_id;

```

#### [SQL Question 1: First 14-Day Satisfaction](https://datalemur.com/blog/doordash-sql-interview-questions)(9 min)
Ordered within 14 days of signup and signup in June22, what is their order cancellation rate ?
```sql
WITH june22_users AS (
    SELECT customer_id, signup_timestamp
    FROM customers
    WHERE signup_timestamp >= '2022-06-01'
      AND signup_timestamp <  '2022-07-01'
),
orders_14d AS (
    SELECT o.*,
           CASE
               WHEN status IN ('completed incorrectly', 'never received')
                 OR actual_delivery_timestamp > order_timestamp + INTERVAL '30 minutes' -- missed this constraint
               THEN 1 ELSE 0
           END AS is_bad
    FROM orders o
    JOIN june22_users ju -- inner join works no need for left
      ON o.customer_id = ju.customer_id
     AND o.order_timestamp >= ju.signup_timestamp -- explicit condition 
     AND o.order_timestamp <  ju.signup_timestamp + INTERVAL '14 days' -- less than 
)
SELECT
    ROUND(100.0 * SUM(is_bad)::numeric / COUNT(*), 2) AS bad_experience_pct
FROM orders_14d;


--- Alternate thinking in one cte
--- move all conditions to join 
WITH first14d_orders AS (
    SELECT
        o.order_id,
        /* “Bad” if status tells us so OR delivered after the 30-min SLA */
        (   o.status IN ('completed incorrectly', 'never received')
         OR o.actual_delivery_timestamp
              > o.order_timestamp + INTERVAL '30 minutes'
        ) AS is_bad
    FROM orders   o
    JOIN customers c
      ON c.customer_id = o.customer_id
     /* ① June-2022 sign-ups only */
     AND c.signup_timestamp >= DATE '2022-06-01'
     AND c.signup_timestamp <  DATE '2022-07-01'
     /* ② Order must fall in the customer’s first 14 days */
     AND o.order_timestamp >= c.signup_timestamp
     AND o.order_timestamp <  c.signup_timestamp + INTERVAL '14 days'
)

SELECT
    ROUND(100 * AVG(is_bad::int), 2)  AS bad_experience_pct
FROM first14d_orders;
```

#### [SQL Question 2: : Analyze DoorDash Delivery Performance](https://datalemur.com/blog/doordash-sql-interview-questions)(8 min)

As a Data Analyst at DoorDash, you're tasked to analyze the delivery performance of the drivers. Specifically, you are asked to compute the average delivery duration of each driver for each day, the rank of each driver's daily average delivery duration, and the overall average delivery duration per driver.

Use the deliveries table where each row represents a single delivery. The columns are:
delivery_id: An identifier for the delivery
driver_id: An identifier for the driver
delivery_start_time: Timestamp for the start of the delivery
delivery_end_time: Timestamp for the end of the delivery
```sql 
-- EXTRACT DATE FROM timestamp
-- timestamp_column::date
-- CAST(timestamp_column AS DATE)
WITH daily AS (
    SELECT
        driver_id,
        DATE_TRUNC('day', delivery_start_time) AS delivery_day, -- focus on naming
        AVG(delivery_end_time - delivery_start_time) AS avg_delivery_dur
    FROM deliveries
    WHERE delivery_start_time IS NOT NULL -- checks I missed 
      AND delivery_end_time   IS NOT NULL -- checks I missed
    GROUP BY driver_id, DATE_TRUNC('day', delivery_start_time)
)
SELECT
    driver_id,
    delivery_day,
    avg_delivery_dur,
    RANK() OVER (PARTITION BY delivery_day 
                 ORDER BY avg_delivery_dur ASC)  AS daily_rank, -- did desc pay attention - getting impatient 
    AVG(avg_delivery_dur) OVER (PARTITION BY driver_id) AS overall_avg_delivery_dur -- was not too sure while writing this 
FROM daily
ORDER BY delivery_day, daily_rank; -- missed ordering


--- Tips 
--- Keep in mind the window functions will only work with columns it is involved with like in this `overall_avg_delivery_dur` will only see `avg_delivery_dur` and `driver_id` and for each row for that driver it will put same value.
--- Rank(will skip next rank, leave gaps after ties, skip 1-2-2-4) and Dense Rank (will not skip 1-2-2-3)
```

#### [SQL Question 4: Restaurant Performance Analysis](12 min)

Tip: Jot down a 1-sentence goal (e.g., “Find top 5 restaurants by order count in last 30 days”)

```sql
SELECT 
    restaurant_id,
    tot_orders
FROM (
    SELECT 
        restaurant_id,
        COUNT(order_id) AS tot_orders,
        RANK() OVER (ORDER BY COUNT(order_id) DESC) AS order_rank -- used rank which is a reserved keyword
    FROM orders AS o
    WHERE 
        o.order_date >= CURRENT_DATE - INTERVAL '1 month'
        AND o.order_date < CURRENT_DATE -- missed AND 
    GROUP BY restaurant_id
) ranked_rest
WHERE order_rank <= 5;

```
</details>


<details>
<summary> DAY 3 Practice </summary>

#### [SQL Question 5: Calculating Courier Average Distance and Total Revenue](7 min)
```sql
    -- read question correctly as it is asking for absolute difference
    -- In PostgreSQL, ROUND() works with numeric types,
    -- had to read question multiple times 
    SELECT 
    courier_id, 
    ROUND(AVG(ABS(end_point - start_point))::numeric, 0) AS avg_distance,
    SUM(quantity * 
        CASE 
            WHEN ABS(end_point - start_point) > delivery_fee  --here also absolute 
            THEN ABS(end_point - start_point) 
            ELSE delivery_fee 
        END) AS total_revenue
FROM 
    deliveries
WHERE 
    date >= CURRENT_DATE - INTERVAL '1 month'
    AND date < CURRENT_DATE -- missed this 
GROUP BY 
    courier_id;

-- Note - case when can be written like below for better clarity 
SUM( 
    CASE 
        WHEN ABS(start_point - end_point) > delivery_fee 
        THEN ABS(start_point - end_point) * quantity
        ELSE delivery_fee * quantity 
    END) AS total_revenue
```


#### [SQL Question 6: Average Delivery Time per Restaurant](2.30 min)

```sql 
SELECT restaurant_id, 
       AVG(EXTRACT(EPOCH FROM (delivery_time - order_time))/60) AS   avg_delivery_time_minutes -- give in minutes 
FROM orders
GROUP BY restaurant_id;
```
</details>

<details>
<summary> DAY 4 Practice </summary>

#### Write a SQL query that selects users who transitioned directly from “Data Analyst” to “Data Scientist”, with no other titles in between. Utilize subqueries or join conditions to capture the specific data pattern, and calculate the percentage based on the total number of users.

```sql
-- Could have used self join 
-- Percentages: Count users who pass the first checks and divide by the total relevant users (either all Data Analysts or all users, depending on the intent).
-- I’d ask if the percentage is out of all users or just Data Analysts.
-- I’m calculating the percentage out of users who were Data Analysts, since the question is about their career progression. Does that sound right, or should it be all users?
-- Remember the word “sequence” or “order” as your mental nudge to explore window functions like LAG, which is perfect for looking at “previous” or “next” records in a sorted list.
-- Think, “What if end_time is missing? Does that mean the role is ongoing?” 

WITH ordered_roles AS (
    SELECT 
        user_id,
        title,
        start_time,
        end_time,
        LAG(title) OVER (PARTITION BY user_id ORDER BY start_time, end_time) AS prev_title,
        LAG(end_time) OVER (PARTITION BY user_id ORDER BY start_time, end_time) AS prev_end_time
    FROM user_experiences
)
SELECT 
    ROUND(
        (COUNT(DISTINCT CASE 
            WHEN title = 'Data Scientist' 
            AND prev_title = 'Data Analyst' 
            AND prev_end_time <= start_time
            THEN user_id 
        END)::FLOAT / 
        COUNT(DISTINCT user_id)::FLOAT) * 100,
        2
    ) AS transition_percentage
FROM ordered_roles;
```

#### Let’s say we have a table representing vacation bookings. Write a query that returns columns representing the total number of bookings in the last 90 days, last 365 days, and overall.

```sql
-- 90 days is in quotes 
-- case when then 1 and 0 not order id (needs integer for sum)
-- operator between date and comparison 

SELECT 
    SUM(CASE WHEN booking_date >= CURRENT_DATE - INTERVAL '90 days' THEN 1 ELSE 0 END) AS last_90_days,
    SUM(CASE WHEN booking_date >= CURRENT_DATE - INTERVAL '365 days' THEN 1 ELSE 0 END) AS last_365_days,
    COUNT(*) AS all_time
FROM bookings;

-- in my sql and when start date is given then you have to check between 
SELECT
    COUNT(DISTINCT CASE WHEN check_out_date >= DATE_SUB('2022-01-01', INTERVAL 90 DAY) AND check_in_date <= '2022-01-01' THEN reservation_id END) AS num_bookings_last90d,
    COUNT(DISTINCT CASE WHEN check_out_date >= DATE_SUB('2022-01-01', INTERVAL 365 DAY) AND check_in_date <= '2022-01-01' THEN reservation_id END) AS num_bookings_last365d,
    COUNT(DISTINCT reservation_id) AS num_bookings_total
FROM
    bookings;

```
</details>

<details>
<summary> DAY 5-6 Practice </summary>

From https://platform.stratascratch.com/coding?companies=237&code_type=1

Schema \
consumer_id: bigint\
customer_placed_order_datetime: timestamp without time zone\
delivered_to_consumer_datetime: timestamp without time zone\
delivery_region:text\
discount_amount:bigint\
driver_at_restaurant_datetime: timestamp without time zone\
driver_id: bigint\
is_asap: boolean\
is_new:boolean\
order_total:double precision\
placed_order_with_restaurant_datetime:timestamp without time zone\
refunded_amount:double precision\
restaurant_id:bigint\
tip_amount:double precision\

#### 1. Workers With The Highest Salaries
```sql
WITH highest_sal AS (
    select worker_id from (
        select
        worker_id, -- missed ,
        rank() over(ORDER BY salary desc) as rn
        from 
        worker) work 
    where rn = 1 
)
select worker_title from 
highest_sal inner join 
title -- missed this table 
on highest_sal.worker_id = title.worker_ref_id

-----Alternate solution 
WITH max_salary AS (
    SELECT MAX(salary) AS highest_salary
    FROM worker
)
SELECT b.worker_title AS best_paid_title
FROM worker a
JOIN title b ON a.worker_id = b.worker_ref_id
JOIN max_salary ms ON a.salary = ms.highest_salary
ORDER BY best_paid_title;
```

#### 2. Bikes Last Used (3min)
```sql 
SELECT bike_number,
       max(end_time) last_used
FROM dc_bikeshare_q1_2012
GROUP BY bike_number
ORDER BY last_used DESC -- order by is done after group by and aggregation do last_used can be used 
```

#### 3. Avg Earnings per Weekday and Hour (6 min)
```sql 
-- if any of order_total, tip_amount, refunded_amount, or discount_amount can be NULL, you might want to wrap them -  `COALESCE(order_total, 0)`

-- Casting to Numeric: By adding ::numeric after the AVG(...) expression, we convert the double precision result of AVG to a numeric type, which ROUND can handle without issues.

SELECT 
    TO_CHAR(customer_placed_order_datetime, 'Day') AS day_of_week,
    EXTRACT(HOUR FROM customer_placed_order_datetime) AS hour,
    ROUND(AVG(order_total + tip_amount - refunded_amount - discount_amount)::NUMERIC, 2) AS avg_order
FROM doordash_delivery
GROUP BY 
    TO_CHAR(customer_placed_order_datetime, 'Day'),
    EXTRACT(HOUR FROM customer_placed_order_datetime)
ORDER BY 
    day_of_week, hour;
```
#### 4.Avg Order Cost During Rush Hours (7 min)
```sql 
SELECT
    EXTRACT(HOUR FROM customer_placed_order_datetime) AS hour,
    AVG(order_total + tip_amount - discount_amount - refunded_amount) AS avg_net_order_value
FROM delivery_details
WHERE EXTRACT(HOUR FROM customer_placed_order_datetime) BETWEEN 15 AND 17 -- filter should go in where - you put it in having which is for aggregated filters
AND delivery_region = 'San Jose' -- missed this condition 
GROUP BY EXTRACT(HOUR FROM customer_placed_order_datetime)
```
#### 5. Lowest Revenue Generated Restaurants 
Write a query that returns a list of the bottom 2% revenue generating restaurants. Return a list of restaurant IDs and their total revenue from when customers placed orders in May 2020.

You can calculate the total revenue by summing the order_total column. And you should calculate the bottom 2% by partitioning the total revenue into evenly distributed buckets.
```sql 
--problem mentions partitioning into evenly distributed buckets, which suggests using something like NTILE
WITH RestaurantRevenue AS (
    SELECT 
        restaurant_id,
        SUM(order_total) AS total_revenue
    FROM doordash_delivery
    WHERE customer_placed_order_datetime >= '2020-05-01 00:00:00' 
        AND customer_placed_order_datetime < '2020-06-01 00:00:00'
    GROUP BY restaurant_id
),
--assigns each restaurant to one of 100 buckets using NTILE(100) based on their total_revenue in ascending order. This means the lowest revenue restaurants will be in the lowest buckets.
RevenueBuckets AS (
    SELECT 
        restaurant_id,
        total_revenue,
        NTILE(100) OVER (ORDER BY total_revenue ASC) AS revenue_bucket
    FROM RestaurantRevenue
)
SELECT 
    restaurant_id,
    total_revenue
FROM RevenueBuckets
WHERE revenue_bucket <= 2
ORDER BY total_revenue ASC;

-- extract date part and use 
WHERE DATE(customer_placed_order_datetime AT TIME ZONE 'UTC') >= '2020-05-01' 
    AND DATE(customer_placed_order_datetime AT TIME ZONE 'UTC') < '2020-06-01'

```


#### 6. Delivering and Placing Orders correlation(3min)

You have been asked to investigate whether there is a correlation between the average total order value and the average time in minutes between placing an order and having it delivered per restaurant.


You have also been told that the column order_total represents the gross order total for each order. Therefore, you'll need to calculate the net order total.


The gross order total is the total of the order before adding the tip and deducting the discount and refund. Make sure correlation is rounded to 2 decimals
```sql
-- one shot correct code 
-- round numeric was correctly identified 
-- extract epoch from correct 
WITH RestaurantAverages AS (
    SELECT 
        restaurant_id,
        ROUND(AVG(EXTRACT(EPOCH FROM (delivered_to_consumer_datetime - customer_placed_order_datetime))/60)::numeric, 2) AS avg_del_time_min,
        ROUND(AVG(order_total + tip_amount - refunded_amount - discount_amount)::numeric, 2) AS avg_net_total
    FROM delivery_details
    GROUP BY restaurant_id
)
select * from  RestaurantAverages;
```

#### 7. Daily Top Merchants(20 min)

```sql
--GROUP BY reduces the number of rows by aggregating, while PARTITION BY works on the full set of rows (or the aggregated set if used after a GROUP BY) to compute values like rankings or running totals within each partition.
-- PARTITION BY is like telling the database, "for each group defined by this column, calculate something, but don’t combine the rows into one."
-- If you thought PARTITION BY merchant_id alongside a GROUP BY on date would work, it’s likely because you were picturing PARTITION BY as a way to focus on individual merchants within a broader grouping. But remember, PARTITION BY defines the scope of comparison for the window function.
-- window functions (including those with PARTITION BY) are typically evaluated after WHERE, GROUP BY, and HAVING but before ORDER BY and LIMIT.
-- GROUP BY sets up the summarized data, and PARTITION BY lets you do further analysis (like ranking) on that summarized data without losing the individual rows

-- GROUP BY happens early and squashes data into summary rows (e.g., one row per date-merchant with a count of orders).
-- PARTITION BY happens later in a window function and just draws invisible lines around groups of those rows to do calculations like ranking, without changing the row count.
-- Ask yourself: “Am I summarizing data (GROUP BY) or analyzing within subsets of it (PARTITION BY)?”

-- was trying to do in one CTE and got incorrect results
WITH daily_orders AS (
    SELECT 
        TO_CHAR(order_timestamp, 'YYYY-MM-DD') AS date,
        md.name,
        COUNT(*) AS order_count
    FROM order_details od
    INNER JOIN merchant_details md ON od.merchant_id = md.id
    GROUP BY TO_CHAR(order_timestamp, 'YYYY-MM-DD'), md.name  -- Aggregates by date and merchant
),
ranked AS (
    SELECT 
        date,
        name,
        DENSE_RANK() OVER (PARTITION BY date ORDER BY order_count DESC) AS rnk  -- Ranks within each date
    FROM daily_orders
)
SELECT date, name, rnk
FROM ranked
WHERE rnk <= 3
ORDER BY date, rnk, name;

```


#### 8. First Time Orders
- understood the first order of customer incorrectly 

```sql
WITH first_cust_order AS (
    SELECT customer_id, merchant_id
    FROM (
        SELECT customer_id, 
               merchant_id,
               ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_timestamp) AS rnk
        FROM order_details
    ) ranked
    WHERE rnk = 1
)
SELECT md.name,
       COUNT(od.id) AS total_orders,
       COUNT(DISTINCT fco.customer_id) AS first_time_orders
FROM merchant_details md
INNER JOIN order_details od
    ON md.id = od.merchant_id
LEFT JOIN first_cust_order fco
    ON md.id = fco.merchant_id
GROUP BY md.name;
```

#### 9.Highest Earning Merchants
```sql
WITH daily_totals AS (
    SELECT 
        merchant_id,
        DATE(order_timestamp) AS order_date,
        ROUND(SUM(total_amount_earned)::NUMERIC, 2) AS total_earned
    FROM order_details
    GROUP BY merchant_id, DATE(order_timestamp)
),
previous_day_earnings AS (
    SELECT 
        merchant_id,
        order_date,
        total_earned AS current_day_earned,
        LAG(total_earned, 1) OVER (PARTITION BY merchant_id ORDER BY order_date) AS prev_day_earned,
        LAG(order_date, 1) OVER (PARTITION BY merchant_id ORDER BY order_date) AS prev_date
    FROM daily_totals
),
filtered_consecutive_days AS (
    SELECT 
        merchant_id,
        order_date,
        prev_day_earned
    FROM previous_day_earnings
    WHERE prev_date IS NOT NULL 
    AND DATEDIFF(order_date, prev_date) = 1 -- if interval is not working 
),
ranked_merchants AS (
    SELECT 
        merchant_id,
        order_date,
        RANK() OVER (PARTITION BY order_date ORDER BY prev_day_earned DESC) AS rnk
    FROM filtered_consecutive_days
)
SELECT 
    TO_CHAR(order_date, 'YYYY-MM-DD') AS date,
    m.name
FROM ranked_merchants r
JOIN merchant_details m ON r.merchant_id = m.id
WHERE rnk = 1
ORDER BY order_date;
```

#### 10. [Extremely Late Delivery](https://platform.stratascratch.com/coding/2113-extremely-late-delivery?code_type=1)
```sql
SELECT 
    TO_CHAR(actual_delivery_time, 'YYYY-MM') AS month, -- REM To char for this format
    -- interval 20 minutes, days 
    (SUM(CASE WHEN actual_delivery_time > predicted_delivery_time + INTERVAL '20 minutes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) AS perc_late_orders
FROM delivery_orders
GROUP BY TO_CHAR(actual_delivery_time, 'YYYY-MM')
ORDER BY month; -- order by month in these questions 
```



#### 11.First Ever Ratings

```sql
with first_del as (
    select driver_id,
           row_number() over (partition by driver_id order by actual_delivery_time) as rnk,
           delivery_rating
    from delivery_orders
    where actual_delivery_time is not null
)
select  
    Round(Sum(Case when (delivery_rating = 0 and rnk=1) then 1 else 0 end) * 100.0 / count(distinct driver_id), 2) as percentage
from first_del;
```


#### 12. More Than 100 Dollars

```sql
-- Extract vs DATE_TRUNC('month', order_placed_time)
-- order_placed_time >= '2021-01-01 00:00:00' AND order_placed_time < '2022-01-01 00:00:00' (drastically reduce scan times)
-- WHERE order_placed_time >= '2021-01-01' AND order_placed_time < '2022-01-01'
-- '2021-01-01' is interpreted as the start of the day (midnight), just like '2021-01-01 00:00:00', in most databases like PostgreSQL.

WITH sales AS (
    SELECT 
        restaurant_id,
        EXTRACT(MONTH FROM order_placed_time) AS month, -- extract syntax 
        SUM(sales_amount) AS sales_amount
    FROM delivery_orders AS del
    JOIN order_value AS ov -- left join if we consider all restaurants 
        ON del.delivery_id = ov.delivery_id
    WHERE EXTRACT(YEAR FROM order_placed_time) = 2021
        AND actual_delivery_time IS NOT NULL 
    GROUP BY EXTRACT(MONTH FROM order_placed_time), restaurant_id
)
SELECT 
    month,
    ROUND(SUM(CASE WHEN sales_amount >= 100 THEN 1 ELSE 0 END) * 100.0 / COUNT (restaurant_id), 2) AS per_rest_sales_gre_100 -- round
FROM sales
GROUP BY month
ORDER BY month;
```


#### 13. Top 2 Restaurants of 2022(5 min)

Christmas is quickly approaching, and your team anticipates an increase in sales. To predict the busiest restaurants, they wanted to identify the top two restaurants by ID in terms of sales in 2022.

The output should include the restaurant IDs and their corresponding sales.

Note: Please remember that if an order has a blank value for actual_delivery_time, it has been canceled and therefore does not count towards monthly sales.
```sql 
SELECT 
    do.restaurant_id,
    SUM(ov.sales_amount) AS total_sales
FROM delivery_orders do
JOIN order_value ov ON do.delivery_id = ov.delivery_id
WHERE 
    DATE_PART('year', do.actual_delivery_time) = 2022 -- could have used this 
    AND do.actual_delivery_time IS NOT NULL
GROUP BY do.restaurant_id
ORDER BY total_sales DESC, do.restaurant_id ASC
LIMIT 2;

-- another approach
SELECT 
    restaurant_id,
    total_sales,
    rank_position
FROM (
    SELECT 
       d.restaurant_id AS restaurant_id, 
       SUM(o.sales_amount) AS total_sales,
       RANK() OVER (ORDER BY SUM(o.sales_amount) DESC) AS rank_position
    FROM delivery_orders d -- as do was not working 
    JOIN order_value o ON d.delivery_id = o.delivery_id
    WHERE 
        DATE_PART('year', d.actual_delivery_time) = 2022
        AND d.actual_delivery_time IS NOT NULL
    GROUP BY d.restaurant_id
) AS ranked_data
WHERE rank_position <= 2;

```
#### 14. Average On-Time Order Value (4 min)
```sql
SELECT driver_id,
       AVG(order_total) AS avg_order_value
FROM delivery_details
WHERE EXTRACT(EPOCH FROM (delivered_to_consumer_datetime - customer_placed_order_datetime))/60 <= 45 -- order of subtraction -- epoch from extract logic 
GROUP BY driver_id;

--- another approach 
SELECT driver_id,
       AVG(order_total) AS avg_order_value
FROM delivery_details
WHERE (delivered_to_consumer_datetime - customer_placed_order_datetime) <= INTERVAL '45 minutes' -- better, I came up with this but got confused 
GROUP BY driver_id;
```

#### 15. Workers Who Are Also Managers 
```sql
select worker.first_name, 
worker_title
from worker
inner join title
on title.worker_ref_id = worker.worker_id
and worker_title = 'Manager'

```
#### Doordash total orders from 2022 - 2024 month on month and quarter as well
```sql SELECT 
    YEAR(order_date) AS year,
    QUARTER(order_date) AS quarter,
    MONTH(order_date) AS month,
    DATE_FORMAT(order_date, '%Y-%m') AS month_year,
    COUNT(*) AS total_orders
FROM 
    orders
WHERE 
    order_date BETWEEN '2022-01-01' AND '2024-12-31'
GROUP BY 
    YEAR(order_date),
    QUARTER(order_date),
    MONTH(order_date),
    DATE_FORMAT(order_date, '%Y-%m')
ORDER BY 
    year, quarter, month;
```

#### Cumulative Sales of Restaurant 100011
```sql
SELECT 
    order_date,
    restaurant_id,
    SUM(sales_amount) AS daily_sales,
    SUM(SUM(sales_amount)) OVER (PARTITION BY restaurant_id ORDER BY order_date) AS cumulative_sales
FROM food_order
WHERE restaurant_id = 100011
GROUP BY order_date, restaurant_id
ORDER BY order_date;
```