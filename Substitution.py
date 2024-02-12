from Term import *
from UnificationProblem import *

class Substitution: 
    def __init__(self,pairs=[]): 
        self.mapping = {}
        for x,y in pairs:
            self.mapping[x]=y
   
    def __add__(self,b):
        if type(b) is tuple and len(b) == 2:
            self.addBinding(b[0],b[1])
        return self

    def __str__(self):
        return "{"+ ",".join([ str(x)+" ==> "+str(y) for x,y in self.mapping.items()]) +"}"

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

    def applySub(self,x):
        if type(x) is App:
            return x.applyFunc(self.applySub)
        elif type(x) is Var and x in self.domain():
            return self.mapping[x].instance()
        elif type(x) is Rec and x in self.domain():
            return self.mapping[x].instance()
        else:
            return x.instance()
    def __call__(self, *args):
        if len(args) == 1 and type(args[0]) is set: return set(map(self,args[0]))
        elif len(args) == 1 and type(args[0]) is list: return list(map(self,args[0]))
        elif callable(getattr(args[0], "handleSubstitution", None)): return args[0].handleSubstitution(self)
        elif len(args) == 1 and isinstance(args[0],Term): return self.applySub(args[0])
        elif len(args) == 1 and type(args[0]) is Substitution:
            sigma = args[0]
            ret = Substitution()
            for x in self.domain():
                v,t = x,sigma.applySub(self.mapping[x])
                if v != t:
                    ret.addBinding(x,sigma.applySub(self.mapping[x]))
            for x in sigma.domain():
                if not x in self.domain():
                    ret.addBinding(x,sigma.mapping[x])
            return ret

        else: raise ValueError()

