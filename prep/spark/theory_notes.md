<details> 
<summary>  Spark Basics  </summary>

- Started with Hadoop(Java Map/Reduce) in 2009 -> Hive (switch from Hive to Presto) Presto does everything in memory, if it is not happening in memory it fails -> Spark 
- APIs of Spark - Dataframe, SparkSQL, Dataset, Pyspark

#### Features 
- Leverages RAM 
Group by in Hive - written and read from disk - very resilient but slow 
- Spark - minimize time by
- Spark only write to disk when not enough mem the only it spill to disk 
- Storage Agnostic - you can read anything you want Mongo DB, Relational DB 
- Don't necessarily need to use with databrick 

#### Don't wanna use spark when
- you are the only one who knows spark - better reliance and maintainability and distribute work - Use big quey or snowflake - Homogeneity of pipelines is imp

#### Components 

1. Plan   (Play)
- Transformation you do in Python, SQL, Scala
- Plan is evaluated lazily (execution only happens when it needs to )
- write data out somewhere or collecting data (taking info from play and bringing to coach and coach telling what to do next)

2. Driver (Coach)
- driver reads the plan what plan to run 
- can have multiple setting (may be 10), 2 you need to know
- mem driver has to process the job `spark.driver.memory` can go all the way to 16GB, default to 2 GB 
    - Two cases when you need to bump it 
        - collect() when data it is processing changes the plan of the job, bad practice
        - complicated job where it has multiple 
- memory overhead `spark.driver.memoryOverheadFactor`
    - complicated job then - mem that java needs to run- JVM take up more memory
    - What % of mem driver needs for non heap related tasks, usually 10%

    Driver Tasks 
    1. When the job should Execute - when it finds output or collect() 
    2. How to JOIN the datasets - what type of join - determines the performance of your job 
    3. How much Parallelism is needed in each step 
        - let's say you are dealing with two big datasets 
        - how many files those datasets are written to 
        

3. Executor (Players)
- Actually do the work - Driver passes the plan to Executors, they transform - aggregate 
- Settings 
    1. `spark.executor.memory` - same constraint as driver mem 2-16GB 
        - Determines how much memory each executor gets 
        - If a job OOMs people will update it to 16GB and then leave , run it at different level, and one of them runs all the time for couple of times. 
        - You dont want too much padding - expensive 
    2. `spark.executor.cores` 
        - How many task can happen on each machine 4-6 - more parallelism 
        - Bottleneck - throughput of too many task running at the same time
        - Skewed tasks 
    3. `spark.executor.memoryOverheadFactor` 
        - What % of mem should executor use for non heap related tasks usually 10%. For jobs with lots of UDFs you might need to bump this.
        - can increase this without increasing memory


<details>
<summary> Types of JOIN in Spark</summary>
 
1. Shuffle Sort Merge Join 
    - Default Join 
    - Works when both sides of join are large datasets 
    - most versatile , least performant
2. Broadcast Hash Join 
    - works well if one side of join is small, it just ships the whole dataset to the executor and you don't have to shuffle at all, upto 8-10 GB you will be okay.
    - `spark.sql.autoBroadcastJoinThreshold` default is 10 Mb, problems above 10 GB
    - A join without Shuffle!
3. Bucket Join
    - A join without Shuffle!
    - Efficient for joins without shuffle if data is pre-bucketed (use powers of 2 for bucket counts, e.g., 2, 4, 8).

Use .explain
Add Diagrams 
</details>


<details>
<summary>  What is Shuffle and How does it work? </summary>

