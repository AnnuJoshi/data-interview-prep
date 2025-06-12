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
```

#### A-2 30-Day Cancellation Rate per Restaurant (Easy/Medium)
For each restaurant that had ≥ 30 total orders in the past 30 days (relative to CURRENT_DATE), output:\
restaurant_id | total_orders | cancelled_orders | cancel_pct\
Cancel % = cancelled_orders / total_orders, rounded to 2 decimal places.\
Order by cancel_pct DESC, break ties by total_orders DESC.\
Hint: status = 'CANCELLED' OR cancelled_at IS NOT NULL.\

```sql
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

WITH daily AS (          -- 1. compact orders into one row per (city, day)
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
rolling AS (            -- 2. 7-day window that starts ON EACH order_date
    SELECT
        order_date                            AS window_start,
        city,
        /* number of orders in the 7-day span [window_start, window_start+6] */
        SUM(day_orders)    OVER (
            PARTITION BY city
            ORDER BY order_date
            RANGE BETWEEN CURRENT ROW AND INTERVAL '6 days' FOLLOWING
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
