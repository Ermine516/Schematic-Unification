from Term import *
from functools import reduce
from Solver import Solver
from UnificationProblem import UnificationEquation as UEq
from UnificationProblem import UnificationProblem as UProb

class ThetaUnification(Solver):
    class Configuration:
        def __init__(self,active):
            self.active = active # Set of unification problems
            self.store = UProb() # Set of variable on left unification problems
            self.store.schSubs = active.schSubs

            self.dom = [x.name for x in  self.store.schSubs.symbols] # Set of Domain variable symbols
            self.recursions = set()
            self.seen = set()
        def addSeen(self, *args):
            if len(args)==1:
                self.seen.add((args[0][0],args[0][0],args[0][1]))
            elif len(args)==2:
                self.seen.add((args[0][0],args[0][1],args[1][1]))
                self.seen.add((args[0][0],args[1][1],args[0][1]))

        def __str__(self):
            exset = str([str(x) for x in self.dom])
            ret=f"Active({exset}):\n"
            for x,y in self.active:
                ret+=f"\t {x} =?= {y}\n"
            ret+=f"Store({exset}):\n"
            for x,y in self.store:
                ret+=f"\t {x} =?= {y}\n"
            return ret

        def updateStore(self,binding):
            def findRecursions(binding):
                def checkForRecs(t):
                    if type(t) is App:
                        ret =set()
                        for x in t.args: 
                            ret.update(checkForRecs(x))
                        return ret
                    elif type(t) is Var:
                        return set()
                    else:
                        return set([t]) 

                ret = checkForRecs(binding[1])
                if type(binding[0]) is Rec: 
                    ret.add(binding[0])
                return ret

            self.recursions.update(findRecursions(binding))
            self.store+binding
    
    def __init__(self,SchematicSubstitution=None,debug=0,start_time=-1):
        self.recursions=set()
        super().__init__(SchematicSubstitution,debug,start_time)
        
    def unify(self,problem):
        config = ThetaUnification.Configuration(problem)  
        def recCycle(x,y):
            if type(y) is App:
                for z in y.args:
                    if recCycle(x,z): return True
            elif type(y) is Var:
                return False
            else:
                return True if type(y) is Rec and x.func.name == y.func.name else False
        def isFutureRelevant(x):
            for r in config.recursions:
                 if self.SchematicSubstitution.isFutureRelevant(r,x): return True
            return False
        def existsseen(uEq):
            for p1,p2,p3 in config.seen:
                if  p1==uEq[0] and p2==uEq[0] and p3==uEq[1]: return True
            return False

#Checks useful for the unification procedure
        isTerm = lambda a: not type(a) is Var and not type(a) is Rec
        isVarRec =lambda a:  type(a) is Var or  type(a) is Rec
        isRec = lambda a: type(a) is Rec
        isVar = lambda a: type(a) is Var
        unseen = lambda a: not a in config.seen
        stored = lambda a: a in config.store
        anno = lambda a: (uEq[0],uEq[0],uEq[1])
#Conditions for rules
        delete = lambda uEq: isTerm(uEq[0]) and existsseen(uEq)
        decomposition = lambda uEq:  unseen(anno(uEq)) and isTerm(uEq[0]) and isTerm(uEq[1]) and uEq[0].func.name == uEq[1].func.name
        orient1 = lambda uEq: not uEq.reflexive() and (isVarRec(uEq[1]) and isTerm(uEq[0])) and unseen(anno(uEq))
        orient2 = lambda uEq: not uEq.reflexive() and isVarRec(uEq[0]) and isVarRec(uEq[1]) and not uEq.flip() in config.active
        clash = lambda uEq:  isTerm(uEq[0]) and isTerm(uEq[1])  and uEq[0].func.name != uEq[1].func.name
        store_T_R= lambda uEq: not uEq.reflexive() and isVar(uEq[0]) and  not stored(uEq) and isRelevant(uEq)
        store_T_D= lambda uEq: isRec(uEq[0]) and  not  isVar(uEq[1]) and not uEq.reflexive() and not stored(uEq)
        store_T_F= lambda uEq: not uEq.reflexive() and isVar(uEq[0]) and  not stored(uEq) and isFutureRelevant(uEq[0])
        transitivity = lambda uEq: lambda a: isVar(uEq[0]) and isVar(a[0]) and uEq[0]!= a[1] and not uEq.reflexive() and a[0]==uEq[0] and uEq[1]!=a[1] and unseen((uEq[0],a[1],uEq[1])) and unseen((uEq[0],uEq[1],a[1])) 

# Checks whether the given binding 'a' is relevent to the binding stored in the configuration
        relevantCheck = lambda a: (lambda b,c: b or c[1].occurs(a[0]) or c[0].occurs(c[1]) or (not type(a[0]) is Rec and a[0]==c[0])) 
        isRelevant = lambda a: reduce(relevantCheck(a),config.store,False)  
        speseen=set()
        change =True
        while change:
            updates=set()
            toRemove=set()
            change = False
            for uEq in config.active:
    #Delete Rule
                if delete(uEq):
                    if self.debug>4: print(f"\t Delete: {str(uEq)}")
                    toRemove.add(uEq.duplicate())
                    change =True
    # Decomposition Rule
                elif decomposition(uEq):
                    if self.debug>4: print(f"\t Decomposition: {str(uEq)}")
                    config.addSeen(uEq)
                    config.addSeen(uEq.flip())
                    toRemove.add(uEq.duplicate())
                    updates.update([UEq(x1,y1) for x1,y1 in list(zip(uEq[0].args,uEq[1].args)) if unseen((x1,x1,y1))])
                    change =True
    # symmetry Rule
                elif orient1(uEq):
                    if self.debug>4: print(f"\t Orient 1: {str(uEq)}")
                    config.addSeen(uEq)
                    toRemove.add(uEq.duplicate())
                    updates.add(uEq.flip())
                    change =True
    # symmetry Rule
                elif orient2(uEq):
                    if self.debug>4: print(f"\t Orient 2: {str(uEq)}")
                    config.addSeen(uEq)
                    config.addSeen(uEq.flip())
                    updates.add(uEq.flip())
                    change =True
    # Reflexivity Rule
                elif uEq.reflexive():
                    if self.debug>4: print(f"\t Reflexivity: {str(uEq)}")
                    config.addSeen(uEq)
                    toRemove.add(uEq)
                    change =True
    # Clash Rule
                elif clash(uEq):
                    raise Solver.ClashExeption(uEq[0].func.name,uEq,self.start_time)
    # Store-Θ-R Rule
                elif store_T_R(uEq):
                    if self.debug>4: print(f"\t Store-Θ-R: {str(uEq)}")
                    config.updateStore(uEq)
                    change =True
    # Store-Θ-D Rule
                elif store_T_D(uEq):
                    if self.debug>4: print(f"\t Store-Θ-D: {str(uEq)}")
                    config.updateStore(uEq)
                    change =True
    # Store-Θ-F Rule
                elif  store_T_F(uEq):
                    if self.debug>4: print(f"\t Store-Θ-F: {str(uEq)}")
                    config.updateStore(uEq)
                    change =True
    #Transitivity           
                else:
                    for uEq2 in filter(transitivity(uEq),config.active):   
                        if self.debug>4: print(f"\t Transitivity: {str(uEq)} and {str(uEq2)}")
                        config.addSeen(uEq,uEq2)
                        updates.add(UEq(uEq[1],uEq2[1]))
                        change =True
            config.active = set(filter(lambda a: not a in toRemove, config.active))
            config.active.update(updates)
        if self.debug>4: print()
        self.recursions=config.recursions
        return config.store, config.active, config.recursions