- Shuffling in Spark is the process of redistributing data across the partitions of a cluster so that `related data (usually based on a key)` ends up on the `same executor or node` for processing.
- Spark works on a divide-and-conquer model, splitting data into partitions that are processed in parallel. When an operation requires data from different partitions to be combined—like in a join or aggregation—Spark needs to move data around to group it appropriately.
- When a shuffle is triggered, Spark first determines `how to partition the data based on the operation`. For most operations like joins or groupByKey, it uses a `hash-based partitioning strategy`. This means Spark applies a hash function to the key (or keys) of each record to decide which partition the record should go to. The goal is to ensure that records with the same key land in the same partition, so they can be processed together.
- For example, in a join, if two rows from different datasets have the same join key, the hash function ensures they’re sent to the same target partition.
- Two main phases: 1. write phase 2. fetch phase.
    - `WRITE Phase` - each executor processes its local partitions of the data, computes the hash of the keys, and writes the data into temporary files (or buffers) on its local disk, grouped by the target partition,—but the data stays on the original executor. These are often called "shuffle files." 
        - Spark also creates a map of where each piece of data is written, so it knows which executor holds which partition’s data. This step can spill to disk if the data doesn’t fit in memory, which is common with large datasets.
    - `FETCH Phase`, executors pull the data they need for their assigned partitions from other executors across the cluster. This is where the network overhead comes in, as data is transferred over the network between nodes. Each executor reads the shuffle files (or buffers) from other executors based on the partition mapping created earlier. Once the data is fetched, it’s ready for the next stage of processing, like sorting or merging in the case of a Shuffle Sort Merge Join.
    - Writing locally first allows executors to process and bucket the data without immediate network transfer, which can be done in parallel and reduces contention. It also means that if something fails, Spark can recover using lineage information without having to redo the entire shuffle from scratch. The fetch phase then focuses on moving only the necessary data to the right place for the downstream computation, like a join or aggregation.
    - `Shuffling is expensive` because it involves **disk I/O**, **network transfer**, and sometimes **serialization/deserialization of data**. It’s often a bottleneck in Spark jobs, especially if the data is unevenly distributed (data skew), causing some partitions to be much larger than others, or if the cluster’s network bandwidth is limited. Spark tries to optimize this with techniques like combining records before shuffling (using combiners in operations like reduceByKey) to reduce the amount of data moved, or by tuning parameters like the number of partitions to balance the load.
    - `Shuffling happens automatically when needed, based on the operation.` You don’t explicitly trigger it, but you can influence it by setting configurations like `spark.sql.shuffle.partitions` (default is 200) to control how many partitions the shuffled data is split into, which can help manage workload distribution.

#### How it works ?

- Least scalable part of Spark. Fine for smaller data (under 1-10TB),as scale goes up 20-30 TB a day, shuffle is out of window, you need to solve differently.

    ![Example](../../resources/ezachly_community_bootcamp/images/spark/shuffle_works.png)

- Let's say you have a table with data in 4 files - we do a map operation first (add a new column, or .withcolumn()) - map is infinitely scalable - then imagine we do a group by user id - Let's say we have 3 partitions, (default is 200) so you divide user_id by 3 then whatever remainder you get is the partition number where it goes. 
- So all data from File4 will be in partition 1,2 or 3.
- In join also, shuffle will be similar, all user_id divisible by n go to same partition and then you can do the join. 

- In Broadcast join, Spark avoids the heavy overhead of shuffling data across the cluster by "broadcasting" the smaller dataset to all the executors. Instead of redistributing both datasets to match keys (like in a shuffle sort merge join), Spark just ships the entire small dataset to every executor where the larger dataset resides.

#### Parallelism:
- `spark.sql.shuffle.partitions`  and `spark.default.parallelism` are essentially the same unless you are using RDD API
- Use higher-level APIs (DataFrame, Spark SQL) over RDD for better control.
- Is shuffle good or bad?
    - Low to Medium Volume  -> Good
    - High Volumn > 10 TB   -> Painful

Example from netflix 
- Processed 100TB/hour joining network requests(which IP was connecting to which IP microservice?) to microservices. Broadcast join worked until IPv6 expanded data size, forcing a shuffle join (failed). Solved upstream by logging app data directly.    
- Netflix wanted to shift from IPv4 to IPv6
    - Bucketting 100 TB per hours at Netflix 
    - Solved upstream - asked teams to log app in the data - removed the join altogether.

