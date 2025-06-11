<details> 
  <summary> 678. Valid Parenthesis String
  </summary>

  [leetcode link](https://leetcode.com/problems/valid-parenthesis-string/description/)
  ```python
  def checkValidString(self, s: str) -> bool:
        # greedy approach
        # First pass: left to right, treat * as (
        # check if can not have too many )
        balance = 0
        for char in s:
            if char in '(*':
                balance += 1
            else:  # char == ')'
                balance -= 1
                if balance < 0:  # too many ) even when all *s are trying to balance
                    return False

        # Second pass: right to left, treat * as )
        balance = 0
        for char in reversed(s):
            if char in ')*':
                balance += 1
            else:  # char == '('
                balance -= 1
                if balance < 0:
                    return False
        return True
  ```


