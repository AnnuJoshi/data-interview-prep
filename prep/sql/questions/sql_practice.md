#### Questions

<details> 
  <summary>1. Find Median Given Frequency of Numbers</summary>

```sql 
    select percentile_cont(0.5) within group (order by num) as median
    from (
        select num
        from numbers, generate_series(1, frequency) -- cross join 
        -- will create rows for each num value equal to its corresponding frequency
        -- SELECT * FROM table1 CROSS JOIN table2 no condition is required - it generates all combinations 
        )
```

GENERATE_SERIES(start, stop, step)

1. If you don’t specify a step, it defaults to 1 for numbers or a day for timestamps.\
2. It returns a set of values from start to stop, inclusive, incrementing by step.
```sql 
SELECT * FROM GENERATE_SERIES('2023-01-01'::date, '2023-01-05'::date, '1 day'::interval)
--tweak the interval to hours, month

select Cast(generate_series(timestamp '2012-08-01',
			'2012-08-31','1 day') as date) as date
```

PERCENTILE_CONT(fraction) WITHIN GROUP (ORDER BY column)

PERCENTILE_CONT is a PostgreSQL aggregate function used to calculate a percentile value from an ordered set of data, assuming a continuous distribution

Unlike PERCENTILE_DISC (which picks an actual value from the dataset)PERCENTILE_CONT interpolates between values if the exact percentile doesn’t correspond to a specific data point

WITHIN GROUP syntax is part of PostgreSQL’s ordered-set aggregate functions, of which PERCENTILE_CONT is one.

These functions operate on a group of rows (like regular aggregates such as SUM or AVG), but they also need an internal ordering for each group to compute their result.\
WITHIN GROUP (ORDER BY ...) specifies that internal ordering for the function. It’s not about grouping rows like GROUP BY in the main query—it’s about how the values within the aggregation are sequenced.\
For PERCENTILE_CONT, this clause is mandatory because the function is defined as an ordered-set aggregate.
</details>

<details>
<summary> 2. Consecutive Available Seats </summary>

```sql
select seat_id from 
(
select seat_id ,
lag(free, 1) over (order by seat_id) as prev_free,
lead(free, 1) over (order by seat_id) as next_free, 
free 
from Cinema 
) where free = 1 and( prev_free = 1 or  next_free =1 )

--- Second way 
SELECT seat_id
FROM (
    SELECT seat_id,
           free,
           SUM(free) OVER (ORDER BY seat_id
                           ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING) AS cnt
    FROM   Cinema
) AS t
WHERE free = 1 AND cnt >= 2;

```
</details>

<details>
<summary>585. Investments in 2016 </summary>
https://leetcode.com/problems/investments-in-2016/description/

```sql
-- got stuck in self join, should have though in this direction 

SELECT ROUND(SUM(tiv_2016)::NUMERIC,2) AS tiv_2016 
FROM Insurance 
WHERE (tiv_2015)
 IN (SELECT tiv_2015 FROM Insurance GROUP BY tiv_2015 HAVING COUNT(*) > 1) AND
(lat, lon) IN (SELECT lat, lon FROM Insurance GROUP BY lat,lon HAVING count(*) = 1)

```
</details>

<details>
<summary> 4. Consecutive dates for each customer ID </summary>

```sql
-- Group consecutive dates for each customer ID, where consecutive means the dates are one day apart, and start a new group when the difference between dates is more than one day. We’ll output the customer ID, start date, and end date for each group of consecutive dates.

WITH DateDiffs AS (
    SELECT 
        customer_id,
        order_date,
        LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date) AS prev_date,
        CASE 
            WHEN order_date = LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date) + INTERVAL '1 day'
            THEN 0
            ELSE 1
        END AS is_new_group
    FROM customer_orders
),
GroupAssignment AS (
    SELECT 
        customer_id,
        order_date,
        SUM(is_new_group) OVER (PARTITION BY customer_id ORDER BY order_date) AS group_id --cummulative sum 
    FROM DateDiffs
)
SELECT 
    customer_id,
    MIN(order_date) AS start_date,
    MAX(order_date) AS end_date
FROM GroupAssignment
GROUP BY customer_id, group_id
ORDER BY customer_id, start_date;
```
</details>