Example from Facebook - feature generation for notification at notification level
- Joined massive datasets (10TB + 50TB). Bucketing on user ID (1,024 buckets) avoided shuffles for multiple joins; skew was a pain but managed with filtering outliers. -- took 30% of all compute.

    - Notification 10TB join Notification 50TB 
    - bucketted the tables on user_id 1024 buckets 
    - join without shuffle 
    - files have guarantee - all data for that id is in that file 
    - user_id % bucket_id 
    - line up the buckets 
    - even if two tables don't have same number of buckets, assuming they are multiple of each other - Always bucket in power of 2
    - How to bucket? We had 10 TB of data - 1024 - 10GB per bucket - you don't want empty buckets as well


When to bucket ?
- to minimize or eliminate the need for shuffle in join 
- When multiple joins happening downstream 
- You have to pay Shuffle cost to bucket 
- If you are doing one join then why you doing that ? Only benefit when there are multiple joins 
- Presto can be weird with bucketted tables, with small number of buckets
    - main drawback - initial parallelism = # of buckets    
    - Bucket join only works when two tables have multiple of each other buckets if one has 2 other has 3 it will not work
</details>


<details>
<summary> Shuffle and Skew </summary>

- What is Skew?
    - Happens when data is unevenly distributed across partitions (e.g., one executor gets way more data due to popular user IDs like Beyoncé’s). Can cause jobs to fail at 99%—super frustrating - Jobs will get to 99%, take forever then fail. 

- Symptoms: Jobs take forever or fail near completion; use box-and-whisker plots for scientific confirmation (or just rage when it fails).

- Solutions:
    - Adaptive Query Execution - ( Only in Spark 3+) to auto-handle skew (more resilient but slower due to extra stats).
        - set `spark.sql.adaptive.enabled` = True 
        - more expensive - slower
    - Salting the group by - Before Spark 3
        - Group by a random number, aggregate + Group by 
        - Careful with AVG - USE sum, count and divide
    - Joins 
        - identify the outliers and filter them out 
        - partition the downstream table - one side handle the outlier and otherside handle the other 


#### Spark on Databricks vs Regular Spark
- Notebook on Databricks - good for PoCs - good for non technical people
    - don't invite unit test, integration test 
- Check code into git - spark submit 

#### Spark Query Plans 
- explain() your dataframes - to know your join strategies 

#### Where can spark read data from?
- Everywhere!
- From the Lake
    - Delta Lake, Apache Iceberg, Hive Metastore
- From an RDBMS
    - Postgres, Oracle etc
- REST API 
    - Remember that call is always in the driver, what if reponses are big? Careful on how you are processing that data? 
    Solution - List of urls - call spark.parallelise make the calls in executor, its a tradeoff - you can overwelhm the API with parallel calls. How are people doing it ?
    - beware of driver memory limits with APIs—parallelize calls or read directly from databases.
- From Flat Files - csv, json

#### Partitioning 
- on Date - execution date of pipeline 
- ds_partitioning 
- Sorting: Use sortWithinPartitions over global sort to avoid double shuffles, especially at scale (check plans with explain).
</details>

<details>
<summary> Pyspark Lab </summary>

- Pyspark wraps spark library in python so you can use python 
but built on Java so you don't see camelcase not get_or_create but getOrCreate function names
- Spark is a JVM library so most of the style is JAVA based 
- mind the blackslashes in code 
- stage when it is collect()
- Spark is managed by spark session so you create it 

```python
## Cross Join 
## bad practice filter it out before collect()
df.join(df, lit(1)== lit(1)).collect() 
# ERROR Executor: Exception in task 6.0 in stage 13.0 (TID 26)
# java.lang.OutOfMemoryError: Java heap space

df.join(df, lit(1)== lit(1)).take(5)  # works 
df.join(df, lit(1)== lit(1)).show(5) # cross join  
```

