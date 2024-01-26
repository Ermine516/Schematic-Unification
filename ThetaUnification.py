from Term import *
from functools import reduce
from Solver import Solver
class ThetaUnification(Solver):
    class Configuration:
        def __init__(self,active,dom):
            self.active = active # Set of unification problems
            self.store = set() # Set of variable on left unification problems
            self.dom = [x.name for x in dom] # Set of excluded variable symbols
            self.recursions = set()
            self.seen = set()
            self.seenTrans = set()
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
            self.store.add(binding)
    
    def __init__(self,SchematicSubstitution=None,debug=0,start_time=-1):
        self.recursions=set()
        super().__init__(SchematicSubstitution,debug,start_time)
        
    def unify(self,problem):
        config = ThetaUnification.Configuration(problem,self.SchematicSubstitution.symbols)  

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
                 if x.vc in self.SchematicSubstitution.associated_classes[r.func.name].keys():
                    minval = self.SchematicSubstitution.associated_classes[r.func.name][x.vc]
                    if r.idx.number +minval <= x.idx: return True
            return False
        def existsseen(x,y):
            for p1,p2,p3 in config.seen:
                if  p2==x and p3==y: return True #isTerm(p1) and
            return False

        

    #Checks useful for the unification procedure
        isTerm = lambda a: not type(a) is Var and not type(a) is Rec
        isVarRec =lambda a:  type(a) is Var or  type(a) is Rec
        isRec = lambda a: type(a) is Rec
        isVar = lambda a: type(a) is Var
        unseen = lambda a: not a in config.seen
        stored = lambda a: a in config.store

    #Conditions for rules
        decomposition = lambda x,y:  unseen((x,x,y)) and isTerm(x) and isTerm(y) and x.func.name == y.func.name
        orient1 = lambda x,y: x!=y and (isVarRec(y) and isTerm(x)) and unseen((x,x,y))
        orient2 = lambda x,y: x!=y and isVarRec(x) and isVarRec(y) and not (y,x) in config.active
        transitivity = lambda x,y: lambda a: x!= a[1] and x!= y and a[0]==x and y!=a[1] and unseen((x,a[1],y)) and unseen((x,y,a[1])) 
        delete = lambda x,y: isTerm(x) and existsseen(x,y)
        store_T_R= lambda x,y: x != y and isVar(x) and  not stored((x,y)) and isRelevant((x,y))
        store_T_D= lambda x,y: isRec(x) and  not  isVar(y) and x != y and not stored((x,y))
        store_T_F= lambda x,y: x != y and isVar(x) and  not stored((x,y)) and isFutureRelevant(x) #and (isFutureRelevant(y) if  isVar(y) else True ) 

        clash = lambda x,y:  isTerm(x) and isTerm(y)  and x.func.name != y.func.name

    # Checks whether the given binding 'a' is relevent to the binding stored in the configuration
        #relevantCheck = lambda a: (lambda b,c: b or  ( a[0].occurs(c[1]) and isTerm(a[1]) ) or (not type(a[0]) is Rec and a[0]==c[0])) 
        relevantCheck = lambda a: (lambda b,c: b or a[0].occurs(c[1]) or a[1].occurs(c[0]) or (not type(a[0]) is Rec and a[0]==c[0])) 
        isRelevant = lambda a: reduce(relevantCheck(a),config.store,False)  

        change =True
        while change:
            updates=set()
            toRemove=set()
            change = False
            for x,y in config.active:
    #Delete Rule
                if delete(x,y):
                   toRemove.add((x,y))
                   change =True
    # Decomposition Rule
                if decomposition(x,y):
                    if self.debug>4: print(f"\t Decomposition: {x} =?= {y}")
                    config.seen.add((x,x,y))
                    toRemove.add((x,y))
                    updates.update([(x1,y1) for x1,y1 in list(zip(x.args,y.args)) if unseen((x1,x1,y1))])
                    change =True
    # symmetry Rule
                elif orient1(x,y):
                    if self.debug>4: print(f"\t Orient 1: {x} =?= {y}")
                    config.seen.update([(x,x,y)])
                    toRemove.add((x,y))
                    updates.add((y,x))
                    change =True
    # symmetry Rule
                elif orient2(x,y):
                    if self.debug>4: print(f"\t Orient 2: {x} =?= {y}")
                    config.seen.update([(x,x,y)])
                    config.seen.update([(y,y,x)])
                    updates.add((y,x))
                    change =True
    # Reflexivity Rule
                elif x==y:
                    if self.debug>4: print(f"\t Reflexivity: {x} =?= {y}")
                    config.seen.add((x,x,y))
                    toRemove.add((x,y))
                    change =True
    # Clash Rule
                elif clash(x,y):
                    raise Solver.ClashExeption(x.func.name,[x,y],self.start_time)
    # Store-Θ-R Rule
                elif store_T_R(x,y):
                    if self.debug>4: print(f"\t Store-Θ-R: {x} =?= {y}")
                    config.updateStore((x,y))
                    change =True
    # Store-Θ-D Rule
                elif store_T_D(x,y):
                    if self.debug>4: print(f"\t Store-Θ-D: {x} =?= {y}")
                    config.updateStore((x,y))
                    change =True
    # Store-Θ-F Rule
                elif  store_T_F(x,y):
                    if self.debug>4: print(f"\t Store-Θ-F: {x} =?= {y}")
                    config.updateStore((x,y))
                    change =True
    #Transitivity           
                else:
                    for x1,y1 in filter(transitivity(x,y),config.active):   
                        if self.debug>4: print(f"\t Transitivity: {x} =?= {y} and {x1} =?= {y1}")
                        config.seen.add((x,y,y1))
                        config.seen.add((x,y1,y))
                        updates.add((y,y1))
                        change =True

            config.active = set(filter(lambda a: not a in toRemove, config.active))
            config.active.update(updates)
        
        if self.debug>4: 
            print()
        
        self.recursions=config.recursions
        return config.store, config.active

