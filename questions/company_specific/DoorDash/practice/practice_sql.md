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