- With repartition, you're just reorganizing data into chunks, often based on a key, whereas a global sort (like DF.sort()) forces all data through a single executor to guarantee order, causing a double shuffle and major slowdowns at scale.
- stick to things like sortWithinPartitions after a repartition
    ```python 
    ## Repartitiom - you're essentially telling Spark to reshuffle your data into a new number of partitions, which can help balance the workload or prepare data for specific operations.
    # df is being split into 10 partitions based on the event_date column.

## At scale they will be very different 
## At scale they will be very different 

    ## At scale they will be very different 

    # it will look in the partition and sort locally 
    sorted = df.repartition(10, col("event_date")).sortWithinPartitions()
    sorted.explain()

    # Global sort of all the data - very slow 
    sorted_two = repartition(10, col("event_date"))\
                .sort(col(), col())
    sorted_two.explain()
    # extra exchange range partitioning line in the plan -- double shuffle 
    # read explain plan from bottom up
    # explain = sort in plan 
    ```

```sql
(

)
using ICEBERG
PARTITIONED by year(event_date);

```

- partition by date and there should be partitioning by dates 
- In iceberge after you write your tables out, you can query the metadata of the files, sum(file_size_in_bytes)
- Example of how if you have Low cardinality things togther then you get better partitioning - Run length encoding 
- when sorting data you want lowest cardinality first and then highest cardinality
- `sortWithinPartitions` also ties into writing data out efficiently. When writing sorted data (especially with low to high cardinality columns like event_date to host), you get better compression through run-length encoding, shrinking file sizes by 10-15%.
- When you use `sortWithinPartitions`, it doesn't create or change the number of partitions on its own. Instead, it operates on the existing partition structure of your DataFrame at the time the operation is called. This means the number of partitions remains the same as whatever it was before you applied sortWithinPartitions, unless you've explicitly repartitioned the data beforehand.
</details>

</details>  <!--  top spark basics closing -->



<details>
<summary> Advanced Spark</summary>

<details>
 <summary>  Spark Deployment Methods: Server vs. Notebooks </summary>
 
 - **Spark Server Overview**: Spark Server involves submitting jobs via the command line interface (CLI) using tools like spark-submit, where a Java class (often packaged in a JAR file) is executed. This method, used by companies like Airbnb, can be slower due to the time required to upload large JAR files with dependencies, sometimes taking several minutes just to initiate a job.

- **Spark Notebooks Overview**: Spark Notebooks provide an interactive environment with a persistent Spark session that users manually start and stop, offering a more hands-on approach for development and testing. However, they can be misleading as behaviors like caching in notebooks often don’t reflect production environments, leading to potential discrepancies.

- **Comparison of Session Management**: 
    - In Spark Server, the session runs only for the duration of the job, starting when submitted and terminating upon completion, which automates resource management.
    - In contrast, notebooks require manual termination of sessions, which can lead to resource lingering if not handled properly.

- **Pros and Cons of Each Method**: Spark Server is favored for development Zach because it mirrors production behavior, ensuring consistency when deploying jobs. Notebooks, while faster for iterative testing, are less reliable for production simulation, and both methods have trade-offs depending on the use case.
- **Risks with Notebooks in Production**: Using notebooks in production, especially on platforms like Databricks, poses risks since changes can be made on the fly and immediately affect live data without proper validation. Zach highlights this as dangerous, citing potential for bad data introduction from minor edits to filters or columns.
- **Importance of CI/CD for Notebooks**: Netflix (where notebook scheduling in production was pioneered), Zach stresses the need for a CI/CD process to manage notebook changes. Without checks and balances, there’s a high risk of errors slipping into production, and robust processes are essential to minimize inevitable mistakes.
- **Recommendation for Deployment**: Use Spark Server with spark-submit for development to ensure alignment with production behavior, reducing surprises during deployment. This approach is  more reliable for maintaining consistency across environments, despite slower submission times.
</details>

<details>
 <summary>  Performance Optimizations in Spark </summary>
 
 - Temporary view == CTE 
    - always get recomputed unless cached 
    - very big difference via persistence 
    - caching prevents Spark from recalculating the same data repeatedly, caching a Temporary View reused seven times cut a job’s duration from 3 hours to 10 minutes.
