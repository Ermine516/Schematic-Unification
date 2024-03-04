from Substitutable import *
from collections.abc import Iterable
class Substitution(Substitutable): 
    def __init__(self,pairs=[]): 
        self.mapping = {}
        self.addBindings(pairs)
        
# Magic Methods

    def __add__(self,b):
        self.addBinding(*b)
        return self

    def __str__(self):
        return "{"+ ",".join([ str(x)+" ==> "+str(y) for x,y in self.mapping.items()]) +"}"

    def __call__(self, *args):
        x= args[0] if len(args)==1 else None
        if isinstance(x,Substitutable): return x.handleSubstitution(self)
        elif isinstance(x,Iterable): return x.__class__.__call__(map(self,x))
        else: raise ValueError()

    def __iter__(self):
        return self.mapping.keys().__iter__()

    def __next__(self):
        return self.mapping.keys().__next__()

# Abstract Methods
    def handleSubstitution(self,sigma):
        ret = Substitution()
        for x in self.domain(): ret.addBinding(x,sigma(self.mapping[x]))
        for x in sigma.domain()-self.domain(): ret.addBinding(x,sigma.mapping[x])
        return ret

# Class Specific Methods

    def addBinding(self,x,t):
        if not (isinstance(x,Domainable) or isinstance(t,Substitutable) or x!=t): raise ValueError
        self.mapping[x] = t
    
    def addBindings(self,pairs):
        for x in pairs: 
            assert len(x) == 2
            self.addBinding(*x) 

    def removebinding(self,x):
        if x in self.mapping.keys(): del  self.mapping[x]

    def domain(self):
        return self.mapping.keys()

    def range(self):
        return set(self.mapping.values())   

    def restriction(self,f):
        sigma = Substitution()
        for x in self.mapping:
            if f(x): sigma.addBinding(x,self.mapping[x])
        return sigma

