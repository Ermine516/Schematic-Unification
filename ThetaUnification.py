from collections import defaultdict
from enum import Enum
from SchematicSubstitution import SchematicSubstitution
from Term import *
from Solver import Solver
from UnificationProblem import UnificationEquation as UEq
from UnificationProblem import UnificationProblem as UProb

class Configuration:
        active      : UProb
        store       : UProb
        storeLen    : int
        recursions  : set[Rec]
        updates     : set[UEq]

        isTerm = lambda a: not  issubclass(type(a),VarObjects) 
        isVarRec =lambda a:   issubclass(type(a),VarObjects) 
        isRec = lambda a: type(a) is Rec
        isVar = lambda a: type(a) is Var
        stored = lambda config,a: a in config.store
        
        clash = lambda uEq:  Configuration.isTerm(uEq[0]) and Configuration.isTerm(uEq[1])  and uEq[0].func != uEq[1].func
        cycle_F =  lambda config: lambda uEq: Configuration.isVar(uEq[0]) and (config.isFutureRelevantto(uEq[0],uEq[1]))
        orient1 = lambda uEq: Configuration.isVarRec(uEq[1]) and Configuration.isTerm(uEq[0])
        decomposition = lambda uEq:  Configuration.isTerm(uEq[0]) and Configuration.isTerm(uEq[1]) and uEq[0].func == uEq[1].func
        orient2 = lambda config: lambda uEq: Configuration.isVarRec(uEq[0]) and Configuration.isVarRec(uEq[1]) and not uEq.flip() in config.orient2check 
        store_T_R= lambda config, uEq: Configuration.isVar(uEq[0]) and config.isRelevant(uEq)
        store_T_D= lambda  uEq:  Configuration.isRec(uEq[0]) and  not Configuration.isVar(uEq[1]) 
        store_T_F= lambda config, uEq:   Configuration.isVar(uEq[0])  and config.isFutureRelevant(uEq[0]) 
        store = lambda config, uEq:  Configuration.store_T_R(config,uEq) or Configuration.store_T_D(uEq) or Configuration.store_T_F(config,uEq) 

        def __init__(self,active:UProb,schSubs:SchematicSubstitution,start_time = -1):
            self.active = active.prob # Set of unification problems
            self.store = UProb() # Set of variable on left unification problems
            self.store.schSubs = schSubs # The schematic substitution associated with the unfication problem
            self.recursions = set() # used for checking if a variable is future relevant
            self.updates=active.prob # used to update the store and active set after a pass through the loop
            self.relvars = set()
            self.vardict =defaultdict(set)
            self.transPairs=set()
            self.orient1set = []
            self.orient2set = []
            self.orient2check =set()
            self.decompositionset = []
            self.storeSet = []
            self.start_time=start_time
            if clashable:= list(filter( Configuration.clash,self.active)): raise Solver.ClashExeption(clashable[0][0].func.name,clashable[0],self.start_time)
# Optimization 
            if cycleFable := list(filter(Configuration.cycle_F(self),self.active)): raise Solver.CycleException(cycleFable[0],f"{str(cycleFable[0][0])} is future relevant to {str(cycleFable[0][1])}",self.start_time)
            self.processState()
            
# magic methods
        def __str__(self) -> str:
            exset = str([x.name for x in  self.store.schSubs.symbols])
            ret=f"Active({exset}):\n"
            for x,y in self.active: ret+=f"\t {x} =?= {y}\n"
            ret+=f"Store({exset}):\n"
            for x,y in self.store: ret+=f"\t {x} =?= {y}\n"
            return ret

 # Class Specific Methods 
        def processState(self):
            if clashable:= list(filter( Configuration.clash,self.updates)): raise Solver.ClashExeption(clashable[0][0].func.name,clashable[0],self.start_time)