- Caching
    - Caching in Spark is a performance optimization technique used to store intermediate results of a DataFrame or Dataset in memory (or disk) so that they can be reused without recomputation.
    - only provides benefits when a dataset is accessed multiple times;
    - By default, calling `.cache()` on a DataFrame or Dataset stores the data `in memory`, fastest option since it avoids disk I/O
    - If a dataset is too large to fit in memory, Spark offers the option to cache to disk using `.persist()` with a storage level like `DISK_ONLY`
    - Materialized view == Disk == writing it out to the table - maintain a staging table instead
    - Disk caching is slower due to read/write operations and, the data is lost once the Spark job terminates, making it less practical for long-term use.
    - Instead of disk caching, write data to staging tables (e.g., using `write.mode(overwrite).saveAsTable()`), as these persist beyond the job’s lifecycle, aiding in debugging, backfills, and intermediate result analysis.
    - In notebook, cached data can skew performance perceptions since rerunning code with cached results appears faster than a production cold start would be. Call `.unpersist()` after caching to test true pipeline behavior.
- Caching vs. Broadcast Joins:  
    - **cached data remains partitioned across executors**, maintaining Spark’s distributed nature, while **broadcast joins ship an entire small dataset(1-2 GB) to every executor as a single partition.** Understanding this distinction helps in choosing between caching for general reuse and broadcasting for specific join optimizations, as both leverage memory but for different purposes.
    - if you have 100 GB for caching in 200 partition, each executor will get 2 GB so you can cache it.
- Broadcast Joins:
    - shift to all executors, no shuffle here 
    - Spark automatically uses a Broadcast Join if the smaller dataset is under a configurable size threshold, set by `default to 10MB` via the `spark.sql.autoBroadcastJoinThreshold` parameter.
    - broadcast dataframe `broadcast(df)` that will trigger broadcast join regardless of  size of dataframe.

- Question Spark Optimization 

1. Executor Memory Tuning: Executor memory shouldn’t be set to a high default like 16GB without justification, as it’s wasteful and often unnecessary unless the job demands it. Over-allocating resources, a common practice in big tech to avoid troubleshooting due to high engineer costs, is discouraged in favor of thoughtful allocation to minimize cloud waste.
2. Driver Memory Adjustments: Driver memory only needs tuning for specific operations like .collect() or complex jobs requiring significant driver-side processing, and shouldn’t be over-allocated by default. 
Careful consideration prevents unnecessary resource consumption, aligning with efficient cloud usage principles.
3. Shuffle Partitions Configuration: Shuffle partitions default to 200, but should be tuned based on data size, aiming for 100-200MB per partition for roughly uniform data (e.g., try 1000-3000 partitions for a 20GB output, and pick the winner, 50% lower and higher). Testing a range of values helps identify optimal throughput, as jobs vary in IO, network, or memory intensity.
4. Adaptive Query Execution (AQE): AQE is praised for automatically handling skewed datasets, reducing manual tuning efforts, but should only be enabled if skew is confirmed to avoid unnecessary overhead. This feature has alleviated much pain for data engineers dealing with data skew over the years, making it a lifesaver when appropriately applied.
5. Sorting Strategies: Global sorting with sort() is slow due to a full shuffle to a single partition and should be avoided, while sortWithinPartitions() sorts locally within partitions, offering faster performance. The latter still supports run-length encoding for compression, reducing data size and cloud costs without the heavy shuffle penalty.
4. Run-Length Encoding Benefits: Run-length encoding, used with Iceberg (Spark’s default file format), enhances compression when data is sorted effectively, as shown in labs where sorted data reduced volume. This efficiency lowers storage costs and speeds up queries, making sorting strategies critical for optimization.

</details>

<details>
 <summary>  User-Defined Functions (UDFs) and API Workflows </summary>

