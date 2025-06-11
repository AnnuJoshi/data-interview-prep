<details>
<summary>  Maximum Concurrent Deliveries (Sweep-Line Algorithm) </summary>

```python 
/* A courier can carry at most one active delivery at a time.
You are given a list of deliveries, each defined by a start timestamp (pickup) and an end timestamp (drop-off). Determine the maximum number of simultaneous active deliveries across all couriers.

Input(standard-in):

n # integer, 1 ≤ n ≤ 2*10^5
n lines follow: start_iso   end_iso

Example
5
2025-06-11T10:00:00 2025-06-11T10:25:00
2025-06-11T10:05:00 2025-06-11T10:30:00
2025-06-11T10:15:00 2025-06-11T10:45:00
2025-06-11T11:00:00 2025-06-11T11:20:00
2025-06-11T11:05:00 2025-06-11T11:15:00

Output (standard-out):
3
Explanation: Between 10:15 and 10:25 there are three overlapping deliveries.

Constraints & Tips
• ISO timestamps can be parsed with datetime.fromisoformat.
• O(n log n) expected; think sweep-line / line-sweep with event sorting (+1 at start, −1 at end).
*/



def sweep_line(n, arr_time):
    array_time = [(t.split()) for t in arr_time]
    array_time = [(datetime.fromisoformat(t[0])::time), datetime.fromisoformat(t[1])::time)) for t in array_time]
    array_time.sort()
    
    start_time = array_time[0][0]
    end_time = array_time[0][1]
    max_concurrent = 0
    count = 1
    for i in range(1, len(array_time)):
        new_start , new_end = array_time[i]
        if new_start <  end_time:
            count += 1
        else:
            start_time = new_start
            end_time = new_end
            if count > max_concurrent:
                max_concurrent = count 
                count = 1 
    if count > max_concurrent:
        max_concurrent = count 
     
    return max_concurrent
```
Why the Sweep Line Fits ?\
    For every moment, we need to know, how many intervals overlap that moment and keep track of the maximum. That is exactly the textbook use case for a sweep line.

    Why we attach “+1” to a start-time and “−1” to an end-time?
    
    Picture a cashier holding a simple click-counter:
    • Every time a delivery begins, she clicks “up” once ( +1 ).
    • Every time a delivery finishes, she clicks “down” once ( −1 ).

    At any clock-tick, the display shows `current_up_clicks − current_down_clicks` which is exactly “how many deliveries are out on the road right now”.
   
    Logic:
    1. Turn each interval ⟨start, end⟩ into two events: • (start, +1) ➜ “someone just walked in” (end, −1)  ➜ “someone just walked out”
    2. Sort the events by time, so we visit them in the order they actually happen.
    3. Walk through the timeline once, keeping a single integer active:
    active = 0
    max_active = 0
    for time, delta in events:   # delta is +1 or -1
        active += delta          # click up or down
        max_active = max(max_active, active)
    • When delta = +1, active goes up by one.
    • When delta = −1, active goes down by one. The highest value ever reached is the answer.

Correct Solution 
```python 
from datetime import datetime 

def calculate_max(deliveries):
    events = []
    for s, e in deliveries:
        start = datetime.fromisoformat(s)
        end   = datetime.fromisoformat(e)
        events.append((start,  1))
        events.append((end,   -1))
    
    # Rem : Sort by time; on ties process +1 before -1 
    # Assuming Closed start, Open end [) ; python sort by asc 
    # if Closed start, Closed end [] then no need; as we want to process end (-1 first)
    events.sort(key=lambda e: (e[0], -e[1]))
    
    active_deliveries = max_active_deliveries = 0
    for _, delta in events:
        active_deliveries += delta
        max_active_deliveries = max(max_active_deliveries, active_deliveries)

    return max_active_deliveries
```