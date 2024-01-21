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
    
    def __init__(self,SchematicSubstitution=None,debug=0):
        self.recursions=set()
        super().__init__(SchematicSubstitution,debug)
        
    def unify(self,problem):
        def isFutureRelevant(x):
            for r in config.recursions:
                 if x.vc in self.SchematicSubstitution.associated_classes[r.func.name].keys():
                    minval = self.SchematicSubstitution.associated_classes[r.func.name][x.vc]
                    if r.idx.number +minval < x.idx: return True
            return False

        config = ThetaUnification.Configuration(problem,self.SchematicSubstitution.symbols)  
        

    #Checks useful for the unification procedure
        isTerm = lambda a: not type(a) is Var and not type(a) is Rec
        isRec = lambda a: type(a) is Rec
        isVar = lambda a: type(a) is Var
        unseen = lambda a: not a in config.seen
        stored = lambda a: a in config.store

    #Conditions for rules
        decomposition = lambda x,y:  unseen((x,y)) and isTerm(x) and isTerm(y) and x.func.name == y.func.name
        symmetry = lambda x,y: x!=y and unseen((y,x)) and (isVar(y) or (isRec(y) and isTerm(x)))
        clash = lambda x,y:  isTerm(x) and isTerm(y)  and x.func.name != y.func.name
        transitivity = lambda x,y: lambda a: a[0]==x and y!=a[1] and unseen((a[1],y)) and unseen((y,a[1])) 
    # Checks whether the given binding 'a' is relevent to the binding stored in the configuration
        relevantCheck = lambda a: (lambda b,c: b or a[0].occurs(c[1]) or a[1].occurs(c[0]) or (not type(a[0]) is Rec and a[0]==c[0])) 
        isRelevant = lambda a: reduce(relevantCheck(a),config.store,False)  

        change =True
        while change:
            updates=set()
            toRemove=set()
            change = False
            for x,y in config.active:

    # Removes unification constraints which have been seen before and have a term on the left side
                if not unseen((x,y)) and isTerm(x):
                   toRemove.add((x,y))
                   change =True
    # Decomposition Rule
                elif decomposition(x,y):
                    if self.debug >2: print(f"\t Decomposition: {x} =?= {y}")
                    config.seen.add((x,y))
                    toRemove.add((x,y))
                    updates.update([bind for bind in list(zip(x.args,y.args)) if unseen(bind)])
                    change =True
    # symmetry Rule
                elif symmetry(x,y):
                    if self.debug >2: print(f"\t Symmetry: {x} =?= {y}")
                    config.seen.update([(x,y),(y,x)])
                    if isTerm(x): toRemove.add((x,y))
                    updates.add((y,x))
                    change =True
    # Reflexivity Rule
                elif x==y:
                    if self.debug >2: print(f"\t Reflexivity: {x} =?= {y}")
                    config.seen.add((x,y))
                    toRemove.add((x,y))
                    change =True
    # Clash Rule
                elif clash(x,y):
                    raise Solver.ClashExeption(x.func.name,[x,y])
                    change =True
    # Store-Θ-R Rule
                elif x != y and isVar(x) and  not stored((x,y)) and isRelevant((x,y)):
                    if self.debug >2: print(f"\t Store-Θ-R: {x} =?= {y}")
                    config.updateStore((x,y))
                    change =True
    # Store-Θ-D Rule
                elif isRec(x) and  not  isVar(y) and x != y and not stored((x,y)):
                    if self.debug >2: print(f"\t Store-Θ-D: {x} =?= {y}")
                    config.updateStore((x,y))
                    change =True
    # Store-Θ-F Rule
                elif  x != y and isVar(x) and  not stored((x,y)) and isFutureRelevant(x):
                    if self.debug >2: print(f"\t Store-Θ-F: {x} =?= {y}")
                    config.updateStore((x,y))
                    change =True
    #Transitivity           
                else:
                    for x1,y1 in filter(transitivity(x,y),config.active):   
                        if self.debug >2: print(f"\t Transitivity: {x} =?= {y} and {x1} =?= {y1}")
                        updates.add((y,y1))
                        change =True

            config.active = set(filter(lambda a: not a in toRemove, config.active))
            config.active.update(updates)
        
        if self.debug >2: 
            print()
        
        self.recursions=config.recursions
        return config.store, config.active

