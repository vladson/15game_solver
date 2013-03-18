#! /usr/bin/env python
'''
 Script devoted to solve 15 puzzle
@author: vladson vladson4ik@gmail.com
@version: 0.2
@pyversion 3
'''

from copy import deepcopy
#from numpy import matrix # Matrix only for display. In there is no NumPy, redefine Node.view()  
from Queue import PriorityQueue
from random import shuffle, randrange
import time
from heapq import nlargest
from optparse import OptionParser
from abc import ABCMeta, abstractmethod, abstractproperty

parser = OptionParser()
parser.add_option("-b","--base",dest = "base15",
          help="Base for 15 game", default = 3)
parser.add_option("-s","--sequence",dest="game15",
          help="Game sequence from left to right and from top to bottom")
parser.add_option("-r", '--random', action = "store_true", dest="rand15", default=False,
                help="If we should generate random game")
parser.add_option("-g",'--generate', dest="gen15", default = False,
                help = "If you want to set game state in n quasi-random available moves, then specify number")
parser.add_option("-c", "--complexity", dest = "comlexity", default = False,
                help = "If you want to limit Approximate Cost of game sequence")
(options, args) = parser.parse_args()


class BaseNode:
    """
    Abstract class for Nodes acting an A* algorithm realization
    """
    __metaclass__ = ABCMeta
    
    @abstractproperty
    def getNode(self):
        return self.node
    
    @abstractmethod
    def getAppCost(self):
        pass
    @abstractmethod
    def solvable(self):
        return True
    
    @abstractmethod
    def getEdges(self):
        pass
    
    @abstractmethod
    def view(self):
        pass
    
    @abstractmethod
    def hash(self):
        pass
    @abstractmethod
    def isGoal(self):
        pass
        
    

class Node15Base(BaseNode):
    """
    Base class for 15 game
    """
    
    def __init__(self, node):
        self.node = node
        
    def getAppCost(self):
        
        def mdi(i, l):
            pos = l.index(i)+1
            h = pos%self.base
            w = pos/self.base
            if h == 0:
                x = self.base
                y = w
            else:
                x = h
                y = w +1
            return x, y
        cost = 0
        for i in self.goal:
            cost = cost + sum(map(lambda e1, e2: abs(e1 - e2), mdi(i, self.goal), mdi(i, self.node)))        
        return cost
    
    def solvable(self):
        return self.evenness(self.node) ==  self.evenness(self.goal)
    
    def evenness(self, list):
        inv = 0
        for i in xrange(self.base*self.base):
            if not list[i] == 0:
                for j in xrange(i):
                    if list[i] < list[j]:
                        inv +=1
        inv = inv + (int(list.index(0))) / self.base
        return inv % 2 == 1
    
    def getNode(self):
        return self.node
    def setNode(self, node):
        self.node = node
    
    def isGoal(self):
        return self.node == self.goal
    

    def getMovementsMap(self):
        numpos = self.node.index(0)
        karta = {'getEdgeLeft':True, 'getEdgeRight':True, 'getEdgeDown':True, 'getEdgeUp':True}
        mod = numpos % self.base
        modplus = (numpos + 1) % self.base
        if mod == 0:
            karta['getEdgeLeft'] = False
        if modplus == 0:
            karta['getEdgeRight'] = False
        if numpos / self.base == 0:
            karta['getEdgeUp'] = False
        if numpos / self.base == (self.base - 1):
            karta['getEdgeDown'] = False
        moves = []
        for (name, flag) in karta.iteritems():
            if flag:
                moves.append(name)
        return moves

    def getEdges(self):
        return self.getEdgesByMap(self.getMovementsMap())
        
    def getEdgesByMap(self, karta):
        edges = []
        for name in karta:
            newNode = eval(self.__class__.__name__+"("+'self.' + name + "())")
            edges.append(Edge(self, newNode))
        return edges
    
    def getEdgeLeft(self):
        l = deepcopy(self.node)
        numpos = l.index(0)
        l.insert(numpos-1, l.pop(numpos))
        return l
    
    def getEdgeRight(self):
        l = deepcopy(self.node)
        numpos = l.index(0)
        l.insert(numpos+1, l.pop(numpos))
        return l
    
    def getEdgeDown(self):
        l = deepcopy(self.node)
        numpos = l.index(0)
        e1 = l.pop(numpos+self.base)
        e2 = l.pop(numpos)
        l.insert(numpos, e1)
        l.insert(numpos+self.base, e2)
        return l
    
    def getEdgeUp(self):
        l = deepcopy(self.node)
        numpos = l.index(0)
        e1 = l.pop(numpos)
        e2 = l.pop(numpos-self.base)
        l.insert(numpos-self.base, e1)
        l.insert(numpos, e2)
        return l
    
    def setStateRandSteps(self, steps):
        """
        Set state in integer available steps
        without passing states several times
        """
        self.setNode(self.goal)
        prevstates = set([])
        while steps >= 0:
            prevstates.add(self.hash())
            steps = int(steps) - 1
            karta = self.getMovementsMap()
            flag = False
            while not flag:
                move = karta[randrange(0, len(karta))]
                newstate = eval("self."+move+"()")
                if not self.hash(newstate) in prevstates:
                    flag = True
                    self.setNode(newstate)
    
    def view(self):
        #print matrix(self.node).reshape(self.base, self.base)
        print "-".join(map(lambda i: str(i), self.node))
        
    def hash(self, node = False):
        if not node:
            node = self.node
        return int(reduce( lambda x,y: str(x)+str(y),node))
    
