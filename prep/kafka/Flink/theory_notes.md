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

![stream_batch](../../../resources/ezachly_community_bootcamp/images/flink/stream_batch_contin.png
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
</details>

<details>
<summary> How it works - Details into Architecture? <summary>


![stream_batch](../../../resources/ezachly_community_bootcamp/images/flink/streaming_architecture.png
)
Example of streaming set for the lab - in which every user request on the webpage is sent to Kafka Server.

- HTTP Interceptor 
    ```python 
    def send_message_to_kafka():
        pass

    def create_api_event_middle_ware(request, response, next):
        # sits between user and server 
        should_be_logged= not if request.hostname.contains("localhost") and request.url
        event = {
            "url" : request.url,
            "referral": request.referral,
            "user_agent": request.user_agent,
            "event_time": date()
        }
        
        # not from local host
        if should_be_logged:
            send_message_to_kafka(..event)
            _next()      # passes the request to servver 
        else:
            ## passes the request to server anyway 

    topic = " "
    events = {} # object that you will write 
    def producer():
        # Send the data to kafka 
        print("message send successfully")

    ```

### Data Products 
- They will need to have a closed loop system, where feedback from user is shown back to them. 
- Web Sockets 
    - When you are build a website,client initiates a request - so client is asking for more data from server, this is how usually HTTP works
    - For Two-way communication between a client (like a web browser) and a server over a single, long-lived connection. 
    - Super useful for applications that need instant updates, like chat apps, live sports scores, or collaborative tools.
    - When a WebSocket connection is established, it starts with a handshake over HTTP. The client sends a special request to the server asking to upgrade the connection to a WebSocket, and if the server agrees, they switch protocols. From there, the connection stays open, and both the client and server can push messages back and forth as needed.
    - One thing to note is that since the connection stays open, both the client and server need to handle things like timeouts or reconnection logic if something goes wrong.

##### The big competing architectures (Very Imp Questions at Interview)
1. Lambda 
    - Optimize for Latency and correctness 
    - batch and streaming that both write the same data, batch pipeline is for backup, double code 
    - Pain is double codebase
    - Easy to insert data quality checks on batch side 
2. Kappa Architecture 
    - You can just use streaming - For eg, in Flink you can switch from streaming to batch 
    - Can be painful when you have to read a lot of history - backfill is painful - you have to read things sequentially 
    - Netflix - Iceberg is changing that - FLink can dump to iceberg - and you can backfill with partitions - you can append - Kafka has lines of data 
    - Netflix is trying to move from Lambda to Kappa Architecture 
    - Uber uses Kappa - they are 100% streaming 
    - Delta Lake, Hudi, iceberg are making this architecture more viable


#### Flink UDFs
- UDFs generally speaking will not perform as well as built in functions
- Python UDFs are going to be even less performant than Java or Scala, since they need a separate process as python executes it, so we need to get out of Java, process in python and pass it back to Java - extra serialisation and deserialisation. 

#### Windowing in Flink 
1. Data Driven Window 
    - count
        - This window will be open until we see `n` number of events 
        - Open on first event 
        - window per user == partition by in SQL == key by in Flink
        - number of events may never come, so you need a timeout to close the window, if n is never met
        - Powerful for funnel analytics 
        - Notifications funnel -> generated -> sent -> delivered -> open -> clicked -> downstream action = 7 events (fixed events) not gonna wait for days 

2. Time Driven Window 
    - Tumbling 
        - similar to hourly data in batch - fixed between a window 
        - fixed size 
        - no overlap 
        - Great for chunking data
        - commonly used 
    - Sliding 
        - fixed width but has overlap E.g. from 1-2pm then 1.30 - 2.30pm => duplicates 
        - find the window that has the most data 
        - can find peak time  12-1 1-2 spike at 
        - processing the midnight boundaries - double counting
        - starts at 11.58pm and goes it 12.02am 4 min session do they count as daily active on both days and not very long 
        - What if we pick UTC ? you can change the number of DAU by 7%, people had short session around midnight
    - Session
        - User specific, window starts at your first event and window will last until there is gap in your data no data till 20 min. How users are using your app ?

#### Allowed Lateness and Watermarking 
- If late in order of 
    - sec then watermarks
    - mins then allowed lateness

1. Watermarks
    - for managing event-time processing in Flink, which is the time when an event actually occurred, as opposed to the time it is processed (processing time) or ingested by the system (ingestion time)
    - Events often arrive out of order due to network delays, Watermarks help Flink track the progress of event time and decide when to stop waiting for earlier events.
    - essentially a special marker or metadata element inserted into the data stream with a timestamp
    - When a watermark with timestamp `t` is emitted, it signals that the system believes all events with timestamps less than or equal to `t` have been processed, and no further events with earlier timestamps are expected
    - This allows Flink to trigger computations, such as window calculations, without waiting indefinitely for late data.
    1. `Bounded Out-of-Orderness`, where watermarks are generated based on a maximum expected delay (e.g., 5 seconds), meaning the watermark is set as the latest event timestamp minus this delay. 
    2. `Punctuated Watermarking` - watermarks are generated based on specific events or conditions, offering more control for irregular streams.
2. Allowed Lateness
    - Default is set to 0, meaning late events are dropped or sent to a side output unless specified otherwise 
    - Allows for reprocessing of events that fall within the late window 
    - CAUTION: Will generate/ merge with other record  
    - Deals with events arriving after the watermark has passed their event time, i.e., late events
    - NOTE: While watermarks define when the system considers a time window "complete" and triggers computations, allowed lateness provides a grace period during which late events can still be processed and contribute to the results, rather than being discarded immediately.
    - For instance, if a window ends at time t and the watermark advances past t, events with timestamps within the allowed lateness period (e.g., 5 seconds after t) can still cause the window function to be recalculated, often referred to as a "late firing."
    - Flink supports side outputs to collect late events for separate processing if they exceed the allowed lateness threshold, ensuring no data is lost even if it can't update the main results.

3. Key Difference - Watermarks are a proactive mechanism to track event-time progress and decide when to initially close a window or trigger computations, based on the assumption that earlier events are unlikely to arrive. Allowed lateness, on the other hand, is a reactive mechanism applied after the watermark, allowing a window to remain open for a bit longer to accommodate late events and update results if necessary.