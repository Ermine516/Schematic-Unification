from Term import *
from UnificationProblem import *
from Substitutable import Substitutable

class Substitution(Substitutable): 
    def __init__(self,pairs=[]): 
        self.mapping = {}
        for x,y in pairs:
            self.mapping[x]=y

# Magic Methods
  
    def __add__(self,b):
        if type(b) is tuple and len(b) == 2:
            self.addBinding(b[0],b[1])
        return self

    def __str__(self):
        return "{"+ ",".join([ str(x)+" ==> "+str(y) for x,y in self.mapping.items()]) +"}"

    def __call__(self, *args):
        x= args[0] if len(args)==1 else None
        if type(x) is set: return set(map(self,x))
        elif type(x) is list: return list(map(self,x))
        elif type(x) is tuple: return tuple(map(self,x))
        elif isinstance(x,Substitutable): return x.handleSubstitution(self)
        else: raise ValueError()

# Abstract Methods
    def handleSubstitution(self,sigma):
        ret = Substitution()
        for x in sigma.domain():
            ret.addBinding(x,sigma.mapping[x].handleSubstitution(self))
        for x in self.domain()-sigma.domain():
            ret.addBinding(x,self.mapping[x])
        return ret

# Class Specific Methods

    def addBinding(self,x,t):
        if not type(x) is Var and not type(x) is Rec: return False
        if x == t: return False
        self.mapping[x] = t
        return True

    def removebinding(self,x):
        if x in self.mapping.keys():
            del  self.mapping[x]

    def domain(self):
        return self.mapping.keys()

    def range(self):
        return self.mapping.values()   

    
    
   

