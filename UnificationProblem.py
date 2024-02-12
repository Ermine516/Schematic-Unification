import SchematicSubstitution as schsub
from Substitution import Substitution as sub

class nonUniforminputException(Exception):
    def __init__(self):
        pass
    def handle(self):
        print("""The input schematic substitution is non-uniform. The algorithm is designed for uniform schematic substitutions only. Using a non-uniform schematic subsitutions may lead to non-stability. To continue type OK and Press Enter.""")
        x = input()
        return False if x.lower() =="ok" else True

class UnificationEquation:
    def __init__(self,left,right,anno=""):
        self.left = left
        self.right = right
        self.iterstate = 2
        self.anno=anno
    def __iter__(self):
        self.iterstate=2
        return self
    def __next__(self):
        if self.iterstate ==0:
            raise StopIteration
        ret = self.left if self.iterstate == 2 else self.right
        self.iterstate = self.iterstate - 1
        return ret
    def duplicate(self):
        return UnificationEquation(self.left,self.right)
    def instance(self):
        return UnificationEquation(self.left.instance(),self.right.instance())
    def flip(self):
        return UnificationEquation(self.right,self.left)
    def reflexive(self):
        return self.left ==self.right
    def vars(self):
        return self.left.vars().union(self.right.vars())
    def recs(self):
        ret = set()
        for t in self:
            ret.update(t.recs())
        return ret
    def depth(self):
        return max(self.left.depth(),self.right.depth())
    
    def maxIdx(self):
        return max(self.left.maxIdx(),self.right.maxIdx())

    def normalization(self):
        ret = self.instance() 
        ret.right= ret.right.normalizedInstance()
        return ret
    def handleSubstitution(self,sigma):
        return UnificationEquation(sigma(self.left),sigma(self.right))
    def __getitem__(self,key):
        if not isinstance(key, int): raise TypeError
        if not key in [0,1]: raise KeyError
        return self.left if key ==0 else self.right
    def __str__(self):
        return "\t" +(self.anno+" : " if self.anno!="" else "")+ f"{self.left} =?= {self.right}\n"
    def __repr__(self):
        return f"({repr(self.left)},{repr(self.right)})"
    def __eq__(self, other):
        return isinstance(other, __class__) and self.left == other.left and self.right == other.right

    def __hash__(self):
        return hash((self.left,self.right))

class UnificationProblem:
    def __init__(self,debug=0):
        self.schSubs = schsub.SchematicSubstitution()
        self.prob = set()
        self.PrimMap = sub()
        self.debug = debug
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
        self.schSubs.add_relevent_vars(other)
        return self
    def __contains__(self,item):
        return item in self.prob
    
    def vars(self):
        ret = set()
        for x in self.prob:
            ret.update(x.vars())
        return ret
    def depth(self):
        return max((x.depth() for x in self.prob))
    def maxIdx(self):
        return max((x.maxIdx() for x in self.prob))

    def increment(self,ss):
        ss.clear()
        ss.ground(localRecs=self.recs())
        return ss(self.instance())
    def handleSubstitution(self,sigma):
        ret = UnificationProblem()
        for eq in self.prob:
            nEq = sigma(eq)
            ret.addEquation(nEq.left,nEq.right)
        return ret
    def normalization(self):
        ret = self.instance() 
        for x in ret:
            x.right= x.right.normalizedInstance()
        return ret
    def instance(self):
        inst = UnificationProblem()
        inst.schSubs = self.schSubs
        inst.PrimMap = self.PrimMap
        inst.debug = self.debug 
        inst.prob = set([uEq.instance() for uEq in self.prob]) 
        return inst
    def addEquation(self,s,t,anno=""):
        nEq = UnificationEquation(s,t,anno)
        self.prob.add(nEq)
        self.schSubs.add_relevent_vars(nEq)

    def addEquations(self,pairs):
        for x,y in pairs:
            self.addEquation(x,y)
    def clearReflex(self):
        removeSet =set()
        for x in self.prob:
            if x[0] ==x[1]:
                removeSet.add(x)
        for x in removeSet:
            self.prob.remove(x)

    def addMapping(self,s,t):
        self.schSubs.add_interpreted(s,t)
    def addMappings(self,pairs):
        for x,y in pairs:
            self.schSubs.add_interpreted(x,y)
    def makePrimitive(self):
        if self.schSubs.uniform == False: raise nonUniforminputException()
        if self.schSubs.primitive == False:
            if(self.debug>0):
                print("Schematic substitution is Uniform but Non-Primitive.")
            self.schSubs,self.PrimMap = self.schSubs.makePrimitive()
            if(self.debug>0):
                print("Mapping used to transform Schematic substitution:")
                print("\t",self.PrimMap)
            self.prob = set([UnificationEquation(self.PrimMap(x),self.PrimMap(y)) for x,y in self.prob])
    def recs(self):
        ret = set()
        for uEq in self:
            ret.update(uEq.recs())
        return ret