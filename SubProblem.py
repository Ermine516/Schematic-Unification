from Term import *
from UnificationProblem import *
from Substitution import *
from functools import reduce as fold
from UnionFindNode import UnionFindNode 

class SubProblem:
   
    def __len__(self):
        return len(self.subproblem)
    def __str__(self):
        return str(self.subproblem) 
    def __iter__(self):
        return self.subproblem.__iter__()
    
    def __next__(self):
        return self.subproblem.__next__()
    def __init__(self,subproblem,futureRel=set()):
        self.subproblem = subproblem
        self.vars =set()
        self.recs = set()
        self.futurevars ={}
        self.stab =-1
        self.futureRel = futureRel
        self.cyclic = False
        self.eqSubstitution = None
        self.simplified= None
        self.IrrSub =Substitution()
        self.NormalSimplifiedForm = None

# Collects all variables and recursion occurring in the problem
        for uEq in subproblem:
            for t in uEq:
                self.vars.update(t.vos(Var))
                self.recs.update(t.vos(Rec))
# Collects all variables that are future relevent 
        for x in self.vars:
            if not x.vc in self.futurevars.keys(): self.futurevars[x.vc] =  x 
            if x.idx >self.futurevars[x.vc].idx: self.futurevars[x.vc] =  x 
   
    def normalization(self):
        return SubProblem(self.subproblem.normalize(),futureRel=self.futureRel)
    
    def simplify(self,dom):
            if self.eqSubstitution: return  self.simplified
            varUF = {}
            sigma =Substitution()
            grouping ={}
            orderedGroup = {}
            newsubp= UnificationProblem()
            furtureRelevant = set()
# Here we compute the equivalence classes 
            for x,y in self.subproblem:
                if type(x) is Var and type(y) is Var:
                    if not x in varUF.keys(): varUF[x] = UnionFindNode(x)
                    if not y in varUF.keys(): varUF[y] = UnionFindNode(y)
                    varUF[x].union(varUF[y])
                else: newsubp.addEquation(x,y)
            for x in varUF.keys():
                if not varUF[x].find().val in grouping.keys(): grouping[varUF[x].find().val] = set([x])
                else: grouping[varUF[x].find().val].add(x)
# We reorder the equivalence classes so the largest index is the representative
            for x,y in grouping.items():   
                maxfunc = lambda acc,val: (acc[0],acc[1].union(set([val]))) if acc[0].idx > val.idx else (val,acc[1].union(set([acc[0]])))
                maxV ,maxbase = fold(maxfunc, y,(x,set()))
                orderedGroup[maxV]=maxbase
# We construct the simplifying substitution here and mark the future relevant variables
            for x,y in orderedGroup.items():
                sigma.addBindings(list(map(lambda a: (a,x),y)))
                if len([z for z in list(y)+[x] if dom.isFutureRelevantTo(self.recs,z)]) != 0: furtureRelevant.add(x)                    
            newsubp=sigma(newsubp)
            newsubp.clearReflex()
            ret = SubProblem(newsubp,futureRel = furtureRelevant )
            self.futureRel = furtureRelevant
            self.simplified= ret
            self.eqSubstitution = sigma
            return ret