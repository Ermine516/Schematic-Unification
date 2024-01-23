from typing import Set, Tuple, Dict
from collections import defaultdict
from Solver import Solver
from functools import reduce
from Term import *
class MM(Solver):
    def __init__(self,SchematicSubstitution=None,debug=0,start_time=-1):
       self.problemVars={}
       self.var_reps = set()
       self.tosolve = set()
       self.solved =set()
       self.currentprob=0
       super().__init__(SchematicSubstitution,debug,start_time)

    def getrep(self,t):
        rep =self.problemVars[t.vc][t.idx] 
        return Var.find(rep)

# mm has the structure (variables,terms,subterm at position,Symbols found)
    def mmeq(self,mm,term):
        vars,terms,matches,syms = mm
        if type(term) is Var:
            asVar = self.getrep(term)
# remove occurances of variables found during decomposition
            asVar.setocc(-1)
            vars.append(asVar)
        elif type(term) is App:
            terms.append(term)
            syms.add(term.func)
            for x in range(0,term.func.arity): matches[x].append(term.args[x])
        return (vars,terms,matches,syms)

    def futureoccurs(self,c,recs):
        for r in recs:
            for c1, gap in  self.SchematicSubstitution.associated_classes[r.func.name].items():
                if c1 in c.maxsub.keys() and c.maxsub[c1]>=gap+r.idx.number:
                    return r
        return None
# M and M decomposition function
# decomposes the terms and builds the common part
# and frontier
    def decompose(self,cur,ts):
        vars,terms,matches,syms =reduce(lambda a,b: self.mmeq(a,b) ,ts,([],[],defaultdict(lambda :[]),set()))
        if len(syms)>1: raise Solver.ClashExeption(syms,ts,self.start_time)
        elif len(vars)>0: return (reduce(lambda a,b:  Var.union(a,b),vars),[(set(vars),terms)])
        else:
            sym =syms.pop()
            args,front=[None]*sym.arity,[]
            for x,y,z in map(lambda a: (a[0],*self.decompose(cur,a[1])),matches.items()):
                args[x]=Var.find(y)
                front.extend(z)
            return (sym(*args),front)


   #I am here trying to fix the issues with multiple occurances of variables
    def unify(self,problem):
        self.preprocess(problem)
        steps=0
        while len(self.var_reps)>0:
            if self.debug>2: self.print_current_step(steps,self.tosolve)
#Get the next multi-equation with zero occurances
            cur = self.var_reps.pop()
#Remove it from the to solve set
            self.tosolve.remove(cur)
#check if there are terms on the right side of the multiequation
            if cur.ts()!= []:
#decompose the terms on the right side of the multiequation to get
#the common part and frontier
                common,front = self.decompose(cur,cur.ts())
                if self.debug>2:
                    print("common: \n\t"+str(common))
                    print()
                    print("frontier: ")
#Finish compatification of the frontier,Partially done in during decomposition
# add multiequations to the zero occurance set if the variables have zero occurances
# always add the tosolve set incase they do not occur there
# add bindings for variables added to an eq class
#update tosolve some variables my have been updated
                self.solved.add((cur,common))
                for fvar,fterms in front:
                    vrep = Var.find(list(fvar)[0]) 
                    if self.debug>2: print("\t"+str(vrep.occs())+":{"+','.join([str(x) for x in fvar])+"}"+" =?= "+"{{"+','.join([str(x)for x in fterms])+"}}" )
                    vrep.ts().extend(fterms)
                    if vrep.occs() == 0: self.var_reps.add(vrep)
                    self.tosolve.add(vrep)
                    self.solved.update([(v,vrep) for v in fvar if  v != vrep])
                self.tosolve =set([Var.find(x) for x in self.tosolve])
                if self.debug>2:
                    print()
                    print("==========================================================")
            else:
                if self.debug>2:
                    print("==========================================================")
            steps+=1
#If var_reps is empty and tosolve is not then we have a cycle
        if len(self.tosolve)!=0: raise Solver.CycleException(self.tosolve,start_time=self.start_time)
        for vc in self.problemVars:
            for idx in self.problemVars[vc]:
                v = self.problemVars[vc][idx]
                if v!= Var.find(v):
                    self.solved.add((v,Var.find(v)))
        self.clear()
        return dict(self.solved), None

    def preprocess(self,problem):
        def insert(t):
            if t.vc in self.problemVars.keys() and not t.idx in self.problemVars[t.vc].keys(): self.problemVars[t.vc][t.idx] =t  
            elif not t.vc in self.problemVars.keys(): self.problemVars[t.vc] = {t.idx:t}
        def getvars(t):
            if type(t) is App:
                for x in t.args: getvars(x)
            elif type(t) is Var:
                insert(t)
                self.getrep(t).setocc(1)
         
        for x,y in problem:
            insert(x)
            if type(y) is Var: 
                insert(y)
                Var.union(self.getrep(x),self.getrep(y))
            else:
                self.getrep(x).terms.append(y) 
                getvars(y)

        for x,y in self.problemVars.items():
            for z,w in y.items():
                rep = Var.find(w)
                if rep.occ == 0: self.var_reps.add(rep)
                self.tosolve.add(rep)

    def clear(self):
        for x,y in self.problemVars.items():
            for w,z in y.items():
                z.reset()
        self.problemVars = {}
        self.var_reps = set()
        self.tosolve = set()
        self.solved =set()

    def print_current_step(self,steps,tosolve):
        print("Step ",str(steps)," of ",str(self.count))
        for x in tosolve: print("\t"+x.format())
        print()
