#### DATE_TRUNC 
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

