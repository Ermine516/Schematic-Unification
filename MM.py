from __future__ import annotations
from typing import Tuple 
from collections import defaultdict
from Namer import Namer
from SchematicSubstitution import SchematicSubstitution
from Solver import Solver
from functools import reduce
from Term import *
from UnificationProblem import *
from Substitution import Substitution
from UnionFindNode import UnionFindNode



# Implements the  Martelli and Montanari unification algorithm
class MM(Solver):
    probVarsDict : dict[UnionFindNode] # Stores variables occuring in the problem as UnionFindNodes
    probVarsSet  : set[UnionFindNode]  # Stores variables occuring in the problem as UnionFindNodes
    var_reps     : set[UnionFindNode]  # Stores the representatives of each variable EQ class
    tosolve      : set[UnionFindNode]  # Stores EQ classes with no occurances
    count        : int                 # current problem being solved

    def __init__(self:MM,SchematicSubstitution:SchematicSubstitution=None,debug:int=0,start_time:float=-1):
       self.probVarsDict={}
       self.probVarsSet=set()
       self.var_reps = set()
       self.tosolve = set()
       self.solved =set()
       self.count = 0
       super().__init__(SchematicSubstitution,debug,start_time)
    
    def getrep(self:MM,t:VarObjects)-> UnionFindNode:
        return self.probVarsDict[t.vc][t.idx].find()
    
    def toUnifProb(self:MM) -> UnificationProblem:
        ret = UnificationProblem()
        for x in self.tosolve:
            for y in x.terms: 
                ret.addEquation(x,y,str(x.occ))
        return ret        
    
    def clear(self:MM)-> None:
        self.probVarsDict = {}
        self.probVarsSet = set()
        self.var_reps = set()
        self.tosolve = set()
        self.solved =set()

    def insert(self:MM,t:VarObjects,count:int)->UnionFindNode:
            if t.vc in self.probVarsDict.keys() and not t.idx in self.probVarsDict[t.vc].keys(): 
                uft=UnionFindNode(t) 
                self.probVarsDict[t.vc][t.idx] = uft
                self.probVarsSet.add(uft)
            elif not t.vc in self.probVarsDict.keys(): 
                uft=UnionFindNode(t) 
                self.probVarsDict[t.vc] = {t.idx:uft} 
                self.probVarsSet.add(uft)
            uft=self.probVarsDict[t.vc][t.idx].find()
            uft.setocc(count)
            return uft
    
# We assume all problems in problem have the form
# s=?=t where s is a variable. Otherwise use 
# elaboratePreprocess
    def preprocess(self:MM,problem:UnificationProblem)-> None:
        self.clear() 
        for x,y in problem:
            if issubclass(type(y),VarObjects): 
                self.insert(x,0).union(self.insert(y,0))
            else:
                self.insert(x,0).ts().append(y) 
                for w in y.vosOcc(VarObjects): self.insert(w,1)
        for x in self.probVarsSet:
            if x.find().occ == 0: self.var_reps.add(x.find())
            self.tosolve.add(x.find())

    def elaboratePreprocess(self:MM,problem:UnificationProblem)-> None:
        self.clear() 
        fvar = Namer("MM").current_name()
        for i,ue in enumerate(problem):
            pVar = self.insert(Var(fvar,i),0)
            if issubclass(type(ue[0]), VarObjects): 
                pVar = pVar.union(self.insert(ue[0],0))
            else: 
                pVar.ts().append(ue[0])
                for w in ue[0].vosOcc(VarObjects): self.insert(w,1)

            if issubclass(type(ue[1]), VarObjects): 
                pVar = pVar.union(self.insert(ue[1],0))
            else: 
                pVar.ts().append(ue[1])
                for w in ue[1].vosOcc(VarObjects): self.insert(w,1)
        for x in self.probVarsSet:
            if x.find().occ == 0: self.var_reps.add(x.find())
            self.tosolve.add(x.find())
        
# mm has the structure (variables,terms,subterm at position,Symbols found)
    def mmeq(self:MM,mm:Tuple[list[VarObjects],list[Term],list[list[Term]],set[Func]],term:Term)->Tuple[list[VarObjects],list[Term],list[list[Term]],set[Func]]:
        vars,terms,matches,syms = mm
        if issubclass(type(term), VarObjects):
            asVar = self.getrep(term)
