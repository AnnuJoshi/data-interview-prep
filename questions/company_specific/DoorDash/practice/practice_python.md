<details>
<summary>Maximum Concurrent Deliveries (Sweep-Line Algorithm) </summary>

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
</details>

<details>
<summary> Move Zeros Back (5 min) </summary>

```python 
def move_zeros_to_end(array):
    if not array:
        return array  # Handle empty array explicitly

    current = 0
    last_swap = len(array) - 1

    while current <= last_swap:
        if array[current] == 0:
            # Swap zero with element at last_swap
            array[current], array[last_swap] = array[last_swap], array[current]
            last_swap -= 1
            # Skip any zeros at last_swap to ensure we swap with a non-zero if possible
            while last_swap >= current and array[last_swap] == 0:
                last_swap -= 1
        else:
            current += 1

    return array

# Alternatively 
def move_zeros_back(array):
    """
    Moves all zeros to the end of the array while maintaining the order of non-zero elements (bringing them up)
    i is always moving but non_zero_position only moves if a non zero value is there
    """
    non_zero_pos = 0
    for i in range(len(array)):
        if array[i] != 0:
            array[non_zero_pos], array[i] = array[i], array[non_zero_pos]
            non_zero_pos += 1
    return array

```

</details>

<details>
<summary>Recency Weighted Salaries(2 min) </summary>

```python 
def recency_weighted_salaries(previous_salaries):
    if not previous_salaries:
        return 0.0  # Handle empty input by returning 0.0

    weighted_salaries = [(i + 1) * salary for i, salary in enumerate(previous_salaries)]
    
    # Sum of weights: 1 + 2 + ... + n = n*(n+1)/2
    n = len(previous_salaries)
    total_weights = (n * (n + 1)) // 2
    
    weighted_average = sum(weighted_salaries) / total_weights
    return round(weighted_average, 2)
```
</details>

<details>
<summary>1200. Minimum Absolute Difference (5 Min)</summary>

```python 
def min_distance(test_input):
    if len(test_input) < 2:
        return 0, []  # Handle edge case: less than 2 elements
    
    test_input.sort()  
    min_dist = float('inf')
    
    for i in range(len(test_input) - 1):
        current_dist = test_input[i + 1] - test_input[i]
        if current_dist < min_dist:
            min_dist = current_dist
  
    result = []
    for i in range(len(test_input) - 1):
        if test_input[i + 1] - test_input[i] == min_dist:
            result.append([test_input[i], test_input[i + 1]])
    
    return result
```
</details>

<details>
<summary> Scrambled Tickets (12 min)</summary>

```python 

# flights = [
#     ['Chennai', 'Bangalore'], 
#     ['Bombay', 'Delhi'], 
#     ['Goa', 'Chennai'], 
#     ['Delhi', 'Goa'], 
#     ['Bangalore', 'Beijing']
# ]

def plan_trip(flights):
    
    src_dest_map = {}
   
    # Count occurrences of each city (as source or destination)
    count_dict = {}
    for src, dest in flights: # directly unpack flights 
        src_dest_map[src] = dest
        count_dict[src] = count_dict.get(src, 0) + 1  #Please use .get() 
        count_dict[dest] = count_dict.get(dest, 0) + 1
    
    # Find the starting city: it should appear only once in count_dict
    # and must be a source (i.e., in src_dest_map)
    start_trip = None
    for city in count_dict:
        if count_dict[city] == 1 and city in src_dest_map:
            start_trip = city
            break
    
    #Remember to check this - If no start is found, return empty or handle error (for simplicity, assume valid input)
    if start_trip is None:
        return []

    # list.pop(ele) is wrong because pop() on a list expects an index, not a value. Use remove() or rethink the logic   
    
    # Build the result list by following the source-to-destination mapping
    result = []
    current = start_trip
    while current in src_dest_map:
        next_city = src_dest_map[current]
        result.append([current, next_city])
        current = next_city
    
    return result

```
</details>


<details>
<summary> Generate a dictionary from two nested lists, handling duplicates or missing values. </summary>

```python 
def create_dict_from_nested_lists(keys_list, values_list):
    result_dict = {}
    # Get the minimum length to avoid index out of range
    min_length = min(len(keys_list), len(values_list))
    
    for i in range(min_length):
        key = keys_list[i]
        value = values_list[i]
        # Handle nested structure by flattening if necessary
        if isinstance(key, list):   # REM
            key = tuple(key)  # # REM Convert nested list to tuple to make it hashable
        if isinstance(value, list):
            value = tuple(value)
        result_dict[key] = value
        
        #REM:
        # Result[key] = Result.get(key, []).append(value) is incorrect 
        # append() method modifies the list in place and returns None, so this line actually sets Result[key] to None
        
        #temp = Result.get(key, [])
        #temp.append(value) 
        #Result[key] = temp
    return result_dict
```
</details>

<details>
<summary> 2 Sum  (10 min)</summary>

- Missed reading question properly had to return indexes, was returning numbers 
- using abs for no reason it was not required 
- took too long :((\

```python 
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        store = {}
        for i in range(len(nums)):
            if target - nums[i] in store:
                return [i, store[target - nums[i]]]
            else:
                store[nums[i]] = i
```

</details>
<details>
<summary> Write a function that takes n number of dice/die and returns all possible permutations of result.<br>
For example, when you have n=2 dice, we want to return: [(1,1), (1,2),(1,3)...(6,5),(6,6)] </summary>

https://leetcode.com/discuss/post/1515046/doordash-data-eng-tech-phone-screen-by-a-wgmq/

```python
#(i,) is a single-element tuple containing the value i
# The comma after i is important because it tells Python this is a tuple
# + operator, when used with tuples, concatenates them. 
# So if i=1 and perm=(2,), then (1,) + (2,) results in (1, 2).

def return_dice_permutation(n):
    if n <= 0:
        return []        # return empty list not 0 
    if n == 1:           # python is == 
        return [(i,) for i in range(1,7)]  

    prev_perm = return_dice_permutation(n - 1)
    result = []
    for i in range(1, 7):
        for perm in prev_perm:
            result.append((i,) + perm) 
```
</details>

<details>
<summary>13. Comvert from Roman to INT (15 min) </summary>

```python 
# REM to read question properly 
# it is very easy just REM you need to check if they are in order or not
'''
Each symbol adds its own value, except for when a smaller valued symbol is before a larger valued symbol.
In those cases, instead of adding both symbols to the total, we need to subtract the large from the small.
'''
def romanToInt(self, s):
        """
        :type s: str
        :rtype: int
        """
        values= {
        "I": 1,
        "V": 5,
        "X": 10,
        "L": 50,
        "C": 100,
        "D": 500,
        "M": 1000,
        }
        total = 0 
        i = 0 
        while i < len(s):
            if i+1 < len(s) and values[s[i+1]] > values[s[i]]:
                total += values[s[i+1]] - values[s[i]]
                i += 2
            else:
                total += values[s[i]]
                i += 1

        return total
```
</details>