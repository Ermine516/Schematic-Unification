from Term import *
from Solver import Solver
from UnificationProblem import UnificationEquation as UEq
from UnificationProblem import UnificationProblem as UProb

class Configuration:
        active      : UProb
        store       : UProb
        storeLen    : int
        recursions  : set[Rec]
        seen        : set[Tuple[Term,Term,Term]]
        updates     : set[UEq]
        toRemove    : set[UEq]
        
        def __init__(self,active,schSubs):
            self.active = active # Set of unification problems
            self.store = UProb() # Set of variable on left unification problems
            self.storeLen = len(self.store)
            self.store.schSubs = schSubs
            self.recursions = set()
            self.seen = set()
            self.updates=set()
            self.toRemove=set()

        def __str__(self) -> str:
            exset = str([x.name for x in  self.store.schSubs.symbols])
            ret=f"Active({exset}):\n"
            for x,y in self.active: ret+=f"\t {x} =?= {y}\n"
            ret+=f"Store({exset}):\n"
            for x,y in self.store: ret+=f"\t {x} =?= {y}\n"
            return ret
        
        def addSeen(self, *args:Tuple[UEq])-> None:
            if len(args)==1:
                self.seen.add((args[0][0],args[0][0],args[0][1]))
            elif len(args)==2:
                self.seen.add((args[0][0],args[0][1],args[1][1]))
                self.seen.add((args[0][0],args[1][1],args[0][1]))
            

        def final(self)-> bool:
            if len(self.seen)!=0 and len(self.updates)+len(self.toRemove)== 0 and self.storeLen==len(self.store): return False
            self.active = set(filter(lambda a: not a in self.toRemove, self.active))
            self.active.update(self.updates)
            self.updates=set()
            self.toRemove=set()
            self.storeLen=len(self.store)
            return True
            
        def updateStore(self,binding:UEq) -> None:
            self.recursions.update(binding.recs())
            self.store+binding

        def isFutureRelevant(self,x:Term) -> bool:
            for r in self.recursions:
                 if self.store.schSubs.isFutureRelevant(r,x): return True
            return False
        
        def existsseen(self,uEq:UEq) -> bool:
            for p1,p2,p3 in self.seen:
                if  p1==uEq[0] and p2==uEq[0] and p3==uEq[1]: return True
            return False
        
        def isRelevant(self,a:UEq) -> bool:
            for b in self.store:
                if b[1].occurs(a[0]) or b[0]==a[1] or (not type(a[0]) is Rec and a[0]==b[0]):
                    return True
            return False
        
class ThetaUnification(Solver):

    def __init__(self,SchematicSubstitution=None,debug=0,start_time=-1):
        super().__init__(SchematicSubstitution,debug,start_time)
        
    def unify(self,problem:UProb)-> Tuple[UProb,UProb,set[Rec]]:
        config = Configuration(problem,self.SchematicSubstitution)  
#Checks useful for the unification procedure
        isTerm = lambda a: not type(a) is Var and not type(a) is Rec
        isVarRec =lambda a:  type(a) is Var or  type(a) is Rec
        isRec = lambda a: type(a) is Rec
        isVar = lambda a: type(a) is Var
        unseen = lambda a: not a in config.seen
        stored = lambda a: a in config.store
        anno = lambda a: (uEq[0],uEq[0],uEq[1])
#Conditions for rules
        delete = lambda uEq: isTerm(uEq[0]) and config.existsseen(uEq)
        decomposition = lambda uEq:  unseen(anno(uEq)) and isTerm(uEq[0]) and isTerm(uEq[1]) and uEq[0].func.name == uEq[1].func.name
        orient1 = lambda uEq: not uEq.reflexive() and (isVarRec(uEq[1]) and isTerm(uEq[0])) and unseen(anno(uEq))
        orient2 = lambda uEq: not uEq.reflexive() and isVarRec(uEq[0]) and isVarRec(uEq[1]) and not uEq.flip() in config.active
        clash = lambda uEq:  isTerm(uEq[0]) and isTerm(uEq[1])  and uEq[0].func.name != uEq[1].func.name
        store_T_R= lambda uEq: not uEq.reflexive() and isVar(uEq[0]) and  not stored(uEq) and config.isRelevant(uEq)
        store_T_D= lambda uEq: isRec(uEq[0]) and  not  isVar(uEq[1]) and not uEq.reflexive() and not stored(uEq)
        store_T_F= lambda uEq: not uEq.reflexive() and isVar(uEq[0]) and  not stored(uEq) and config.isFutureRelevant(uEq[0])
        transitivity = lambda uEq: lambda a: isVar(uEq[0]) and isVar(a[0]) and uEq[0]!= a[1] and not uEq.reflexive() and a[0]==uEq[0] and uEq[1]!=a[1] and unseen((uEq[0],a[1],uEq[1])) and unseen((uEq[0],uEq[1],a[1])) 

# Checks whether the given binding 'a' is relevent to the binding stored in the configuration
        while config.final():
            for uEq in config.active:
                if delete(uEq):
                    if self.debug>4: print(f"\t Delete: {str(uEq)}")
                    config.toRemove.add(uEq.duplicate())
                elif decomposition(uEq):
                    if self.debug>4: print(f"\t Decomposition: {str(uEq)}")
                    config.addSeen(uEq)
                    config.addSeen(uEq.flip())
                    config.toRemove.add(uEq.duplicate())
                    config.updates.update([UEq(x1,y1) for x1,y1 in list(zip(uEq[0].args,uEq[1].args)) if unseen((x1,x1,y1))])
                elif orient1(uEq):
                    if self.debug>4: print(f"\t Orient 1: {str(uEq)}")
                    config.addSeen(uEq)
                    config.toRemove.add(uEq.duplicate())
                    config.updates.add(uEq.flip())
                elif orient2(uEq):
                    if self.debug>4: print(f"\t Orient 2: {str(uEq)}")
                    config.addSeen(uEq)
                    config.addSeen(uEq.flip())
                    config.updates.add(uEq.flip())
                elif uEq.reflexive():
                    if self.debug>4: print(f"\t Reflexivity: {str(uEq)}")
                    config.addSeen(uEq)
                    config.toRemove.add(uEq)
                elif clash(uEq):
                    raise Solver.ClashExeption(uEq[0].func.name,uEq,self.start_time)
                elif store_T_R(uEq):
                    if self.debug>4: print(f"\t Store-Θ-R: {str(uEq)}")
                    config.updateStore(uEq)
                    config.addSeen(uEq)
                elif store_T_D(uEq):
                    if self.debug>4: print(f"\t Store-Θ-D: {str(uEq)}")
                    config.updateStore(uEq)
                    config.addSeen(uEq)
                elif  store_T_F(uEq):
                    if self.debug>4: print(f"\t Store-Θ-F: {str(uEq)}")
                    config.updateStore(uEq)
                    config.addSeen(uEq)
                else:
                        for uEq2 in list(filter(transitivity(uEq),config.active)):   
                            if self.debug>4: print(f"\t Transitivity: {str(uEq)} and {str(uEq2)}")
                            config.addSeen(uEq,uEq2)
                            config.updates.add(UEq(uEq[1],uEq2[1]))
        if self.debug>4: print()
        return config.store, config.active, config.recursions