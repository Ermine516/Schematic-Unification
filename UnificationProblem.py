import SchematicSubstitution as schsub
from Substitution import Substitution as sub
from Substitutable import Substitutable
from TermAttr import TermAttr
from Normalizable import Normalizable
from Term import Rec, Term
class nonUniforminputException(Exception):
    def __init__(self):
        pass
    def handle(self):
        print("""The input schematic substitution is non-uniform. The algorithm is designed for uniform schematic substitutions only. Using a non-uniform schematic subsitutions may lead to non-stability. To continue type OK and Press Enter.""")
        x = input()
        return False if x.lower() =="ok" else True

class UnificationEquation(Substitutable,TermAttr,Normalizable):
    left        : Term
    right       : Term
    iterstate   : int
    anno        : str
    
    def __init__(self,left,right,anno=""):
        self.left = left
        self.right = right
        self.iterstate = 2
        self.anno=anno

#Magic Methods 

    def __iter__(self):
        self.iterstate=2
        return self
    
    def __next__(self):
        if self.iterstate ==0:
            raise StopIteration
        ret = self.left if self.iterstate == 2 else self.right
        self.iterstate = self.iterstate - 1
        return ret
    
    def __getitem__(self,key):
        if not isinstance(key, int): raise TypeError
        if not key in [0,1]: raise KeyError
        return self.left if key ==0 else self.right
    
    def __str__(self):
        return "\t " +(self.anno+" : " if self.anno!="" else "")+ f"{self.left} =?= {self.right}\n"
    
    def __repr__(self):
        return f"({repr(self.left)},{repr(self.right)})"
    
    def __eq__(self, other):
        return isinstance(other, __class__) and self.left == other.left and self.right == other.right

    def __hash__(self):
        return hash((self.left,self.right))
    
    def __contains__(self,item):
        return item is self.left or item is self.right

#Abstract Methods
    def normalize(self):
        ret = self.instance() 
        ret.right= ret.right.normalize()
        return ret
    def handleSubstitution(self,sigma):
        return UnificationEquation(sigma(self.left),sigma(self.right))

    def vos(self,sCls):
        return self.left.vos(sCls).union(self.right.vos(sCls))
    
    def vosOcc(self,sCls):
        return self.left.vosOcc(sCls) or self.right.vosOcc(sCls)
    
    def maxIdx(self):
        return max(self.left.maxIdx(),self.right.maxIdx())
    
    def minIdx(self):
        return max(self.left.minIdx(),self.right.minIdx())
    
    def occurs(self,t):
        if not isinstance(t,Term): raise ValueError
        return max(self.left.occurs(t),self.right.occurs(t))
    
    def depth(self):
        return max(self.left.depth(),self.right.depth())
    
    def instance(self):
        return UnificationEquation(self.left.instance(),self.right.instance())

    def applyFunc(self,f):
        return UnificationEquation(self.left.applyFunc(f),self.right.applyFunc(f))
#Class Specific Methods
    def duplicate(self):
        return UnificationEquation(self.left,self.right)
   
    def flip(self):
        return UnificationEquation(self.right,self.left)
    def reflexive(self):
        return self.left ==self.right

    
   
    
class UnificationProblem(Substitutable,TermAttr,Normalizable):
    def __init__(self,debug=0):
        self.prob = set()
        self.PrimMap = sub()
        self.debug = debug

#Magic Methods    

    def __len__(self):
        return len(self.prob)
    
    def __iter__(self):
        return self.prob.__iter__()
    
    def __next__(self):
        return self.prob.__next__()
    
    def __str__(self):
        return "{\n"+",\n".join([str(x) for x in self.prob])+"}"
    
    def __add__(self,other):
        self.prob.add(other)
        return self
    def __contains__(self,item):
        return item in self.prob
    
#Abstract Methods
    def normalize(self):
        ret = self.instance() 
        ret.prob = set([x.normalize() for x in ret])
        return ret
    
    def handleSubstitution(self,sigma):
        ret = UnificationProblem()
        for eq in self: 
            ret+= sigma(eq)
        return ret
    
    def vos(self,sCls):
        ret = set()
        for x in self:
            ret.update(x.vos(sCls))
        return ret

    def vosOcc(self,sCls):
        ret = []
        for x in self:
            ret.append(x.vosOcc(sCls))
        return ret

    def maxIdx(self):
        return max((x.maxIdx() for x in self))

    def minIdx(self):
        return max((x.minIdx() for x in self))
    
    def occurs(self,t):
        for x in self:
            if x.occurs(t): return True
        return False

    def depth(self):
        return max((x.depth() for x in self))
    
    def instance(self):
        inst = UnificationProblem()
        inst.PrimMap = self.PrimMap
        inst.debug = self.debug 
        inst.prob = set([uEq.instance() for uEq in self]) 
        return inst
    
    def applyFunc(self,f):
        newUP = self.instance()
        newUP.prob = set([uEq.applyFunc(f) for uEq in self]) 
        return newUP

#Class Specific Methods
    def increment(self,ss):
        ss.clear()
        ss.ground(localRecs=self.vos(Rec))
        return ss(self.instance())
    
    def addEquation(self,s,t,anno=""):
        nEq = UnificationEquation(s,t,anno)
        self.prob.add(nEq)

    def addEquations(self,pairs):
        for x,y in pairs:
            self.addEquation(x,y)
   
    def clearReflex(self):
        removeSet =set()
        for x in self.prob:
            if x[0] ==x[1]: removeSet.add(x)
        for x in removeSet:
            self.prob.remove(x)

    def makePrimitive(self,schSubs):
        if schSubs.uniform == False: raise nonUniforminputException()
        if schSubs.primitive == False:
            if(self.debug>0): print("Schematic substitution is Uniform but Non-Primitive.")
            schSubs,self.PrimMap = schSubs.makePrimitive(self)
            if(self.debug>0): print("Mapping used to transform Schematic substitution:\n","\t",self.PrimMap)
            self.prob = set([UnificationEquation(self.PrimMap(x),self.PrimMap(y)) for x,y in self])
        return schSubs
