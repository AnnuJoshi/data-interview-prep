#### Write a query that will show how many unique transactions customers had during the month of Aug, 2023. Ensure the query includes the customers who had zero transactions in Aug, 2023.

Trans Table:
Transaction_ID | Customer_ID | Item_ID  | Order_Date_Time     | Unit_Price | Quantity_Sold\
AYR81564P      | 12345434    | 4325432  | 2023-08-30 16:10:10 | 22.07      | 3\
AQWS8165P      | 12349874    | 3245332  | 2023-08-03 18:16:08 | 107.91     | 1\
AYRS8165P      | 46532274    | 9854344  | 2023-08-27 17:08:45 | 68.12      | 4


Customer Table:
Customer_ID | Customer_Name    | Hashed Email_Address | Address         | Zip_Code | State | Country\
12345434    | James Dove       | sV7B4fR5y96uoshOcPV7 | 123234 Abc 15th | 98933    | FL    | US\
12349874    | John Michael     | Vd1fCoMYS86zgRejhi3Q | 123234 Abc 12th | 67543    | WA    | US\
46532274    | Alexander Bell   | mjm0iLos3F1vkxyOPYh6 | 123234 Abc 9th  | 45433    | MD    | US


There is a problem with this solution as you are filtering based on transaction data 
WHERE clause eliminates zero-transaction customers
```sql
SELECT 
    c.customer_id,
    COUNT(DISTINCT t.Transaction_ID) AS unique_transactions
FROM customer AS c 
LEFT JOIN trans AS t
    ON c.customer_id = t.customer_id
WHERE DATE_TRUNC('month', t.Order_Date_Time) = '2023-08-01'::date    -- remember this 
GROUP BY c.customer_id;
```

You need Filter transactions to August 2023 in JOIN 
```sql
SELECT 
    c.Customer_ID,
    c.Customer_Name,
    COUNT(t.Transaction_ID) AS Transaction_Count
FROM Customer c
LEFT JOIN Trans t ON c.Customer_ID = t.Customer_ID 
    AND t.Order_Date_Time >= '2023-08-01' 
    AND t.Order_Date_Time < '2023-09-01'
GROUP BY c.Customer_ID, c.Customer_Name
ORDER BY c.Customer_ID;
```


#### You are the BIE for softlines (Apparels, Beauty Products, Cosmetics, Shoes/Belts) marketing team at Amazon. Leadership has asked you to create a dashboard which provides 2023 performance.What kind of data visualization would you builds?
