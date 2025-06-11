Schema 
restaurants       (restaurant_id PK, name, city, signup_date)
orders            (order_id PK, restaurant_id FK, customer_id FK,
                   placed_at TIMESTAMP, status VARCHAR,
                   subtotal_cents INT, delivery_fee_cents INT,
                   courier_id FK, cancelled_at TIMESTAMP NULL)
order_items       (order_id FK, item_id FK, quantity INT, price_cents INT)
couriers          (courier_id PK, name)
customers         (customer_id PK, name, city, signup_date)
Statuses are ‘PLACED’, ‘DELIVERED’, ‘CANCELLED’.
Assume data spans multiple years and CURRENT_DATE is 2025-06-11.

Section A SQL Practice (4 Qs)
Suggested timing: 6–8 min each
Recommended features: DATE_TRUNC, INTERVAL arithmetic, JOINs, conditional aggregation, window functions, CTEs.

A-1 Year-over-Year January Order Declines (Easy)
Return restaurant_id, this_year_orders, last_year_orders, percent_change for every restaurant whose January order count this year < January order count last year.


with order_count_last_year as 
(
    Select restaurant_id, count(order_id) as count_last_year
    from orders
    where placed_at >= '2024-01-01' and placed_at < '2024-02-01'
    group by restaurant_id
),
order_count_last_year as 
(
    Select restaurant_id, count(order_id) as count_curr_year
    from orders
    where placed_at >= '2025-01-01' and placed_at < '2025-02-01'
    group by restaurant_id
),
filetered_rest as
(
Select cy.restaurant_id, count_last_year, count_curr_year
from order_count_last_year as ly
inner join order_count_last_year as cy
on ly.restaurant_id = cy.restaurant_id
and cy.count_curr_year < ly.count_last_year
) 
select 
rest.restaurant_id,
count_last_year, 
count_curr_year, 
Round((count_curr_year-count_last_year/ count_last_year)*100.0,2) as perc_change
from 
filetered_rest left join 
restaurants as rest 
ON restaurant_id = rest.restaurant_id;
order by perc_change desc 

Requirements

Compare January 2025 vs January 2024.
Percent change = (this_year − last_year) / last_year.
Order by percent_change ASC (biggest drop first).

A-2 30-Day Cancellation Rate per Restaurant (Easy/Medium)
For each restaurant that had ≥ 30 total orders in the past 30 days (relative to CURRENT_DATE), output:
restaurant_id | total_orders | cancelled_orders | cancel_pct
Cancel % = cancelled_orders / total_orders, rounded to 2 decimal places.
Order by cancel_pct DESC, break ties by total_orders DESC.
Hint: status = 'CANCELLED' OR cancelled_at IS NOT NULL.

with filetered_rest as (
 Select restaurant_id, 
    count(order_id) as order_count, 
    sum(case when status = 'CANCELLED' OR cancelled_at IS NOT NULL then 1 else 0 end) as cancelled_orders
    from orders
    where placed_at >= Date_trunc(current_date, -30 days)
    and order_count > 30
    group by restaurant_id
) select restaurant_id, 
order_count as total_orders, 
cancelled_order, 
Round(cancelled_order/(total_orders*1.0),2) as cancel_pct
from filetered_rest
order by cancel_pct DESC, total_orders DESC


A-3 7-Day Rolling Avg Delivery Fee by City (Medium)
Produce a result set with columns

window_start (DATE) | city | avg_delivery_fee_cents
for every city and every 7-day window (inclusive) in the past 90 days.
• A window starts each day, so windows will overlap.
• Use window functions, not self-joins.
• Exclude cities with < 100 orders in that 7-day window.
• Order by window_start, then city.

with city_orders(
select o.restaurant_id, r.city, o.delivery_fee_cents, o.placed_at
from orders as o 
join restaurants as r 
on o.restaurant_id = r.restaurant_id 
)
select placed_at, city, 
AVG(LAG(delivery_fee_cents, 7) over (partition by city order by placed_at ) ) as  avg_delivery_fee_cents
from city_orders
group by city 
having count(placed_at) < 100 
order by window_start, city 




A-4 Likely Churned Customers (Medium)
Find customers who

Placed ≥ 3 orders lifetime, and
Have no orders in the last 60 days.
Return: customer_id, lifetime_orders, days_since_last_order
Sort descending by days_since_last_order.

with cust_gr_3_orders(
   Select customer_id, count(order_id) as lifetime_orders
    from orders
    group by customer_id
    having orders_placed > 3
),
cust_no_orders_in_3_months(
    Select customer_id, 
    count(order_id) as orders_placed, 
    datediff(current_date - max(placed_at)) as days_since_last_order
    from orders
    where placed_at < Current_date - '60 days'
    group by customer_id
    having orders_placed = 0
)
select customer_id, 
lifetime_orders, 
days_since_last_order
from cust_gr_3_orders 
inner join cust_no_orders_in_3_months
on customer_id 
order by days_since_last_order desc 

