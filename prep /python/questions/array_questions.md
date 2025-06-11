<details> 
  <summary>121. Best Time to Buy and Sell Stock (buy and sell different day) </summary>
  
  ```python
    class Solution:
        def maxProfit(self, prices: List[int]) -> int:
            min_price = float("inf")
            max_profit = 0
            for i in range(len(prices)):
                if prices[i] < min_price:
                    min_price = prices[i]
                elif prices[i] - min_price > max_profit:
                    max_profit = prices[i] - min_price 
            return max_profit
  ```  

<details> 
  <summary> 122. Best Time to Buy and Sell Stock II (buy and sell same day)</summary>

  #### Key Insight 
  - Capture EVERY upward movement = Maximum profit
  - Why Greedy Works?
    - Any profit sequence can be broken down into consecutive day gains
    - Example: Buy at 1, sell at 5 = (1→2) + (2→3) + (3→4) + (4→5)
    - Missing any upward move = suboptimal

  - Time:  O(n) - one pass
  - Space: O(1) - no extra storage
  ```python
  class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        max_profit = 0
        for i in range(len(prices) - 1):
            if prices[i + 1] > prices[i]:
                max_profit += prices[i + 1] - prices[i]
        return max_profit
  ```

<details>
  <summary> </summary>