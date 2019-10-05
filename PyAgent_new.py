# PyAgent.py

from random import randint
import Action
import Orientation
import time


class WorldState:
    def __init__(self, explored=None):
        self.agentLocation = [1,1]
        self.agentOrientation = Orientation.RIGHT
        self.agentHasArrow = True
        self.agentHasGold = False
    
class Agent:
    def __init__(self):
        self.worldState = WorldState()
        self.previousAction = Action.CLIMB
        path.append(self.previousAction)
        self.actionList = []
        self.orientation_move = {0:[1,0], 1:[0,1], 2:[-1,0], 3:[0,-1]}
        #self.explored = explored
    
    def Initialize(self):
        self.worldState.agentLocation = [1,1]
        self.worldState.agentOrientation = Orientation.RIGHT
        self.worldState.agentHasArrow = True
        self.worldState.agentHasGold = False
        self.previousAction = Action.CLIMB
        self.actionList = []

    
    def Process(self, percept):
        # percept is a dictionary of percepts
        # update state based on last moves
        self.UpdateState(percept)
        print self.worldState.agentLocation
        # given percepts, do some action
        if (not self.actionList):
            if (percept['Glitter']): # Rule 3a
                gold_location = self.worldState.agentLocation
                self.actionList.append(1)
                self.actionList.append(1)
                self.actionList.append(Action.GRAB)
                # once the gold is found, turn around (two lefts) and backtrack. will need to save moves and update list
            elif (self.worldState.agentHasGold and (self.worldState.agentLocation == [1,1])): # Rule 3b
                self.actionList.append(Action.CLIMB)
            elif (percept['Stench'] and self.worldState.agentHasArrow): # Rule 3c
                self.actionList.append(Action.SHOOT)
            elif (percept['Bump']): # Rule 3d
                #check if left + forward is explored, or right + forward is explored
                randomAction = 1 # 1=TURNLEFT, 2=TURNRIGHT
                # turn around
                self.actionList.append(randomAction)
                #self.actionList.append(1)
            else: # this depends on if we know where gold is - and/if we have gold
                if not self.worldState.agentHasGold:
                    if not gold_location:
                        # go forward
                    else:
                        # use a* - first claculate cost
                        # calc manhatten dist for each possible move:
                        # forward 
                        costs = []
                        for k in self.orientation_move:
                            new_loc = self.add_vectors(self.worldState.agentLocation, self.orientation_move[k])
                            
                            cost = self.add_vectors(gold_location, self.negative_vector(new_loc))
                            # sum the innards of the vector to find lowest cost
                            cost = sum([abs(v) for v in cost])
                            costs.append(cost)
                        min_cost = costs.index(min(costs))
                        self.actionList.append(Action.GOFORWARD)
        action = self.actionList.pop(0) 
        self.previousAction = action
        if not percept['Glitter']:
            path.append(action)
        return action #this is where the action actually happens

    def UpdateState(self, percept):
        currentOrientation = self.worldState.agentOrientation
        # only change squares when moving forward
        if (self.previousAction == Action.GOFORWARD):
            if (not percept['Bump']):
                if self.worldState.agentLocation not in explored:
                    path.append(self.worldState.agentLocation)
                self.Move()
        if (self.previousAction == Action.TURNLEFT):
            self.worldState.agentOrientation = (currentOrientation + 1) % 4
        if (self.previousAction == Action.TURNRIGHT):
            currentOrientation -= 1
            if (currentOrientation < 0):
                currentOrientation = 3
            self.worldState.agentOrientation = currentOrientation
        if (self.previousAction == Action.GRAB):
            self.worldState.agentHasGold = True # Only GRAB when there's gold
            # if agent has gold, then back track (use a*?)
        if (self.previousAction == Action.SHOOT):
            self.worldState.agentHasArrow = False
        # Nothing to do for CLIMB
        
    def negative_vector(self, vec):
        return [-v for v in vec]

    def backtrack(self):
        while path:
            print('backtracking')
            action = path.pop()
            if action == Action.TURNLEFT:
                action = Action.TURNRIGHT
            elif action == Action.TURNRIGHT:
                action = Action.TURNLEFT
            return action

    def add_vectors(self, vec1, vec2):
        return [v1 + v2 for v1,v2 in zip(vec1, vec2)]

    def Move(self): #given orientation, where do you end up if moving forward
        self.worldState.agentLocation = self.add_vectors(self.worldState.agentLocation, self.orientation_move[self.worldState.agentOrientation])


# Global agent
myAgent = 0
explored = []
gold_location = None
path = []
stench_loc = []
wumpus_loc = []

def PyAgent_Constructor ():
    print "PyAgent_Constructor"
    global myAgent
    global explored
    global path
    myAgent = Agent()

def PyAgent_Destructor ():
    print "PyAgent_Destructor"
    global myAgent
    global explored
    global path
    myAgent = Agent()

def PyAgent_Initialize ():
    print "PyAgent_Initialize"
    #input map
    global myAgent #it is a global variable BOOYAH
    global explored
    global path
    myAgent.Initialize()

def PyAgent_Process (stench,breeze,glitter,bump,scream):
    global myAgent
    percept = {'Stench': bool(stench), 'Breeze': bool(breeze), 'Glitter': bool(glitter), 'Bump': bool(bump), 'Scream': bool(scream)}
    #print "PyAgent_Process: percept = " + str(percept)
    time.sleep(.35)
    return myAgent.Process(percept)

def PyAgent_GameOver (score):
    print "PyAgent_GameOver: score = " + str(score)
    print explored