# Optimization 
            if cycleFable := list(filter(Configuration.cycle_F(self),self.updates)): raise Solver.CycleException(cycleFable[0],f"{str(cycleFable[0][0])} is future relevant to {str(cycleFable[0][1])}",self.start_time)
            self.orient1set.extend(list(filter(Configuration.orient1, self.updates)))
            self.decompositionset.extend(list(filter(Configuration.decomposition, self.updates)))
            self.orient2set.extend(list(filter(Configuration.orient2(self), self.updates)))
            for uEq in filter(lambda uEq:  issubclass(type(uEq[0]),VarObjects) and not uEq in self.vardict[uEq[0]] ,self.updates):
                    self.transPairs.update([(uEq,uEq1) for uEq1 in self.vardict[uEq[0]] ])                     
                    self.vardict[uEq[0]].add(uEq)
            self.updates=set()
                    
        def update(self):
            self.updates = set(filter(lambda uEq: not uEq.reflexive() ,self.updates))
            self.active.update(self.updates)
            self.processState()
        
        def final(self)-> bool:
            return  False if len(self.transPairs)==0 and len(self.orient1set)==0 and len(self.orient2set)==0 and len(self.decompositionset)==0 else True
        
        def finalStore(self)-> bool:
            self.storeSet = set(filter(lambda a: Configuration.store(self,a), self.active))
            return False if len(self.storeSet)==0 else True
            
        
        def isFutureRelevant(self,x:Term) -> bool:
            return True if [ r for r in self.recursions if self.store.schSubs.isFutureRelevant(r,x)] else False
        
        def isFutureRelevantto(self,x:VarObjects,t:Term) -> bool:
            return True if [ r for r in t.vos(Rec) if self.store.schSubs.isFutureRelevant(r,x)] else False
    
        def isRelevant(self,a:UEq) -> bool:
            return True if [v for v in self.relvars if a[0]==v] else False 

        
class ThetaUnification(Solver):

    def __init__(self,SchematicSubstitution:SchematicSubstitution=None,debug:int=0,start_time:float=-1):
        super().__init__(SchematicSubstitution,debug,start_time)
        
    def unify(self,problem:UProb)-> Tuple[UProb,UProb,set[Rec]]:
        config = Configuration(problem,self.SchematicSubstitution,self.start_time)  
        while config.final():
            while config.orient1set !=  []:
                uEq =config.orient1set.pop()
                try:
                    config.active.remove(uEq)
                except KeyError as e:
                    continue               
                config.updates.add(uEq.flip())            
                if self.debug>4: print(f"\t Orient 1: {str(uEq)}")
            config.update()
            while config.decompositionset != []:
                uEq =config.decompositionset.pop()
                try:
                    config.active.remove(uEq)
                except KeyError as e:
                    continue
                config.updates.update([UEq(x1,y1) for x1,y1 in list(zip(uEq[0].args,uEq[1].args)) ]) 
                if self.debug>4: print(f"\t Decomposition: {str(uEq)}")
            config.update()
            while config.orient2set != []:
                uEq =config.orient2set.pop()
                config.orient2check.update([uEq,uEq.flip])
                config.updates.add(uEq.flip())
                if self.debug>4: print(f"\t Orient 2: {str(uEq)}")
            config.update()
            while config.transPairs != set():
                uEq1,uEq2 = config.transPairs.pop()
                config.updates.add(UEq(uEq1[1],uEq2[1]))
                if self.debug>4: print(f"\t Transitivity: {str(uEq1)} and {str(uEq2)}")
            config.update()

        while config.finalStore(): 
                while config.storeSet:
                    uEq =config.storeSet.pop()
                    config.recursions.update(uEq.vos(Rec))
                    config.active.remove(uEq)
                    config.store+= uEq
                    config.relvars.update(uEq.vos(VarObjects))
                    if self.debug>4: print(f"\t Store-Θ: {str(uEq)}")
        if self.debug>4: print()
        return config.store, config.active.union(config.store.prob)