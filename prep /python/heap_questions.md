### Patterns 
- single Heap
- two Heap (finding median)
- finding the k largest or smallest elements
- scheduling problems - manage which job runs next based on some criteria
- priority, ordering, or need quick access to extreme values (min or max)
- Stream of data

**Approach (Two Heaps)**:
  - Max-heap (`lower_half`) for smaller half; maintain max_heap containing max value of all min elements 
  - Min-heap (`upper_half`) for larger half; containing min value of max elements at top
  - Balance no. of elements: k odd → `lower_half` has (k+1)/2; k even → both k/2.
  - Add/remove elements as window slides (O(log k) per operation).
  - Median: k odd → top of larger heap; k even → average of tops.
  - **Time**: O((n - k + 1) * log k) for n elements.
    
### Challenges
  - Don’t support efficient removal of arbitrary elements (only the top)
  - No built-in support for decrease/increase-key or arbitrary delete;

#### Basic Operations
- Python’s `heapq` module implements a min-heap by default using a list.
- By default, heapq is min heap you can put -ve values to create max heap
  ```python
  import heapq as hq
  min_heap = []
  hq.heappush(min_heap, 1)
  min_heap[0] # gives 0th ele
  len(heap) # Size
  not heap  #empty
  ```
- **heappush(heap, value)**: Insert a new value into the heap, bubbling it up to maintain heap property. O(log n)
- **heappop(heap)**: Remove and return the smallest element (root), bubbling down to restore heap property. O(log n)
- **heapify(list)**: Transform a list into a heap in-place by bubbling down elements. O(n) - build heap 
- **heapreplace(heap, value)**: Pop the smallest element and push a new value in one operation, more efficient than separate pop and push. O(log n)
- **nlargest(k, iterable)**: Return the k largest elements from the iterable using a heap. O(n log k) for n elements.
- **nsmallest(k, iterable)**: Return the k smallest elements from the iterable using a heap. O(n log k) for n elements.
- **Peek (heap[0])**: View the smallest element (root) without removing it. O(1)

### Questions 
<details> 
  <summary>1. Maximum Capital (IPO Problem) with Heaps </summary>
  
  ```python
    def maximum_capital(c, k, capitals, profits):
      capital_min_heap = []
        for cap, prof in zip(capitals, profits):
            hq.heappush(capital_min_heap, (cap, prof))
        
        # Max-heap for profits (to pick highest profit among affordable projects)
        # Use negative profits since heapq is min-heap by default
        profit_max_heap = []
        
        # Select up to k projects
        for _ in range(k):
            # Move all affordable projects (capital <= c) to profit max-heap
            while capital_min_heap and capital_min_heap[0][0] <= c:
                cap, prof = hq.heappop(capital_min_heap)
                hq.heappush(profit_max_heap, (-prof, cap))
            
            # If no affordable projects are available, stop early
            if not profit_max_heap:
                break
            
            # Pick the project with max profit (negated back to positive)
            max_profit, _ = hq.heappop(profit_max_heap)
            c += -max_profit  # Add profit to capital (negate since we stored as negative)
        
        return c
  ```
  </details>
  <details> 
  <summary>2. Find Median from Data Stream </summary>
  
  ```python 
  class MedianOfStream:

    def __init__(self):
        self.max_heap_for_smallnum = [] # remember small nums in max heap, name accordingly 
        self.min_heap_for_largenum = []

    def insert_num(self, num):
        # first insert to small nums heap if it empty 
        # if incoming num is less than max of small nums then it will come small num heap 
        if not self.max_heap_for_smallnum or -self.max_heap_for_smallnum[0] >= num: # rem to insert negative values
            heappush(self.max_heap_for_smallnum, -num)
        else:
            heappush(self.min_heap_for_largenum, num)
        
        # balancing 
        # if maxheap (smaller numbers) has more than one element more than the min heap (larger numbers)
        if len(self.max_heap_for_smallnum) > len(self.min_heap_for_largenum) + 1:
            heappush(self.min_heap_for_largenum, -heappop(self.max_heap_for_smallnum))
        # if maxheap (smaller numbers) is less than minheap (larger values)
        elif len(self.max_heap_for_smallnum) < len(self.min_heap_for_largenum):
            heappush(self.max_heap_for_smallnum, -heappop(self.min_heap_for_largenum))

    def find_median(self):
        if len(self.max_heap_for_smallnum) == len(self.min_heap_for_largenum):

            # even number case, take the average of middle two elements
            # we divide both numbers by 2.0 to ensure we add two floating point numbers
            return -self.max_heap_for_smallnum[0] / 2.0 + self.min_heap_for_largenum[0] / 2.0

        # odd number case- max-heap will have one more element than the min-heap
        return -self.max_heap_for_smallnum[0] / 1.0
    
  ```
  </details>
