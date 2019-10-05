# PyAgent.py

from random import randint
import Action
import Orientation
from operator import mul
import time
    
class WorldState:
    def __init__(self):
        self.agentLocation = [1,1]
        self.agentOrientation = Orientation.RIGHT
        self.agentHasArrow = True
        self.agentHasGold = False
    
class Agent:
    def __init__(self):
        self.worldState = WorldState()
        self.previousAction = Action.CLIMB
        self.actionList = []
    
    def Initialize(self):
        self.worldState.agentLocation = [1,1]
        self.worldState.agentOrientation = Orientation.RIGHT
        self.worldState.agentHasArrow = True
        self.worldState.agentHasGold = False
        self.orientation_move = {0:[1,0], 1:[0,1], 2:[-1,0], 3:[0,-1]}
        self.previousAction = Action.CLIMB
        self.actionList = []
        track.wumpus_location = track.next_location
        
        self.old_path = track.path[1:]
        track.path = []
        if track.gold_location:
            self.old_path = track.gold_path[1:]
    
    def Process(self, percept):
        #time.sleep(.2)
        self.UpdateState(percept)
        # use logic to find wumpus (if possible)
        self.check_stenches()
        if (not self.actionList):
            if (percept['Glitter']):
                self.actionList.append(Action.GRAB)
                track.gold_location = self.worldState.agentLocation
                track.gold_path = track.path + [self.worldState.agentLocation]

            elif (self.worldState.agentHasGold and (self.worldState.agentLocation == [1,1])): # Rule 3b
                self.actionList.append(Action.CLIMB)

            elif (percept['Bump']):
                self.Move(percept['Bump'])
                self.actionList.append(1)
                track.path = track.path[:-1]
            
            else: 
                if (percept['Stench']):
                    if self.worldState.agentLocation not in track.stenches:
                        track.stenches.append(self.worldState.agentLocation)
                        if not track.wumpus_location:
                            self.actionList.append(1)
                            self.actionList.append(1)
                            self.actionList.append(Action.GOFORWARD)
                            track.path = track.path[:-1]
                            #bracktrack once
                            #track.path
                
                if len(self.old_path) > 0:
                    next_loc = self.old_path[0]
                    next_move = self.get_move(next_loc)

                    if self.orientation_move[self.worldState.agentOrientation] == next_move:
                        self.actionList.append(Action.GOFORWARD)
                        track.path.append(self.worldState.agentLocation)
                        self.old_path = self.old_path[1:]
                    else:
                        self.minimal_turn(next_move)              
                
                #if have gold, follow path back to start
                elif track.path and self.worldState.agentHasGold:
                    next_loc = track.path[-1]
                    next_move = self.get_move(next_loc)

                    if self.orientation_move[self.worldState.agentOrientation] == next_move:
                        self.actionList.append(Action.GOFORWARD)
                        track.path = track.path[:-1]
                    else:
                        self.minimal_turn(next_move)                       

                else:
                    # uninformed search
                    track.next_location = self.add_vectors(self.worldState.agentLocation,self.orientation_move[self.worldState.agentOrientation])
                    
                    #if we are about to run into a wumpus, then pick another route
                    if track.next_location == track.wumpus_location or percept['Bump']:
                        self.actionList.append(1)
                    elif track.next_location in (track.explored):
                        potential_moves = self.get_all_moves()
                        # all potential are explored go to previous path
                        if len(potential_moves) == 0:
                            #turn and then goforward to previous location in path
                            previous_location = track.path[-1]
                            next_move = self.add_vectors(previous_location, self.worldState.agentLocation, negative=True)
                            self.minimal_turn(next_move) 
                            
                            self.actionList.append(Action.GOFORWARD)
                            track.path = track.path[:-1]
                        else: 
                            # turn left until heading toward unexplored
                            self.actionList.append(1)
                    else:
                        # if no wumpus and we are exploring in unexplored, go ahead!
                        self.actionList.append(Action.GOFORWARD)
                        track.path.append(self.worldState.agentLocation)

        action = self.actionList.pop(0)
        self.previousAction = action
        return action

    def minimal_turn(self, next_move):
        new_direction = self.get_direction(next_move)
        turns = self.get_turns(new_direction) % 4
        if turns <= 2:
            for _ in range(turns):
                self.actionList.append(2) #turn right
        else:
            for _ in range(4 - turns):
                self.actionList.append(1) 

    def get_turns(self, new_direction):
        return self.worldState.agentOrientation - new_direction

    def get_direction(self, new_move):
        for k,v in self.orientation_move.items():
            if v == new_move:
                return k

    def get_all_moves(self):
        potential_moves = []
        for k in self.orientation_move:
            potential_move = self.add_vectors(self.orientation_move[k], self.worldState.agentLocation)
            if potential_move not in track.explored and potential_move != track.wumpus_location:
                potential_moves.append(self.orientation_move[k])
        return potential_moves
    
    def UpdateState(self, percept):
        currentOrientation = self.worldState.agentOrientation
        if (self.previousAction == Action.GOFORWARD):
            if (not percept['Bump']):
                self.Move(percept['Bump'])
        if (self.previousAction == Action.TURNLEFT):
            self.worldState.agentOrientation = (currentOrientation + 1) % 4
        if (self.previousAction == Action.TURNRIGHT):
            currentOrientation -= 1
            if (currentOrientation < 0):
                currentOrientation = 3
            self.worldState.agentOrientation = currentOrientation
        if (self.previousAction == Action.GRAB):
            self.worldState.agentHasGold = True # Only GRAB when there's gold
        if (self.previousAction == Action.SHOOT):
            self.worldState.agentHasArrow = False
        # Nothing to do for CLIMB

    def negative_vector(self, vec):
        return [-v for v in vec]

    def add_vectors(self, vec1, vec2, negative=False):
        if negative:
            vec2 = self.negative_vector(vec2)
        return [v1 + v2 for v1,v2 in zip(vec1, vec2)]

    def get_move(self, new_loc):
        # get next move from a PATH
        neg_current_loc = self.negative_vector(self.worldState.agentLocation)
        next_move = self.add_vectors(new_loc, neg_current_loc)
        return next_move
        
    def Move(self, bump):
        X = self.worldState.agentLocation[0]
        Y = self.worldState.agentLocation[1]
        if (self.worldState.agentOrientation == Orientation.RIGHT):
            X = X + 1
        if (self.worldState.agentOrientation == Orientation.UP):
            Y = Y + 1
        if (self.worldState.agentOrientation == Orientation.LEFT):
            X  = X - 1
        if (self.worldState.agentOrientation == Orientation.DOWN):
            Y = Y - 1
        if [X,Y] not in track.explored:
            track.explored.append([X,Y])
        if not bump:
            self.worldState.agentLocation = [X,Y]

    def check_stenches(self):
        if not track.wumpus_location:                   
            wumpus_location = [0,0]
            # looking at when we know at least 3 stench areas
            if len(track.stenches) >= 3:
                while reduce(mul, wumpus_location, 1) == 0:
                    for i in range(len(track.stenches)):
                        for j in range(2):
                            if track.stenches[i][j] == track.stenches[(i+1)%len(track.stenches)][j]:
                                wumpus_location[j] = track.stenches[i][j]
                                wumpus_location[(j+1)%2] = max(track.stenches[(i+1)%len(track.stenches)][(j+1)%2],track.stenches[i][(j+1)%2])-1
            
            elif len(track.stenches) == 2:
                s1, s2 = track.stenches
                if s1[0] < s2[0]:
                    s1, s2 = s2, s1
                # if s1 and s2 share 1 of same coords, then wumpus is between them
                for j in range(2):
                    if s1[j] == s2[j]:
                        wumpus_location[j] = s1[j]
                        wumpus_location[(j+1)%2] = max(s1[(j+1)%2], s2[(j+1)%2]) - 1

                # else we need to check 2 spots that are kitty corner
                if reduce(mul, wumpus_location, 1) == 0:
                    if s1[0] > s2[1] and s1[1] < s2[1]:
                        if [s1[0]-2, s1[1]] in track.explored or [s2[0], s2[1]-2] in track.explored or [s1[0]-1, s1[1]] in track.explored:
                            wumpus_location = [s1[0], s2[1]]
                        elif [s2[0]+2, s2[1]] in track.explored or [s1[0], s1[1]+2] in track.explored or [s2[0]+1, s2[1]] in track.explored:
                            wumpus_location = [s2[0], s1[1]]
                    else:
                        if [s1[0]-2, s1[1]] in track.explored or [s2[0], s2[1]+2] in track.explored or [s1[0]-1, s1[1]] in track.explored :
                            wumpus_location = [s1[0], s2[1]]
                        elif [s2[0]+2, s2[1]] in track.explored or [s1[0], s1[1]-2] in track.explored or [s2[0]+1, s2[1]] in track.explored:
                            wumpus_location = [s2[0], s1[1]]

            elif len(track.stenches) == 1:
                s1 = track.stenches[0]
                #need to have three explored nodes
                adjacents = [[s1[0], s1[1]+2],[s1[0]+2, s1[1]],[s1[0], s1[1]-2],[s1[0]-2, s1[1]]]

                explored_adj = []
                for adjacent in adjacents:
                    if adjacent in track.explored:
                        explored_adj.append(adjacent)
                if len(explored_adj) == 3:
                    for adjacent in adjacents:
                        if adjacent not in explored_adj:
                            for j in range(2):
                                if adjacent[j] == s1[j]:
                                    wumpus_location[j] = s1[j]
                                    wumpus_location[(j+1)%2] = max(s1[(j+1)%2], adjacent[(j+1)%2]) - 1
                                    
            if reduce(mul, wumpus_location, 1) != 0:
                track.wumpus_location = wumpus_location
    

myAgent = 0
track = 0

class Tracking():
    def __init__(self):
        self.path = []
        self.stenches = []
        self.gold_location = None
        self.wumpus_location = None
        self.next_location = None
        self.explored = [[1,1]]
        self.gold_path = []

def PyAgent_Constructor ():
    print "PyAgent_Constructor"
    global myAgent
    global track
    track = Tracking()
    myAgent = Agent()

def PyAgent_Destructor ():
    global myAgent
    global track
    track = Tracking()
    myAgent = Agent()
    print "PyAgent_Destructor"

def PyAgent_Initialize ():
    print "PyAgent_Initialize"
    global myAgent
    global track
    myAgent.Initialize()

def PyAgent_Process (stench,breeze,glitter,bump,scream):
    global myAgent
    percept = {'Stench': bool(stench), 'Breeze': bool(breeze), 'Glitter': bool(glitter), 'Bump': bool(bump), 'Scream': bool(scream)}
    return myAgent.Process(percept)

def PyAgent_GameOver (score):
    print "PyAgent_GameOver: score = " + str(score)
