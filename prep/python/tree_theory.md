## Trees
**Definition**: A tree is an undirected, acyclic graph with a hierarchical, branching structure.\
**Nonlinear Nature**: Unlike arrays or lists, elements are not sequential but organized in branches.

## Time Complexity for Operations

**Search/Insert in Balanced Trees**: Typically O(log n), where n is the number of elements, due to halving search space.\
**Worst Case (Unbalanced)**: Degrades to O(n) if the tree is skewed, emphasizing the need for balance.

## Tree Traversal with Depth-First Search (DFS)

**DFS Overview**: Explores as far as possible along a branch before backtracking, visiting each node once in O(n) time.\
**Traversal Types**: Includes preorder (root, left, right), inorder (left, root, right), and postorder (left, right, root).\
**Generalization**: These traversals apply to m-ary trees (multiple children per node) by defining a consistent visit order.

