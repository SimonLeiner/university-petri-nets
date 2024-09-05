# Compositional Algorithm

You can model this as a search problem where each state represents a version of the Petri net after applying a transformation. The goal is to reach a state that matches the target Petri net.

`Breadth-First Search (BFS)` is best suited to explore all possible transformation sequences in the shortest number of steps.

# Core Algorithm Steps:

`Input:` Initial Petri net, target Petri net, set of allowed transformations.
- 1. For each transformation in the set, generate a new Petri net graph by applying the transformation.
- 2. Check if the newly generated Petri net is isomorphic to the target net. 

# Algorithmic Complexity:

- Time Complexity of `BFS=O(V+E)`, where V is the number of vertices (places and transitions) and E is the number of edges (arcs) in the Petri net graph. The total time complexity will be the number of explored states S, multiplied by the time it takes to perform the graph isomorphism check on each state: Total Time Complexity = `O(S * V^2 * E)`.

- `Search Space Complexity:` The number of possible transformations might be large, so you can use heuristics to guide the search, such as preferring transformations that bring the Petri net closer to the target structure.

- `Pruning:` To avoid redundant or cyclic transformations, you can use memoization or a visited set to track already-explored Petri nets and avoid revisiting them.

# Check if Graph is the wanted one: Graph Isomorphism Algorithms

- Tools such as `VF2 (Variable Forwarding 2)` algorithm can be used to check for graph isomorphism between the transformed Petri net and the target Petri net.
- This algorithm compares the structure (nodes and edges) of two graphs and determines whether they are isomorphic.
- For Petri nets, this means comparing places, transitions, and their interconnections (arcs) in both nets.
- For each state, we perform a graph isomorphism check to see if it matches the target net. If the size of the Petri nets (in terms of places, transitions, and arcs) is `V node`s and `E edges` the graph isomorphism check takes `O(V^2 * E)`.