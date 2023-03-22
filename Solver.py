from typing import Set, Tuple, Dict
from collections import defaultdict
from functools import reduce
from Term import *
class Solver:
    class ClashExeption(Exception):
        def __init__(self,t1,t2):
            self.lterm = t1
            self.rterm = t2
        def handle(self,debug):
            print()
            print("symbol clash: ",self.lterm,set(self.rterm))
            #print("solved set: ",solved)
            print()

            return None
        pass
    class CycleException(Exception):
        def __init__(self,prob,addendum=""):
            self.ununified = prob
            self.addendum=addendum
        def handle(self,debug):
            if debug >0:
                if self.addendum=="":print("Cycle Detected:")
                else:  print("Cycle Detected ("+self.addendum+"):")
                for x in self.ununified:
                    print("\t"+x.format())
                print()
            else: print("\t not unifiable")
            return None
        pass

    def __init__(self,I):
        self.eqs = defaultdict(set)
        self.starc=-1
        self.I = I
#Fresh variables are needed when introducing equations to solved
    def freshvar(self,active):
        self.starc+=1
        return Var("*",self.starc,active)

# mm has the structure (variables,terms,subterm at position,Symbols found)
    def mmeq(mm,term):
        vars,terms,matches,syms = mm
        if type(term) is Var:
# remove occurances of variables found during decomposition
            term.setocc(-1)
            vars.append(Var.find(term))
        elif type(term) is App:
            terms.append(term)
            syms.add(term.func)
            for x in range(0,term.func.arity): matches[x].append(term.args[x])
        elif type(term) is Rec:
            terms.append(term)
            syms.add(term)
        return (vars,terms,matches,syms)

    def futureoccurs(self,c,recs):
        for r in recs:
            for c1, gap in  self.I.associated_classes[r.func.name].items():
                if c1 in c.maxsub.keys() and c.maxsub[c1]>=gap+r.idx.number:
                    return r
        return None
# M and M decomposition function
# decomposes the terms and builds the common part
# and frontier
    def decompose(self,cur,ts):
        vars,terms,matches,syms =reduce(lambda a,b: Solver.mmeq(a,b) ,ts,([],[],defaultdict(lambda :[]),set()))
        recs,sym = reduce(lambda a,b: (a[0]+[b],a[1]) if type(b) is Rec else (a[0],b),syms,([],None))
        if len(syms)>1 and len(recs)==0:
            raise Solver.ClashExeption(syms,ts)
        elif len(syms)>1 and len(recs)>0 and len(vars)== 0:
            violation = self.futureoccurs(cur,recs)
            if violation: raise Solver.CycleException([cur],addendum= str(cur) +" occurs in "+str(violation))
            starvar = self.freshvar(True)
            return (starvar,[([starvar],terms)])
        elif len(syms)==1 and len(recs)>0 and len(vars)== 0:
            return (terms[0],[])
        if len(vars)>0:
            return (reduce(lambda a,b:  Var.union(a,b),vars),[(set(vars),terms)])
        else:
            args,front=[None]*sym.arity,[]
            for x,y,z in map(lambda a: (a[0],*self.decompose(cur,a[1])),matches.items()):
                args[x]=Var.find(y)
                front.extend(z)
            return (sym(*args),front)


    def preprocess(self):
        var_reps=set()
        def sortbytype(a,b):
             a[0 if type(b) is Var else 1].add(b)
             return a
#counts occurances of variables
        def varocc(t):
            if type(t) is Var: t.setocc(1)
            elif type(t) is App: t.inducApp(varocc)

#Builds multiequations based on the input equations
        for x,y in self.eqs.items():
            vars, terms = reduce(sortbytype,y,(set(),set()))
            if type(x) is Var:
                repvar = reduce(lambda a,b: Var.union(a,b),vars,Var.find(x))
                for t in terms: varocc(t)
                repvar.ts().extend(terms)
                var_reps.add(repvar)
            else:
                for v in vars:
                    varocc(x)
                    v.ts().append(x)
                    var_reps.add(Var.find(v))
                for t in terms:
                    repvar = self.freshvar()
                    varocc(x)
                    varocc(t)
                    repvar.ts().extend([t,x])
                    var_reps.add(repvar)
        var_reps= set([Var.find(x) for x in var_reps])
        return var_reps,set(filter(lambda a: a.occs()==0,var_reps))

    def unify(self,currentprob,debug=0,I=None):
        tosolve,var_reps = self.preprocess()
        solved =set()
        subproblems=[]
        steps=0
        def drop_occs(t):
            if type(t) is Var: t.setocc(-1)
            elif type(t) is App: t.inducApp(drop_occs)


        while len(var_reps)>0:
            if debug==3: self.print_current_step(steps,currentprob,tosolve)
#Get the next multi-equation with zero occurances
            cur = var_reps.pop()
#Remove it from the to solve set
            tosolve.remove(cur)

            if cur.vclass()[0]=='*' and cur.act():
                for t in cur.ts(): drop_occs(t)
                subproblems.append(cur)
                for x in tosolve:
                    if x.occs() ==0:
                        var_reps.add(x)
                steps+=1
                continue
#check if there are terms on the right side of the multiequation
            if cur.ts()!= []:
#decompose the terms on the right side of the multiequation to get
#the common part and frontier
                common,front = self.decompose(cur,cur.ts())
                if debug==3:
                    print("common: \n\t"+str(common))
                    print()
                    print("frontier: ")
#Finish compatification of the frontier,Partially done in during decomposition
# add multiequations to the zero occurance set if the variables have zero occurances
# always add the tosolve set incase they do not occur there
# add bindings for variables added to an eq class
#update tosolve some variables my have been updated
                solved.add((cur,common))
                for fvar,fterms in front:
                    vrep = Var.find(list(fvar)[0])
                    if debug==3: print("\t"+str(vrep.occs())+":{"+','.join([repr(x)for x in fvar])+"}"+" =?= "+"{{"+','.join([str(x)for x in fterms])+"}}" )
                    vrep.ts().extend(fterms)
                    if vrep.occs() == 0: var_reps.add(vrep)
                    tosolve.add(vrep)
                    solved.update([(v,vrep) for v in fvar if  v != vrep])
                tosolve =set([Var.find(x) for x in tosolve])
                if debug==3:
                    print()
                    print("==========================================================")
            else:
                if debug==3:
                    print("==========================================================")
            steps+=1
#If var_reps is empty and tosolve is not then we have a cycle
        if len(tosolve)!=0: raise Solver.CycleException(tosolve)
        return dict(solved),subproblems

    def add_eq(self,x,y):
        if type(x) is Var: self.eqs[x].add(y)
        elif type(y) is Var: self.eqs[y].add(x)
        else: self.eqs[self.freshvar(False)].update([x,y])

    def clear(self):
        self.eqs = defaultdict(set)

    def print_current_step(self,steps,currentprob,tosolve):
        print("Step ",str(steps)," of ",str(currentprob))
        for x in tosolve: print("\t"+x.format())
        print()
