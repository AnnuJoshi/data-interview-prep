#### Write a query that will show how many unique transactions customers had during the month of Aug, 2023. Ensure the query includes the customers who had zero transactions in Aug, 2023.

```sql
SELECT 
    c.customer_id,
    COUNT(DISTINCT trans.Transaction_ID) AS unique_transactions
FROM customer AS c 
LEFT JOIN trans AS t
    ON c.customer_id = t.customer_id
WHERE DATE_TRUNC('month', t.Order_Date_Time) = '2023-08-01'::date    -- remember this 
GROUP BY c.customer_id;
```


#### You are the BIE for softlines (Apparels, Beauty Products, Cosmetics, Shoes/Belts) marketing team at Amazon. Leadership has asked you to create a dashboard which provides 2023 performance.What kind of data visualization would you builds?
