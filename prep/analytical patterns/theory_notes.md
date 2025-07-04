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

--- move to leadership ----
- Think of High level abstract layer - SQL will write itself - beyond the language it is written in - Repeatable analyses is your best friend

- mckinsey refit framework 
- dashboard for DBT at zoom - think about the abstraction 
- SQL might be different in future 
- Streamline your impact - cake making takes time  - you do everything from scratch or you buy some pre-made things and assemble it 
- allow you to play with bigger legos - not have to play with two blocks 
--------------------------



<details>
<summary> Aggregation-based patterns  </summary>

- The most common type of analysis
- You will mostly use `group by` with `Sum, avg, percentile, count, may be array_agg` 
- bring in different dimensions like gender 
1.  Trend Analysis 
    - wow(week on week) change of dimension is a + 1million but it should give you that +1.5mil in US but -0.5 mil in India, can be different overall
2. Root Cause Analysis (WHY)
    - line chart we have a dip and the reason for the dip is e.g. of spike during chinese new year for the airline 
3. Composition
    - to know we have this many users in US, China
4. Always have upstream data aggregated at daily level, that is aggregated along user_id 
    - Good for experimentation - group users and then easily add dimension to the metrics
5. IMP - when doing agg, you shouldn't be going back to fact data because fact data should be aggregated along the dimension like user_id, device_id. Dimensions will not be 1:1 
6. If you join fact data with all the dimensions then do aggregate it will gnarly 

#### Gotchas 
1. Careful about what all dimensions you bring in aggregation - will get you back to daily data 
2. Grain you are working with, gender is cool only two -three, country only one person follows me if he leaves 100% drop so lookout at numbers as well when dealing with %
3. Long time frame analysis (>90 days) lower the cardinality, look at per week or year may be not per day, to avoid lot of rows. 90 days - countries 200 = 1800 rows if you have any high cardinality dimension then it will increase.
</details>

<details>
<summary> Cumulation based patterns </summary>
    
- based on cumultaive table design
- care a lot about shift of state between today and yesterday 
- FUll outer join (you need to keep track when there is no data) here no data is data, we want to keep track of it. In aggregation we don't care about no data

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
    - used for how users are interacting with notifications. Also used for tracking fake accounts, new fake account, reclassified as fake account, declassified
    - ML model at Netflix was labelling applications as risky and not risky, then monitored the flow 
    - At Airbnb, model for hosts classification - host cancels on you. labelling hosts as risky not risky, track the effectiveness of training hosts.
    - So, this pattern is not limited to growth 

2. Retention(J curves)

</details>

<details>
<summary> Window Based patterns </summary>


</details>

<details>
<summary> Enrichment Based patterns </summary>
We are already have all the columns we need to we will skip this one, we are assuming to be in the master layer.

</details>
</details>



<details>
<summary> 7 patterns </summary>

1. Aggregation 
2. Experimentation
3. Prediction
4. Clustering
5. Decision Tree
6. Accumulation Derivative 
7. Funnel analysis 
</details>