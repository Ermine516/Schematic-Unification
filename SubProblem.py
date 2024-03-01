from Term import *
from UnificationProblem import *
from Substitution import *
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
        self.futurevars ={}
        self.recs = set()
        self.stab =-1
        self.futureRel = futureRel
        self.cyclic = False
        self.eqSubstitution = None
        self.simplified= None
        self.IrrSub =Substitution()

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
            def applys(s,t):    
                if type(t) is App:
                    return t.func(*map(lambda x: applys(s,x),t.args))
                elif type(t) is Var and t in s.keys():
                    return Var(s[t].vc,s[t].idx)
                elif type(t) is Var and not t in s.keys():
                    return Var(t.vc,t.idx)
                else:
                    return Rec(t.vc,t.idx)
            def checkfur(y):
                for r in self.recs:
                    if dom.isFutureRelevant(r,y): return True
                return False
            simp =Substitution()
            grouping ={}
            vars= set()
            newsubp= UnificationProblem()
            furtureRelevant = set()
            for x,y in self.subproblem:
                if type(x) is Var and type(y) is Var:
                    check = True
                    for g in grouping.keys():
                        if x in grouping[g] or y in grouping[g]:
                            grouping[g].update(set([x,y]))
                            vars.add(x)
                            vars.add(y)
                            check = False
                    if check:
                        grouping[x]= set([x,y])
                elif not type(x) is Var or not type(y) is Var:
                    newsubp.addEquation(x,y)

            orderedGroup = {}
            for x,y in grouping.items():    
                maxV =x
                maxbase=set()
                for z in y:
                    if z.idx > maxV.idx: maxV = z
                for z in y:
                    if z != maxV: maxbase.add(z)
                orderedGroup[maxV]=maxbase
            for x,y in orderedGroup.items():
                fr = False
                for z in y: 
                    if checkfur(x) or checkfur(z):
                        fr = True
                    simp.addBinding(z,x)
                if fr:
                    #furtureRelevant.update(y)
                    furtureRelevant.add(x)
            newsubp=simp(newsubp)
            newsubp.clearReflex()
            ret = SubProblem(newsubp,futureRel = furtureRelevant )
            self.futureRel = furtureRelevant
            self.simplified= ret
            self.eqSubstitution = simp
            return ret