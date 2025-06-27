<details>
<summary> What is a streaming pipeline ? </summary>

- Processes data in a low latency way 
- intra-day (more than once a day)
- most pipelines are daily pipelines run (5-7 UTC)

- Near Real-time (Microbatch) - data is process in batches, every few minutes (Spark structured streaming)
- Streaming(or continuous) - like a river, data is processes as it is generated (Flink)
- Real Time vs streaming can be different for people - always clarify 
- Most time they need low latency batch pipeline is what they are looking for - when do you need the data refreshed ? SLA ?

#### Should you use Streaming ?
- Let's say you team is good with spark in micro batch pipelines (15 mins refresh)
- One member start doing it - became island, get atleast 3-4 members on team to learn it
- Benefit (or actual impact that will be there) - we can give them in 2-3 mins - security team can benefit from this 

- Uber Kappa Architecture - streaming only 
Trade off 
- daily batch 
- hourly batch




</details>