class Node3 (Node15Base):
    """
        For field 3x3
    """

    def __init__(self, node = False):
        self.goal = [1,2,3,4,5,6,7,8,0]
        self.base = 3
        if node:
            self.node = node
        else:
            self.node = self.goal
        
class Node4 (Node15Base):
    """
        For field 4x4
    """

    def __init__(self, node = False):
        self.goal =  [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,0]
        self.base = 4
        if node:
            self.node = node
        else:
            self.node = self.goal
    
class Edge:
    """
        Edge realization
    """
    
    cost = 1
    def __init__(self, begining, end):
        self.begining = begining
        self.end = end
    def getBegining(self):
        return self.begining
        
    def getEnd(self):
        return self.end
        
    def getCost(self):
        return self.end.getAppCost()+1

class Path:
    """
        Path realization
    """
    
    def __init__(self):
        self.path = []
        self.edge = None
        self.cost = 0
        
    def getLast(self):
        if len(self.path):
            return self.path[-1]
        
    def getCost(self):
        return self.getLast().getAppCost()+len(self.path)
    
    def addNode(self, node):
        self.path.append(node)
        
    def addEdge(self, edge):
        self.edge = edge
        self.addNode(self.edge.getEnd())
        
    def getEdgeCost(self):
        return self.edge.getCost()
    
    def clone(self):
        new_path = Path()
        for node in self.path:
            new_path.path.append(node)
        return new_path
    
    def printout(self):
            print "Number of steps: %i " % len(self.path)
            for node in self.path:
                node.view()
                print ""
    

def solve(start, base = 3, compl = False):
    """
    Main cycle of algorithm
    """
    appcost = start.getAppCost()
    if compl :
        if appcost > int(compl):
            print "Game is more comlex than limit is set"
            return
    if not start.solvable():
        start.view()
        print "Not solvable. Approximate cost %i" % appcost
        return
    print "Game begins! Approximate cost %i"% appcost
    print time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime())
    start.view()
    path = Path()
    path.addNode(start)
    
    opens = PriorityQueue()
    closed = set([])
    opens.put((path.getCost(),path))
    i = 1
    try:
        while not opens.empty():
            i = i+1
            f, path = opens.get()
            last = path.getLast()
            if last.isGoal():
                print "Done! Iterations: %i" % i
                print time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime())
                return path.printout()
            for edge in last.getEdges():
                newpath = path.clone()
                newpath.addEdge(edge)
                if newpath.getLast().hash() in closed:
                    continue
                opens.put((newpath.getCost(), newpath))
            closed.add(last.hash())
    except (KeyboardInterrupt):
        print "User abort. Iterations done %i" % i
        [(h, p)] = nlargest(1, opens.queue)
        print "Maximum num of elts in path %i and priority %i" % (len(p.path), h)
        return
        
    print "Solution not found. Iterations done %i" % i
    print time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime())
    
"""
Parsing cli options and starting
"""
cliBase = int(options.base15)
node = eval("Node"+str(cliBase)+"()")
goodFlag = False
if options.gen15:
    node.setStateRandSteps(options.gen15)
    goodFlag = True
if options.rand15 and not options.comlexity:
    game = range(0,cliBase*cliBase)
    game.reverse()
    shuffle(game)
    node.setNode(game)
    goodFlag = True
if options.rand15 and options.comlexity:
    easy = False
    while not easy:
        game = range(0,cliBase*cliBase)
        game.reverse()
        shuffle(game)
        node.setNode(game)
        if node.getAppCost() <= int(options.comlexity):
            easy = True
        goodFlag = True
if options.game15:
    node.setNode(eval(options.game15))
    goodFlag = True
if  goodFlag:
    solve(node, cliBase, options.comlexity)
else:
    parser.print_help()