- UDF Performance in PySpark vs. Scala: 
    - PySpark UDFs historically suffered from `serialization(spark for python) - deserialization - serialize(python for spark) overhead` between Scala and Python, though Apache Arrow has largely mitigated this, aligning their performance closer to Scala UDFs except for aggregating functions.
    - Scala remains slightly faster for UDFs, but this advantage is niche since UDFs are rarely used in most pipelines.
    - UDAF (user defined aggregated function) - performance hit in pyspark, better in Scala, very rarely used though.
    - Dataset API - Scala spark is better, Scala and Java both compile to Java byte code, can do pure Scala functional data engineering.

- Niche Use of UDFs: UDFs are not common, appearing in perhaps 1 in 100 pipelines, so their performance impact shouldn’t heavily dictate language choice unless critical to the workload. For most users, this makes PySpark’s accessibility outweigh Scala’s marginal UDF efficiency gains.

- Dataset API Advantages in Scala: Lab examples highlight Scala’s Dataset API for its schema access and nullability constraints (using Option for nullable fields), enforcing data quality by failing on unexpected nulls if not modeled correctly. This strictness ensures pipelines catch issues early, unlike DataFrame or SQL APIs which handle nulls more leniently.

- Joins and Transformations in Dataset API: Dataset API joins allow explicit access to left and right sides with type-safe transformations, offering more control and clarity compared to DataFrame or SQL syntax. This makes complex operations easier to manage and debug, especially in large Scala pipelines.

- Mock Data Creation with Dataset API: Creating mock data is seamless in Dataset API since schemas are embedded, unlike DataFrame where separate structures might be needed, simplifying testing. Companies like Airbnb favor this API for its quality guarantees and ease of generating fake input data for pipeline validation.

- UDF Implementation Across APIs: Labs show UDFs in Dataset API as pure Scala functions, avoiding extra definitions required in DataFrame API, making them more integrated and less cumbersome. This direct approach in Scala enhances code readability and reduces overhead compared to DataFrame’s UDF syntax.
</details>


<details>
 <summary>  Spark APIs: DataFrame, Dataset, Spark SQL, and RDD </summary>

1. Spark SQL - most accessible API, ideal for teams with data scientists or multiple collaborators since it only requires SQL knowledge, lowering the barrier to entry.
2. DataFrame - DataFrame API sits in the middle, offering modularity and testability by allowing code to be broken into functions, making it suitable for long-term PySpark projects.
3. Dataset API - Exclusive to Scala, the Dataset API leans towards software engineering with strong schema enforcement, better null handling, and easier mock data creation for testing, recommended for long-haul Scala projects. It provides tight integration with pipeline schemas, enhancing data quality control through strict type safety.
Model into dataset API if values are going to be NULL.
4. RDD as a Lower-Level Option: RDD (Resilient Distributed Dataset) is mentioned as a lower-level API, less user-friendly compared to others, and not detailed extensively but noted for completeness. It’s typically used in scenarios requiring fine-grained control over data processing, though less common in modern Spark workflows.

- Null Handling Across APIs: Spark SQL and DataFrame `return null when encountering it without additional checks`, whereas Dataset API requires `explicit modeling of nullability`, failing loudly if unhandled nulls appear in non-nullable fields. This strictness in Dataset API aids in enforcing data quality by catching issues early.
- Choosing the Right API: Use Spark SQL for quick iterations with data scientists, DataFrame for long-term PySpark pipelines, and Dataset for robust Scala pipelines needing strict quality control. The decision hinges on whether the focus is collaboration, maintainability, or engineering precision.
</details>


<details>
 <summary>  File Formats and Persistence Strategies </summary>

1. Iceberg : Iceberg is `Spark’s default file format`, leveraging `run-length encoding for compression when data is sorted`, reducing storage and query costs. Effective sorting maximizes these benefits, making it a go-to for efficient data management.
2. Staging Tables for Persistence: Persistence via staging tables is preferred over disk caching, as tables retain data post-job for debugging and backfills, unlike temporary disk caches that vanish. This strategy ensures intermediate results are accessible, improving pipeline reliability and recovery options.
3. Avoiding Disk Persistence: Using .persist() for disk storage is discouraged since it’s equivalent to writing a table but without persistence beyond the job, wasting effort. Writing to a table with a schema (e.g., write.mode(overwrite).saveAsTable()) is a better practice for maintaining data integrity and usability.
</details>

