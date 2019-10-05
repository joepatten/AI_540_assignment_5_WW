# PyAgent.py

from random import randint
import Action
import Orientation
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
        self.explored = [[1,1]]
    
    def Process(self, percept):
        self.UpdateState(percept)
        if (not self.actionList):
            if (percept['Glitter']): # Rule 3a
                self.actionList.append(Action.GRAB)
                track.gold_location = self.worldState.agentLocation
            elif (self.worldState.agentHasGold and (self.worldState.agentLocation == [1,1])): # Rule 3b
                self.actionList.append(Action.CLIMB)
            elif (percept['Bump']): # Rule 3d
                X, Y = self.worldState.agentLocation
                if self.worldState.agentOrientation == 0:
                    X += 1
                elif self.worldState.agentOrientation == 1:
                    Y += 1
                elif self.worldState.agentOrientation == 2:
                    X -= 1
                elif self.worldState.agentOrientation == 3:
                    Y -= 1
                if [X,Y] not in self.explored:
                    self.explored.append([X,Y])
                randomAction = 1 #randint(1,2) # 1=TURNLEFT, 2=TURNRIGHT
                self.actionList.append(randomAction)
                track.path = track.path[:-1]
            else: # Rule 3e
                if (percept['Stench']): # Rule 3c
                    if self.worldState.agentLocation in track.stenches:
                        track.stenches.append(self.worldState.agentLocation)
                #look in front using orientation, if explored, turn left. might have to look at all
                #add next move here in explored
                #turn until oriented correctly
                if track.path and self.worldState.agentHasGold:
                    #have gold and go backwards to start
                    next_loc = track.path[-1]
                    next_move = self.get_move(next_loc)
                    #update next location in case we die
                    time.sleep(.2)
                    if self.orientation_move[self.worldState.agentOrientation] == next_move:
                        self.actionList.append(Action.GOFORWARD)
                        track.path = track.path[:-1]
                    else:
                        self.actionList.append(1) #turn left

                elif track.gold_location:
                    next_move, turns = self.get_min_direction()
                    #need to consider bump (if bump, then take direction we currently are in and exclude from list)
                    track.next_location = self.add_vectors(self.worldState.agentLocation,next_move)
                    if self.orientation_move[self.worldState.agentOrientation] == next_move:
                        # we are turned the correct way
                        self.actionList.append(Action.GOFORWARD)
                        track.path.append(self.worldState.agentLocation)
                    else:
                        self.get_best_turn(turns)
                        

                else:
                    # uninformed search exploration stage (TODO)

                    track.next_location = self.add_vectors(self.worldState.agentLocation,self.orientation_move[self.worldState.agentOrientation])
                    
                    #we we are about to run into a wumpus, then pick another route
                    if track.next_location == track.wumpus_location or percept['Bump']:
                        self.actionList.append(1)
                    elif track.next_location in (self.explored):
                        potential_moves = self.get_all_moves()
                        if len(potential_moves) == 0:
                            #turn around and go forward (back)
                            #look at path
                            print(track.path)
                            #track.path = track.path[:-1]
                            previous_location = track.path[-1]

                            print('previous_location')
                            print previous_location

                            #turn and then goforward to previous location in path
                            next_move = self.add_vectors(previous_location, self.worldState.agentLocation, negative=True)

                            new_direction = self.get_direction(next_move)
                            print(new_direction)
                            print(next_move)
                            turns = self.get_turns(new_direction) % 4
                            if turns <= 2:
                                for _ in range(turns):
                                    self.actionList.append(2) #turn right
                            else:
                                for _ in range(4 - turns):
                                    self.actionList.append(1)
                            
                            self.actionList.append(Action.GOFORWARD)
                            track.path = track.path[:-1]
                        else: 
                            #turn left until heading toward unexplored
                            self.actionList.append(1)
                            #next_move = potential_moves[0]
        


                    else:
                        self.actionList.append(Action.GOFORWARD)
                        track.path.append(self.worldState.agentLocation)
        action = self.actionList.pop(0)
        self.previousAction = action
        time.sleep(.35)
        return action

    def get_turns(self, new_direction):
        return self.worldState.agentOrientation - new_direction

    def get_direction(self, new_move):
        for k,v in self.orientation_move.items():
            print(v)
            print(new_move)
            if v == new_move:
                return k

    def get_best_turn(self, turns):
        if turns == -1 or turns == 3:
            self.actionList.append(1) #turn left
        else:
            self.actionList.append(2)

    def get_all_moves(self):
        potential_moves = []
        for k in self.orientation_move:
            potential_move = self.add_vectors(self.orientation_move[k], self.worldState.agentLocation)
            if potential_move not in self.explored and potential_move != track.wumpus_location:
                potential_moves.append(self.orientation_move[k])
        return potential_moves

    def get_min_direction(self):
        min_distance = 100000
        direction = [1,0]
        direction = None
        for k,v in self.orientation_move.items():
            new_loc = self.add_vectors(v, self.worldState.agentLocation)
            if new_loc == track.wumpus_location:
                print 'wow we found teh wunous location'
                continue
            dist_abs = self.add_vectors(new_loc, self.negative_vector(track.gold_location))
            t = self.get_turns(k)
            dist = self.get_abs_sum(dist_abs)

            if dist < min_distance:
                direction = v
                min_distance = dist
                turns = t
        return direction, turns
    
    def UpdateState(self, percept):
        currentOrientation = self.worldState.agentOrientation
        if (self.previousAction == Action.GOFORWARD):
            if (not percept['Bump']):
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
        # get orientation by turning

    def get_abs_sum(self, vec):
        return sum([abs(v) for v in vec])
        
    def Move(self):
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
        if [X,Y] not in self.explored:
            self.explored.append([X,Y])
        self.worldState.agentLocation = [X,Y]

    

        
# Global agent
myAgent = 0

class Tracking():
    def __init__(self):
        self.path = []
        self.stenches = []
        self.gold_location = None
        #self.gold_location = [4,4]
        self.wumpus_location = None
        #self.wumpus_location = [4,3]
        self.next_location = None

track = Tracking()

def PyAgent_Constructor ():
    print "PyAgent_Constructor"
    global myAgent
    global track
    myAgent = Agent()

def PyAgent_Destructor ():
    global myAgent
    global track
    myAgent = Agent()
    print "PyAgent_Destructor"

def PyAgent_Initialize ():
    print "PyAgent_Initialize"
    global myAgent
    global track
    track.wumpus_location = track.next_location
    myAgent.Initialize()

def PyAgent_Process (stench,breeze,glitter,bump,scream):
    global myAgent
    percept = {'Stench': bool(stench), 'Breeze': bool(breeze), 'Glitter': bool(glitter), 'Bump': bool(bump), 'Scream': bool(scream)}
    #print "PyAgent_Process: percept = " + str(percept)
    return myAgent.Process(percept)

def PyAgent_GameOver (score):
    print "PyAgent_GameOver: score = " + str(score)
    print "Explored: score = " + str(myAgent.explored)
    print "Stench: score = " + str(track.stenches)
    #print 'next_location' + track.next_location
    print track.wumpus_location

