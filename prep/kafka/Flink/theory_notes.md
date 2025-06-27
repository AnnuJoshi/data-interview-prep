<details>
<summary> What is a streaming pipeline ? </summary>

- Processes data in a low latency way, intra-day (more than once a day). Most pipelines are daily pipelines run (5-7 UTC). 
- Real Time vs streaming can be different for people - always clarify. Most time they need low latency batch pipeline. Ask what they are looking for? or when do you need the data refreshed? SLA ?

1. Near Real-time (Microbatch) - data is process in batches, every few minutes (Spark structured streaming)
2. Streaming(or continuous) - like a river, data is processes as it is generated (Flink)



#### Should you use Streaming ?
1. Team Skill Set
    - Let's say you team is good with spark in micro batch pipelines (15 mins refresh)
    - One member start doing it - became island, get atleast 3-4 members on team to learn it
2. What is the incremental benefit of reduced latency?
    - actual impact that will be there - we can give them in 2-3 mins - security team can benefit from this 
3. Homogeneity of Pipelines
    - Uber uses Kappa Architecture - streaming only, why will they introduce a new batch pipeline? 
4. Understand Trade off between 
    - daily batch 
    - hourly batch
    - microbatch
    - streaming 
5. Where we will do Data Quality?
    - very hard in streaming, there are no point where you can put in DQ and stop the pipeline 

#### Streaming only usecases (if not then unusable products)
1. Detecting fraud 
2. High frequency Trading 
3. Sports Analytics - stats has to be real time 

###### Gray Area Usecases 
1. Data is served to customer - trade off of latency
2. Master data latency 
    - FB example where every row = notifications event data - can be duplicated because you can click on a notification multiple times. 
    - For deduping - had to hold everything in memory, needed 40 TB of RAM - moved to microbatch
    - Earlier it was 9AM UTC but after microbatch it was delivered at 1AM UTC 
- Most gray area use cases can be solved with Microbatch 
- yesterday's data at 9 AM is good enough for MOST analytics usecases - business don't make decisions very fast.

#### Some other points 
- if you drive more, you gonna crash more 
- Streaming Pipelines are running 24/7 but batch pipelines are running 2-3 hours a day so streaming pipelines are likely to fail more 
- they act like servers, it runs all the time, you need to have more unit and integration test, hard to get DQ in streaming.

![stream_batch](../../../resources/ezachly_community_bootcamp/images/stream_batch_contin.png
)

#### Realtime is a myth!
- because there is Network time 
- you will have milli seconds of latency from event generation to Kafka then Flink needs to pick it up (another 100 ms - 1 secs) and then Flink needs to write it to a sink, if flink has to do aggregations then it can take couple of minutes - if only enrinchments then it can be quick -- then there is latency on writing to postgress or Kafka Queue. 
- Kafka -> Flink -> Sink -> Alerting (couple of minutes) 
- not instanteneous, you can get to order of single digit seconds 

</details>


<details>
<summary> Structure of Streaming Pipeline  </summary>

#### Sources (QUEUEs)
1. Kafka 
- 
2. Rabbit 
- pub sub is easier 
- less throughput 

#### Dimensional Source (side inputs)
- denormalization of fact data from different tables 
- Google flink side inputs - for enriching the events data 
- refreshes on cadence - 3 hours 

#### Compute Engines 
- Flink (windows, watermarking, out of order)
- Structured Streaming Spark 
- they make sense of the data that comes from the stream - crunching of the data 

#### Destination
- where is the data going 
- Another Kafka topic
- hive metastore - overriding the partition was not allowing
- datalake (iceberg) - allowed overriding, append is allowed
- Postgres

#### Challenges 
1. Out of order events - Latency b/w data generation and landing in Kafka - data that was generated before land after the data, that was generated after i.e. data landing not in right order 
    - How does Flink deal with Out of order events? 
    1. Watermarking 
    - In event stream in flink you can specify watermark - there are no events that are later than the watermark - looks at event time everything within 15 sec can be out of order but everything at 16th sec will be ordered. Flink will also fix that 15 sec ordering for you.
2. Late arriving data - not to worry in batch but issues around midnight, flink manage it 
    - How late is too late? 5 min or 10 min 
    - Out of order is also late arriving(small amount of data) - similar for watermarking 
3. Recovering from failures - you need to reset it, the longer you wait the bigger the issue
    - batch is different
    - Checkpointing in Flink, can be n number of secs, where to read from and write to 
    - Offsets - Kafka has offests 
        - earliest (read everything in kafka)
        - latest (only read new incoming data)
        - Specific timestamp
    - checkpoint (internal to Flink, internal Flink binary)
    - Savepoints (more like a csv file, other systems can also use them)

