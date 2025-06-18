- Dictionary access is via [] or dict.get(key, 0); not by dot 
- dot is for class membership 
- :.2f for decimal manipulation 
- convert list to string `','.join(list_name)`
- Avg is not possible in List `sum(list)/len(list)` -- divide by zero - yes 
```python 
list1 = [1]
print(sum(list1)/(len(list1)) if list1 else 0)

try:
    print(sum(list1)/len(list1))
except ZeroDivisionError:
    print("list is empty")

from statistics import mean
print(mean(list1))                
```

```python
from collections import Counter 
from typing import Dict, List,  Optional #(typehinting)

print(list("36484"))
print(int("36484"))
```

- STRING = TUPLE= Immutable 
- LIST = Mutable 
- Just like with strings, if you want a different tuple, you have to create a new one, maybe by slicing or combining with other tuples.

- String Manipulation 
    - .isalnum()
    - .isupper()
    - .isdigit()
    - .isalpha()
    - c.lower() 

- `string.startswith(prefix[, start[, end]])`  The startswith() method checks if a string begins with a specified prefix. It returns True if the string starts with the specified value, and False otherwise.

```python
## Basic SLICING Syntax

#list[start:stop:step] stop is exclusive 

lst[-3:]    # Last three elements
lst[:-2]    # All except last two elements
lst[::2]    # Every second element
lst[::-1]   # Reverse the list")
lst[::-2]   # Every second element from end
```

### Sorting - O(n log n)
```python 
my_list.sort()              # Sorts in-place
my_list.sort(reverse=True)  # Sorts in descending order
my_list.sort(key=lambda x: abs(x))  # Sorts with key function
sorted(lst)                 # returns a new sorted list; creates a new list and leaves the original unchanged

freq_dict[item] = freq_dict.get(item, 0) + 1

float('-inf')
```