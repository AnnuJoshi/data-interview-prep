<details>
<summary> Links </summary>

1. [Medium Article](https://medium.com/@karkisatkarhere/from-patterns-to-practice-50978850fa5f)
2. [Jade Codes](https://www.youtube.com/watch?v=biaaA9GfNPw)

    
</details>


<details>
<summary> Analytical Pattern bootcamp notes</summary>

1. Growth Accounting
    - How FB tracks inflow and outflow of active and inactive users (any state change tracking) 
2. Survival Analysis 
    - Of all users that signed up today, what % are still active in 30 days, 60 days, 90 days (Retention Number)

<details>
<summary> 7 patterns </summary>

<details>
<summary> 1. Aggregation-based patterns  </summary>

- The most common type of analysis
- You will mostly use `Group BY` with `Sum, AVG, percentile, count, may be array_agg`  
1.  Trend Analysis also give you RCA 
    - wow(week on week) change of dimension shows +1million but it should also give you that +1.5mil in US but -0.5 mil in India, shows it can be different overall. Bring in different dimensions like gender, country.
2. Root Cause Analysis (WHY)
    - line chart we have a dip and the reason for the dip is e.g. of spike during chinese new year for the airline. 
3. Composition 
    - e.g., user distribution by region, we have these many users in US, China.
4. Always have upstream data aggregated at daily level, that is aggregated along user_id 
    - Good for experimentation - group users and then easily add dimension to the metrics
5. IMP - when doing agg, you shouldn't be going back to fact data because fact data should be aggregated along the dimension like user_id, device_id. Dimensions will not be 1:1 
    - A key takeaway is to aggregate data at a daily level along a primary dimension (like user ID) for efficiency and to support experimentation (A/B testing). 
 6. However, caution is advised against including too many dimensions, as it can lead to overly granular data that loses analytical value.

#### Gotchas 
1. Careful about what all dimensions you bring in aggregation - will get you back to daily data 
2. Be mindful of grain you are working with, gender is cool only two-three, country only one person follows me if he leaves 100% drop so lookout at numbers as well when dealing with %.
3. Long time frame analysis (>90 days) - try to lower the cardinality, look at per week or year may be not per day, to avoid lot of rows. 90 days - countries 200 = 1800 rows if you have any high cardinality dimension then it will increase.
</details>

<details>
<summary> Cumulation based patterns </summary>

- based on cumultaive table design
- changes over time, between consecutive days (e.g., active today vs. yesterday)
- FUll outer join (to account for missing data, where "no data is data.") here no data is data, we want to keep track of it. In aggregation we don't care about no data.

1. State Change Tracking
- opposite of SCD 
- instead of keeping all values of a dimension, it just keep the changed value, like a change log 

    - Growth Accounting 
        - New (didn't exist yest, active today)
        - Retained (active yest, active today)
        - Churned (active yest, inactive today)
        - Resurrected (active today, inactive yest)
        - Stale (inactive yes, inactive today)
        - deleted (don't exist today but were active/inactive yest) 
    
    - Growth rate = (new +resurr) - churned
    - used for how users are interacting with notifications. 
    - Also used for tracking fake accounts, new fake account, reclassified as fake account, declassified.
    - ML model at Netflix was labelling applications as risky and not risky, then monitored the flow. 
    - At Airbnb, model for hosts classification - host cancels on you. labelling hosts as risky not risky, track the effectiveness of training hosts.
    - It’s particularly powerful for monitoring machine learning model health (e.g., sudden shifts in classifications post-update) and strategic goals (e.g., reducing risky hosts through education).

2. Retention(J curves)
    - tracking how many users remain active over time from a cohort
    - Survivorship analysis measures retention from a reference date (like signup) over time, starting at 100% and declining as users drop off.
    - Successful apps show a flattening curve (some users stick around long-term), while a steep decline indicates poor stickiness.
    - beyond growth to areas like cancer patient survival (reference: diagnosis date, state: alive), smokers remaining smoke-free (reference: quit date).
</details>

<details>
<summary> Window Based patterns </summary>
    
- Calculations over a time window, split into two types: 1. day-over-day, week-over-week, month-over-month, or year-over-year changes (like `derivatives`, showing rate of change) and `rolling sums or averages` (like integrals, showing cumulative trends).
- syntax involving partitioning by dimensions like user ID and defining the window size (e.g., rolling 7 days). 
- A practical note is to partition data in big data environments to avoid performance issues.
- `Derivative metrics` make charts spikier, increasing volatility (especially day-over-day), while `rolling metrics` smooth noise, as seen in stock trading with 50-day or 200-day moving averages (e.g., golden cross for buy signals when 50-day crosses above 200-day)
- Airbnb example notes year-over-year metrics were skewed by the 2020 pandemic, leading to comparisons with 2019 instead.

</details>

<details>
<summary> Enrichment Based patterns </summary>
We are already have all the columns we need to we will skip this one, we are assuming to be in the master layer.

</details>
</details>


2. Experimentation
3. Prediction
4. Clustering
5. Decision Tree
6. Accumulation Derivative 
7. Funnel analysis 
</details>