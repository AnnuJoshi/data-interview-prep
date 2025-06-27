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
2. What Benefit 
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

</details>