<details>
 <summary>  Lab2  </summary>

### Scala 
- `case class Event` String vs Optional type - if its nullable then wrap it in Optional - enforce assumptions in your pipeline 
- val events: Dataset[Event] labelling the type - although it is inferred in scala
- join and`$` syntax in Scala spark 
- manage null - Use .get or coalesce - we are filtering out nulls beforehand - you get access to left and right side of join and you can map to the new schema in Dataset API 
- toUpperCase example - two examples of using udf   
- fake data creation is easier here 

### Caching 
- spylon kernel 
- user 1 to many devices 
- devices 1 to many users 
- agggregate at user and device level 
- text diff for plan comparison when `eventsAggregated` is cached 
- inmemorytablscan - read from mem = cached plan is more - one more step
- second time you will see the benefit
- `.cache(StorageLevel.DISK_ONLY)`  - better to write though
- .cache() == StorageLevel.MEMORY_ONLY

### Bucket JOIN 
- Loading data from csv files into iceberg tables 
- `SELECT * FROM demo.bootcamp.match_details_bucketed.files` - check your number of files 
- not bucketted data
    - matchesBucketed.createOrReplaceTempView("matches")
    - matchDetailsBucketed.createOrReplaceTempView("match_details")

- compare the joins between bucketted and non bucketted data 
    - `spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")` -- disabling broadcast join 
    - bucket join is only required when you have really large dataset, so it should 
    - Bucketted Data Join - sort merge join within the bucket - if you bucket things- you don't have to shuffle (no shuffle)- batch scan - bucketted scan - plan is really tidy 
    - more exchanges in non bucketted data Join 


</details>

</details> <!--  top advanced spark closing -->

<details>
<summary> Testing in Spark Jobs  </summary>

<details>
<summary> Bugs </summary>

### Where Quality Bugs Are Caught

1. In Development: `ideal scenario` where bugs are identified and fixed before deployment. It’s like the bug never existed since it doesn’t impact anyone outside the development phase. Catching bugs here saves time and avoids postmortems.
2. In Production (Staging): Bugs are caught during the "write-audit-publish" process, where data is written to a staging table, audited, and fails quality checks before reaching production tables. `Still better` than catching bugs in production, this can still be onerous due to false positives in data quality checks, which waste time for data engineering teams.
3. In Production (Live Tables): `worst-case scenario` where bugs bypass quality checks and appear in production. These are often discovered by data analysts noticing anomalies in dashboards or data, and sometimes they go unnoticed for weeks if the errors are subtle. This damages company trust and can lead to poor decision-making. Data can be behind. 


### How to Catch Bugs in Development

1. Unit Tests: 
    - These target individual components, like user-defined functions (UDFs) or specific functions in Spark (e.g., lookups). Unit tests are powerful for ensuring small pieces of logic work correctly, especially when integrating with external libraries. 
    - For instance, at Airbnb, Zach tested pipelines that called pricing libraries to ensure changes by other teams wouldn’t break their code.
    - Unit tests in CI/CD pipelines can block merges for others if they fail, enforcing accountability.
2. Integration Tests: 
    These test how different components of the pipeline work together, ensuring the overall flow is correct.
3. Additional Tools: 
    Using a linter to enforce coding standards is recommended. While it doesn’t catch bugs directly, it improves code readability, making it easier to spot issues and ensuring team consistency in coding style (e.g., spacing, variable naming).

### Catching Bugs in Production

1. Write-Audit-Publish: Data is written to a staging table with the same schema as production, quality checks are run, and only if they pass is the data moved to production. 
2. Signal Table Pattern: Mentioned as an alternative used by Facebook, though Zach finds it less effective. 

The worst situation is when bugs reach production and are flagged by data analysts or lead to bad decisions due to unnoticed errors. Relying on manual queries by analysts to catch bugs isn’t scalable or reliable—data engineers must take responsibility for quality.    