# remove occurances of variables found during decomposition
            asVar.setocc(-1)
            vars.append(asVar)
        elif type(term) is App:
            terms.append(term)
            syms.add(term.func)
            for x in range(0,term.func.arity): matches[x].append(term.args[x])
        return (vars,terms,matches,syms)

    
# M and M decomposition function
# decomposes the terms and builds the common part
# and frontier
    def decompose(self:MM,cur:UnionFindNode,ts:list[Term])-> Term:
        vars,terms,matches,syms =reduce(lambda a,b: self.mmeq(a,b) ,ts,([],[],defaultdict(lambda :[]),set()))
        if len(syms)>1: raise Solver.ClashExeption(syms,ts,self.start_time)
        elif len(vars)>0: return (reduce(lambda a,b:  a.union(b),vars),[(set(vars),terms)])
        else:
            sym =syms.pop()
            args,front=[None]*sym.arity,[]
            for x,y,z in map(lambda a: (a[0],*self.decompose(cur,a[1])),matches.items()):
                args[x]=y.find() if type(y) is UnionFindNode else y
                front.extend(z)
            return (sym(*args),front)


    def unify(self:MM,problem:UnificationProblem,stdMode:bool=False)-> Substitution:
        if stdMode: self.elaboratePreprocess(problem)
        else: self.preprocess(problem)
        steps=0
        while len(self.var_reps)>0:
            if self.debug>3: self.print_current_step(steps,self.tosolve)
#Get the next multi-equation with zero occurances
            cur = self.var_reps.pop()
#Remove it from the to solve set
            self.tosolve.remove(cur)
#check if there are terms on the right side of the multiequation
            if cur.ts()!= []:
#decompose the terms on the right side of the multiequation to get
#the common part and frontier
                common,front = self.decompose(cur,cur.ts())
                if self.debug>3:
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
                    vrep = list(fvar)[0].find() 
                    if self.debug>3: print("\t"+str(vrep.occs())+":{"+','.join([str(x) for x in fvar])+"}"+" =?= "+"{{"+','.join([str(x)for x in fterms])+"}}" )
                    vrep.ts().extend(fterms)
                    if vrep.occs() == 0: self.var_reps.add(vrep)
                    self.tosolve.add(vrep)
                    self.solved.update([(v,vrep) for v in fvar if  v != vrep])
                self.tosolve =set([x.find() for x in self.tosolve])
                if self.debug>3: print("\n==========================================================")
            else:
                if self.debug>3: print("==========================================================")
            steps+=1
#If var_reps is empty and tosolve is not then we have a cycle
        if len(self.tosolve)!=0:
            raise Solver.CycleException(self.toUnifProb(),start_time=self.start_time)
        for vc in self.probVarsDict:
            for idx in self.probVarsDict[vc]:
                v = self.probVarsDict[vc][idx]
                if v!= v.find():
                    self.solved.add((v,v.find()))    
        unifier = self.buildUnifier()
        self.clear()
        return unifier, None
    

    def buildUnifier(self:MM)-> Substitution:
        def clean(t):
            if type(t) is UnionFindNode:
                return t.find().val
            elif type(t) is App:
                return t.func(*map(lambda a:clean(a), t.args))
            else: 
                return t
        eqclasses = {}
        maxIdx = {}
        unifier = Substitution()
        for v in self.probVarsSet:
            if not v.find().val in eqclasses.keys(): 
                eqclasses[v.find().val]=set([v.val,v.find().val])
                maxIdx[v.find().val] = v.val if v.val.idx == max(v.val.idx,v.find().val.idx) else v.find().val
            else:  
                eqclasses[v.find().val].add(v.val)
                maxIdx[v.find().val] = v.val if v.val.idx == max(v.val.idx, maxIdx[v.find().val].idx) else  maxIdx[v.find().val]
        for v,t in self.solved:
            v1,t1 = v.val,clean(t)
            if len(v.terms) != 0:
                unifier += (maxIdx[v.find().val],t1)
            for b in eqclasses[v.find().val]:
                unifier += (b,maxIdx[v.find().val])
        
        return unifier
   



    def print_current_step(self:MM,steps:int,tosolve:set[UnionFindNode])-> None:
        print("Step ",str(steps)," of ",str(self.count))
        for x in tosolve: print("\t"+x.format())
        print()

  

