from Substitutable import *
from collections.abc import Iterable
class Substitution(Substitutable): 
    def __init__(self,pairs=[]): 
        self.mapping = {}
        for x,y in pairs:
            if isinstance(x,Domainable) and isinstance(y,Substitutable): 
                self.mapping[x]=y
            else:
                raise ValueError()
# Magic Methods

    def __add__(self,b):
        self.addBinding(*b)
        return self

    def __str__(self):
        return "{"+ ",".join([ str(x)+" ==> "+str(y) for x,y in self.mapping.items()]) +"}"

    def __call__(self, *args):
        x= args[0] if len(args)==1 else None
        if isinstance(x,Substitutable): 
            return x.handleSubstitution(self)
        elif isinstance(x,Iterable): 
            return x.__class__.__call__(map(self,x))
        else: 
            raise ValueError()

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
        if not isinstance(x,Domainable) or x==t or x in self.mapping.keys(): 
            return False
        else:
            self.mapping[x] = t
            return True

    def removebinding(self,x):
        if x in self.mapping.keys():
            del  self.mapping[x]

    def domain(self):
        return self.mapping.keys()

    def range(self):
        return self.mapping.values()   

    
    
   