</details>


<details>
<summary> DE risks | DE vs SWE </summary>

1. Higher Consequences in Software Engineering:
     If a website like Facebook goes down, revenue loss is immediate and significant compared to a data pipeline failing, where stale data might be tolerable for a day or two. SWE often need to respond to issues at odd hours (e.g., 3 a.m.), while data engineers can often wait until regular hours.
2. Maturity of the Field: 
    Software engineering has been around for about 50 years, with established practices like test-driven development (TDD) and behavior-driven development (BDD), whereas data engineering is newer (10-15 years) and still adopting these practices.
3. Diverse Backgrounds in Data Engineering:
    Data engineers come from varied fields (software engineering, data analytics, economics), leading to inconsistent software engineering fundamentals compared to software engineers, who often have computer science degrees.


#### Rising Risks in Data Engineering

1. Impact on Revenue: At Airbnb, Zach worked on data feeding into the Smart Pricing algorithm, which directly affected a large chunk of revenue. Delays in data freshness could measurably reduce revenue, highlighting the need for timely, high-quality data. 
2. Impact on Experimentation: Data quality bugs can skew A/B test results, leading data scientists to draw incorrect conclusions about experiments.
3. Data-Driven Culture: As companies rely more on data for decision-making, poor data quality poses greater risks. Data engineers must elevate their standards to match their growing responsibility.

</details>

<details>
<summary> Why Organizations Miss the Mark on Data Quality </summary>

- Zach shares that in his first 18 months at Facebook, he didn’t write a single data quality check (unit test, integration test, or production check). Instead, issues were often caught by analysts noticing odd charts, leading to days of troubleshooting without adding permanent quality checks.
- There’s a trade-off between business velocity (answering questions quickly) and sustainability/quality.
- Business Velocity vs sustainability 
    - Data engineers to builders of “information highways,” not just query runners for analysts. Building high-quality, long-lasting infrastructure (like a highway) takes longer but pays off compared to quick, low-quality solutions (like a dirt road) - Depends on the strength of your leaders and how much you can push back.
- DE is engineering and not analytics


### Future of Data Engineering

1. Latency: 
    - Solved by moving from batch to streaming or micro-batch pipelines for near-real-time data (e.g., for fraud detection or dynamic pricing)
    - Streaming pipelines run 24/7, increasing the chance of issues compared to batch pipelines running briefly daily, thus requiring higher quality standards.
2. Quality: 
    - Solved using frameworks like Great Expectations, Amazon DQ, or Chisa (used in the lab) to test and prove data quality, moving beyond just writing SQL and dumping data into a lake.
3. Completeness: 
    - Becoming domain experts through experience and stakeholder communication to ensure data covers all necessary aspects.
4. Ease of Access/Usability: 
    - Going beyond tables and dashboards to `data products` and proper data modeling to improve usability.

### Adopting a Software Engineering Mindset
1. Code for Humans, Not Machines: Write readable code to ease troubleshooting, even if it’s slightly less efficient (e.g., avoid complex subqueries for minor performance gains).
2. Avoid Silent Failures: Silent bugs are the enemy. Use loud failures (e.g., throwing exceptions in Java with throw or in Python with raise) to crash programs visibly and alert engineers to issues. Custom exceptions (like DuplicateRecordException) can be created for specific cases.
3. Testing and CI/CD: Loud failures in testing are caught by CI/CD before deployment, preventing production issues.
4. Principles like DRY and YAGNI: DRY (Don’t Repeat Yourself) encourages encapsulating and reusing logic, while YAGNI (You Aren’t Gonna Need It) advises building only what’s needed now, not over-engineering upfront.
5. Efficiency: Care about data structures, algorithms, and Big O notation (e.g., understanding join operations and shuffling in Spark).
6. Design Docs: Use design specifications and reviews to catch errors early.

</details>



<details>
<summary> </summary>
</details>

</details> <!--  top Testing closing -->