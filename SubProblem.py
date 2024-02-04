from Term import *

class SubProblem:
    def getvars(t):
        if type(t) is App:
            ret=set()
            for x in t.args: 
                ret.update(SubProblem.getvars(x))
            return ret
        elif type(t) is Var:
            return set([t]) 
        else:
            return set()  
    def getrecs(t):
        if type(t) is App:
            ret=set()
            for x in t.args: 
                ret.update(SubProblem.getrecs(x))
            return ret
        elif type(t) is Rec:
            return set([t]) 
        else:
            return set()  
    def __len__(self):
        return len(self.subproblem)
   
    def __init__(self,subproblem): 
        self.subproblem = subproblem
        self.vars =set()
        self.futurevars ={}
        self.recs = set()
        self.futureRel = set()
        self.cyclic = False
# Collects all variables and recursion occurring in the problem
        for x,y in subproblem:
            self.vars.update(SubProblem.getvars(x))
            self.vars.update(SubProblem.getvars(y))
            self.recs.update(SubProblem.getrecs(x))
            self.recs.update(SubProblem.getrecs(y))  
# Collects all variables that are future relevent 
        for x in self.vars:
            if not x.vc in self.futurevars.keys():
                self.futurevars[x.vc] =  x 
            if x.idx >self.futurevars[x.vc].idx: 
                self.futurevars[x.vc] =  x 
    def simplify(self,dom):
            def applys(s,t):    
                if type(t) is App:
                    return t.func(*map(lambda x: applys(s,x),t.args))
                elif type(t) is Var and t in s.keys():
                    return Var(s[t].vc,s[t].idx)
                elif type(t) is Var and not t in s.keys():
                    return Var(t.vc,t.idx)
                else:
                    return Rec(t.func,t.idx)
            def checkfur(y):
                for r in self.recs:
                    if dom.isFutureRelevant(r,y): return True
                return False
            applysub = lambda s:lambda a: (applys(s,a[0]),applys(s,a[1]))
            substitution ={}
            grouping ={}
            vars= set()
            newsubp= []
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
                    newsubp.append((x,y))
            # single = None
            # for x in self.vars:        
                # check = True
                # for g in grouping.keys():
                    # if x in grouping[g]:
                        # check = False
                # if check and not single:
                    # grouping[x]= set([x])
                    # single = x
                # elif check and single:
                    # grouping[single].add(x)
            for x,y in grouping.items():
                fr = False
                for z in y: 
                    if checkfur(x) or checkfur(z):
                        fr = True
                    substitution[z]=x
                if fr:
                    furtureRelevant.update(y)
            newsubp = set(map(applysub(substitution), newsubp))
            ret = SubProblem(newsubp)
            ret.futureRel = furtureRelevant
            return ret