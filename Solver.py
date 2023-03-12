from typing import Set, Tuple, Dict
from collections import defaultdict
from functools import reduce
from Term import *
class Solver:
    class ClashExeption(Exception):
        def __init__(self,t1,t2):
            self.lterm = t1
            self.rterm = t2
        def handle(self):
            print()
            print("symbol clash: ",self.lterm,set(self.rterm))
            print("solved set: ",solved)
            return None
        pass
    class CycleException(Exception):
        def __init__(self,prob):
            self.ununified = prob
        def handle(self):
            print("Cycle Detected:")
            for x in self.ununified:
                print("\t"+x.format())
            return None
        pass

    def __init__(self):
        self.eqs = defaultdict( set)
        self.starc=-1

#Fresh variables are needed when introducing equations to solved
    def freshvar(self,active):
        self.starc+=1
        return Var("*",self.starc,active)

# mm has the structure (variables,terms,subterm at position,Symbols found)
    def mmeq(mm,term):
        vars,terms,matches,syms = mm
        if type(term) is Var:
# remove occurances of variables found during decomposition
            Var.find(term).occ =Var.find(term).occ-1
            vars.append(term)
        elif type(term) is App and not term.func.Rec:
            terms.append(term)
            syms.add(term.func)
            for x in range(0,term.func.arity): matches[x].append(term.args[x])
        elif type(term) is App and term.func.Rec:
            terms.append(term)
            syms.add(term.func)
        return (vars,terms,matches,syms)

# M and M decomposition function
# decomposes the terms and builds the common part
# and frontier
    def decompose(self,ts):
        vars,terms,matches,syms =reduce(lambda a,b: Solver.mmeq(a,b) ,ts,([],[],defaultdict(lambda :[]),set()))
        reccount,sym = reduce(lambda a,b: (a[0]+1,a[1]) if b.Rec else (a[0],b),syms,(0,None))
        if len(syms)>1 and reccount == 0:
            raise Solver.ClashExeption(syms,ts)
        elif len(syms)>1 and reccount>0 and len(vars)== 0:
            starvar = self.freshvar(True)
            return (starvar,[([starvar],terms)])
        elif len(syms)==1 and reccount>0 and len(vars)== 0:
            return (terms[0],[])
        if len(vars)>0:
            return (reduce(lambda a,b:  Var.union(a,b),vars),[(set(vars),terms)])
        else:
            args,front=[None]*sym.arity,[]
            for x,y,z in map(lambda a: (a[0],*self.decompose(a[1])),matches.items()):
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
            if type(t) is Var: Var.find(t).occ+=1
            elif type(t) is App and not t.func.Rec: t.inducApp(varocc)

#Builds multiequations based on the input equations
        for x,y in self.eqs.items():
            vars, terms = reduce(sortbytype,y,(set(),set()))
            if type(x) is Var:
                repvar = reduce(lambda a,b: Var.union(a,b),vars,Var.find(x))
                for t in terms: varocc(t)
                repvar.terms.extend(terms)
                var_reps.add(repvar)
            else:
                for v in vars:
                    repvar = Var.find(v)
                    varocc(x)
                    repvar.terms.append(x)
                    var_reps.add(repvar)
                for t in terms:
                    repvar = self.freshvar()
                    varocc(x)
                    varocc(t)
                    repvar.terms.extend([t,x])
                    var_reps.add(repvar)
        var_reps= set([Var.find(x) for x in var_reps])
        return var_reps,set(filter(lambda a: Var.find(a).occ==0,var_reps))

    def unify(self,currentprob,debug=False):
        tosolve,var_reps = self.preprocess()
        solved =set()
        subproblems=[]
        steps=0
        def drop_occs(t):
            if type(t) is Var: Var.find(t).occ-=1
            elif type(t) is App and not t.func.Rec: t.inducApp(drop_occs)


        while len(var_reps)>0:
            if debug: print_current_step(steps,currentprob,tosolve)
#Get the next multi-equation with zero occurances
            cur = var_reps.pop()
#Remove it from the to solve set
            tosolve.remove(cur)

            if cur.vclass[0]=='*' and cur.active:
                for t in cur.terms: drop_occs(t)
                subproblems.append(cur)
                for x in tosolve:
                    if x.occ ==0:
                        var_reps.add(x)
                steps+=1
                continue
#check if there are terms on the right side of the multiequation
            if cur.terms!= []:
                try:
#decompose the terms on the right side of the multiequation to get
#the common part and frontier
                    common,front = self.decompose(cur.terms)
                except Solver.ClashExeption as e: pass
                if debug:
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
                    if debug: print("\t"+str(vrep.occ)+":{"+','.join([str(x)for x in fvar])+"}"+" =?= "+"{{"+','.join([str(x)for x in fterms])+"}}" )
                    vrep.terms.extend(fterms)
                    if vrep.occ == 0: var_reps.add(vrep)
                    tosolve.add(vrep)
                    solved.update([(v,vrep) for v in fvar if  v != vrep])
                tosolve =set([Var.find(x) for x in tosolve])
                if debug:
                    print()
                    print("==========================================================")
            else:
                if debug:
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

    def print_current_step(steps,currentprob,tosolve):
        print("Step ",str(steps)," of ",str(currentprob))
        for x in tosolve: print("\t"+x.format())
        print()
