### Heaps: Quick Revision for Interviews

- A **heap** is a specialized binary tree data structure for managing priorities. 
- for quick access to the smallest or largest element, often used to implement priority queues.

#### What is a Heap?
- A complete binary tree (all levels filled except possibly the last, filled left to right) that satisfies the *heap property*.
- **Types**:
  - **Min Heap**: Node value ≤ children’s values; root is the smallest. Used to prioritize minimum values (e.g., earliest flight).
  - **Max Heap**: Node value ≥ children’s values; root is the largest. Used to prioritize maximum values (e.g., longest-waiting flight).
- Typically implemented as an array for efficiency (e.g., node at index `i` has left child at `2i+1`, right at `2i+2`).

#### When to Use a Heap?
- Implementing **priority queues** (e.g., task scheduling, flight priorities).
- Finding top K elements (e.g., most delayed flights).
- Algorithms like Dijkstra’s shortest path or Huffman coding.
- Best for dynamic data needing fast access to min/max without full sorting.

#### Time Complexity
- **Insert (Add element)**: O(log n) - Add at end, bubble up.
- **Extract Min/Max (Remove root)**: O(log n) - Replace root with last element, bubble down.
- **Peek (View root)**: O(1) - Root is always min/max.
- **Build Heap (from array)**: O(n) - Heapify from last non-leaf node.
- **Update Priority (Change value)**: O(log n) - Update and bubble up/down.

#### Bubble Up (Sift Up) in Heaps
- **Definition**: Process to restore heap property after insertion by moving a new element up the tree.
- **How it Works**:
  - Insert new element at the end (last position in array/tree).
  - Compare with parent; if out of order (smaller in min heap, larger in max heap), swap with parent.
  - Repeat until element is in correct position or reaches root.
- **Time Complexity**: O(log n) - Only traverses one path up the tree height.
- **Use Case**: Ensures heap property after every insert operation.

#### Bubble Down (Sift Down) in Heaps
- **Definition**: Process to restore heap property after extracting the root by moving an element down the tree.
- **How it Works**:
  - Replace root with last element in array, then remove the last element.
  - Compare root with children; swap with smaller child (min heap) or larger child (max heap) if out of order.
  - Repeat until element is in correct position or reaches a leaf.
- **Time Complexity**: O(log n) - Traverses down one path of tree height.
- **Use Case**: Ensures heap property after extract operations (e.g., removing min/max).

#### Why Heaps for Priority Queues?
- Priority queues retrieve elements by custom priority, not insertion order.
- Heaps ensure O(log n) for add/remove operations, much faster than sorted arrays (O(n) insert) or linked lists (O(n) find min/max).
- Perfect for dynamic priority tasks like flight scheduling.

### Heap Operations: Quick Revision

#### 1. Insert (Add Element)
- **Purpose**: Add new element, maintain heap property.
- **Process**: Add at end, bubble up (swap with parent if out of order) until correct spot.
- **Time**: O(log n)
- **Use**: Add to priority queue (e.g., new flight).

#### 2. Extract (Remove Root)
- **Purpose**: Remove/return root (min/max), restore property.
- **Process**: Replace root with last element, shrink size, bubble down (swap with smaller/larger child) until correct.
- **Time**: O(log n)
- **Use**: Process highest priority (e.g., earliest flight).

#### 3. Peek (View Root)
- **Purpose**: See root (min/max) without removing.
- **Process**: Access array[0].
- **Time**: O(1)
- **Use**: Check next priority (e.g., next flight).
 
#### 4. Build Heap (From Array) - Detailed
- **Purpose**: Convert an unsorted array into a valid heap (min or max).
- **Why Not Insert One by One?**: n Repeated inserts will take O(n log n); Build Heap is faster at O(n).
- **How it Works**:
  - Heap as array: node `i` has left child `2i+1`, right `2i+2`, parent `(i-1)/2`.
  - Start at last non-leaf node (index `n/2 - 1`, where `n` is array size), move to root (index 0).
  - For each node, "bubble down": swap with smallest child (min heap) or largest (max heap) if out of order, repeat until correct position.
  - Bottom-up ensures subtrees are valid before processing parents.
- **Time Complexity**: O(n)
  - Not O(n log n) despite bubble-down being O(log n) per node.
  - Most nodes are near bottom with short bubble-down paths (half are leaves, no work; quarter height 1, etc.).
  - Total work sums to ~2n comparisons/swaps, hence linear time.
- **Example (Min Heap)**: Array [4, 10, 3, 5, 1]
  - `n=5`, start at `5/2-1=1` (value 10); swap with child 1: [4, 1, 3, 5, 10].
  - Index 0 (4); swap with child 1: [1, 4, 3, 5, 10]. Done!
- **Use Case**: Initialize priority queue, prep for Heap Sort or Dijkstra’s algorithm.
- **Interview Tips**:
  - Explain starting at `n/2-1` (leaves trivial, bottom-up logic).
  - Know O(n) vs. O(n log n) intuition (node height distribution).
  - Practice small example; may need to code `heapify` (bubble-down).
  #### Condensed Pseudo-Code for Build Heap (Min Heap)
- **BuildHeap(array)**:
  - `n = length(array)`
  - For `i` from `(n/2 - 1)` downto `0`:
    - Call `BubbleDown(array, i, n)`
- **BubbleDown(array, index, size)**:
  - `smallest = index`
  - `left = 2*index + 1`, `right = 2*index + 2`
  - If `left < size` and `array[left] < array[smallest]`: `smallest = left`
  - If `right < size` and `array[right] < array[smallest]`: `smallest = right`
  - If `smallest != index`:
    - Swap `array[index]` with `array[smallest]`
    - Recurse `BubbleDown(array, smallest, size)`
- **Notes**: O(n) total time; for max heap, swap with largest child.
- **How to Explain**:
  - Half nodes are leaves (no work in Build Heap; start at non-leave level so pruned half leaves).
  - Of rest, most are near bottom (e.g., quarter of nodes have height 1, bubble-down is O(1)).
  - above it (one eighth of nodes at height 2,  bubble-down is O(2) and so on)
  - Few nodes near top (e.g., root) need full O(log n) swaps.
    
#### 5. Update Priority (Change Value)
- **Purpose**: Update element value, restore property.
- **Process**: Change value, bubble up or down based on violation.
- **Time**: O(log n)
- **Use**: Update priority for (e.g., flight delay).

#### Example
- Operations on small heaps (5-6 elements) to show inserts/extracts(add sketch)
- Explain bubble up/down clearly; they’re core to heap maintenance.
  
