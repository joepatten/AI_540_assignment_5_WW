CptS 540 Homework 5
Joe Patten

1. The agent does exactly what is asked (through the hw5 sheet). It moves around the world using a modified version of DFS. It explores unexplored nodes, and if it knows there is a wumpus about, it will avoid it. If all nodes around it are explored, it will backtrack to previous nodes, until it finds a node that has not been traveled.

2. It also uses logic to find out where the wumpus is (whether there be 3, 2, or 1 stench). The agent is fairly "aggressive". It may run into the wumpus on the first try. But subsequent tries it will not.

3. I save the path that the agent has gone, and eliminate loops while I go, so if the agent reaches gold, I already have a path without redundancies. Notice this might not be the opimal path (I implemented a version where I use greedy search one I knew where the gold was in order to find a more optimal path). However, I just did what the homework sheet specified.
