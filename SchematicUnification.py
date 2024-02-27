from Solver import Solver
from SubProblemStack import *
from Term import *
from SchematicSubstitution import *
from Namer import *
from ThetaUnification import ThetaUnification
from MM import MM 
import time

class SchematicUnification:

    def __init__(self,UnifProb,schSubs,debug=0):
        self.debug = debug
        self.foSolver = MM(schSubs,debug)
        self.SchSolver = ThetaUnification(schSubs,debug)
        self.count = 0
        self.SchematicSubstitution = schSubs
        self.subproblems = SubProblemStack(UnifProb,schSubs,debug)
        self.irrelevant = UnificationProblem()

    def unif(self,start_time=-1):
        self.foSolver.setTime(start_time)
        self.SchSolver.setTime(start_time)
        if self.debug >0: self.print_initial_problem()
        try:
            while self.subproblems.Open(start_time):
                self.update_subproblems(self.unify_current())
                self.update()
        except Solver.CycleException as e:
            return e.handle(self.debug)
        except Solver.ClashExeption as e:  
            return e.handle(self.debug) 
        except StabilityViolationFinalException as e:
            return e.handle(self.debug,start_time)

        if self.debug >1: self.print_final_results()  
        if self.debug in [0,1]: print(f"\t unifiable --- {round(time.time() - start_time,3)} seconds ---")

        #self.unifier()
        return True , (time.time() - start_time)

    def unify_current(self):

## incrementing the current subproblem for the computation of the next subproblem
        current = self.current().subproblem.increment(self.SchematicSubstitution)
        if self.debug>2: self.print_current_problem(self.current())
        if self.debug>4: print("Theta Unification:\n")
        store, context = self.SchSolver.unify(current)
        if self.debug>3: print("First-order Syntactic Unification:\n")
## Checking for cycles in the new subproblem
        self.foSolver.count = self.count
        self.foSolver.unify(context)
## Dropped everything which has to do with Store from the context
        cleaned_context= set(filter(lambda a:  not a in store and not type(a[0]) is Rec , context)) 
        contextVars = [x[0] for x in cleaned_context]
## Checking for cycles in the Irrelevant set
        results = self.cycle(contextVars,cleaned_context)
## Build substitution without mappings to Rec
## Note, a bit of randomness below. May output different equivalent results
        cleanresults = results.restriction(lambda a:not a.vc in self.SchematicSubstitution.symbols )
## Build substitution with only mappings to Rec
        FromDom = results.restriction(lambda a: a.vc in self.SchematicSubstitution.symbols )
## Build substitution by composing the previous two and removing mappings to Rec
        results = FromDom(cleanresults).restriction(lambda a:not a.vc in self.SchematicSubstitution.symbols )
## We may have derived Store bindings in the process.
        finRes = results.restriction(lambda a: a in contextVars)
        self.current().IrrSub = finRes
        return  store

    def current(self):
        return self.subproblems.Top()

    def update(self):
        self.foSolver.clear()
        self.count+=1

    def update_subproblems(self,sub):
        if self.debug>3: self.print_sub_results(sub)
        self.subproblems += SubProblem(sub)
    
    def cycle(self,contextVars,cleaned_context):
        contextIdxs = [x.idx for x in contextVars]
        maxContextVar =  max(contextIdxs) if contextIdxs != [] else 0
        ## Turning off debugging for checks
        self.foSolver.debug = -1
        ## Add the cleaned context to the irrelevant set
        ## Check if the irrelevant set contains a cycle 
        for uEq in cleaned_context: self.irrelevant +=uEq
        contextRecs = set()
        for x in self.irrelevant: contextRecs.update(x[1].vos(Rec))
        contextRecsIdxs = [x.idx for x in contextRecs]
        minContextRex = min(contextRecsIdxs) if contextRecsIdxs!= [] else 0
        shifts = max(maxContextVar-minContextRex+1,0)
        ## incrementing the irrelevant set for the computation of its extension
        for i in range(0,shifts):
            self.irrelevant = self.irrelevant.increment(self.SchematicSubstitution)
        ## Run MM again to get a unifier
        self.foSolver.unify(self.irrelevant)
        ## We be used to build the irrelevant unifier
        results , _=self.foSolver.unify(cleaned_context)
        ## Turning debugging back on 
        self.foSolver.debug = self.debug
        return results
    #def unifier(self):
        #This is the code for building the first part of a unifier 
               
#         sigma=Substitution()
#         tau = Substitution()
#         sigmaEQ = Substitution()

#         Xi = SchematicSubstitution()
#         recNames = Namer("NR")
# #We create an instance of the initial problem
#         initProb = self.subproblems.subproblems[0].subproblem.instance()
# # We build a substitution into the recs starting from the initial 
# #problem until the problem which starts the cycle. 
#         for i in range(0,self.subproblems.cycle):
# # We will remove bindings associated with recsSet later
#             recsSet= initProb.recs()
# # We build the Schematic substitution instance based on recsSet,
# # update sigma and apply to initProb
#             self.SchematicSubstitution.clear()
#             self.SchematicSubstitution.ground(localRecs=recsSet)
#             sigma = self.SchematicSubstitution(sigma)
#             initProb= self.SchematicSubstitution(initProb)
# # Remove old bindings from the composition
#             if i!=0:
#                 for x in recsSet: sigma.removebinding(x)
# # We compose sigma  with the irrelevant substitutions
#         for i,x in enumerate(self.subproblems):
#             if i< self.subproblems.cycle:sigma=sigma(x.IrrSub)
#             tau = tau(x.IrrSub)
#             sigmaEQ = sigmaEQ(x.eqSubstitution)
# # We get the relevant recursions we can build Xi
#         partUnifProb = sigma(self.subproblems.subproblems[0].subproblem.instance())
#         pupRecs = partUnifProb.recs()
# # We build a substitution and compose it with sigma
#         newRecs = Substitution()
#         newRecsDict = {}
#         for x in pupRecs:
#             newRecs += (x,Rec(Func(recNames.current_name(),1),0))
#             newRecsDict[x] =Func(recNames.current_name(),1)
#             recNames.next_name()
# # At this point we are not done with sigma
# # as there may be new recs introduced for variables in the initial problem
#         sigma=sigma(newRecs)
#         sigma=sigma(sigmaEQ)
#         print(sigma)
# # I am assuming primitive here
#         newRecsterms ={}
#         steps = (len(self.subproblems)-self.subproblems.cycle)+1
#         print(steps)
#         for x in pupRecs:
#             t = x.instance()
#             for i in range(0,steps):
#                 self.SchematicSubstitution.clear()
#                 self.SchematicSubstitution.ground(localRecs=t.recs())
#                 t = self.SchematicSubstitution(t)
#             t = sigmaEQ(t)
#             for r in t.recs():
#                 temp = Substitution()
#                 temp += (r,Rec(newRecsDict[x],steps))
#                 t = temp(t)
#             newRecsterms[x]=t
#         print(newRecsterms[x])

    def print_unif_results(self,unif):
        print("Unifier of "+str(self.count)+":\n"+ ''.join(["\t"+str(x)+" <= "+str(y)+"\n" for x,y in unif])+"\n")

    def print_final_results(self):
        result =self.subproblems.print_closures()
        print()
        for i,x in enumerate(self.subproblems):
            print("Irrelevant Substitution for subproblem "+str(i)+":")
            print(x.IrrSub)
   
    def print_sub_results(self,subp):
            print("subproblem:\n", ''.join([ "\t"+"{"+str(x)+"}"+" =?= "+"{{"+str(y)+"}}\n" for x,y in subp]))
            print("----------------------------------------------------------")
            print("----------------------------------------------------------")
    
    def print_initial_problem(self):
        print("Schematic Unification Problem:\n" )
        for x,y in self.subproblems.subproblems[0]:
            print(f"\t{x} =?= {y}\n")
        print()
        print("Schematic Substitution:\n")
        self.SchematicSubstitution.clear()
        self.SchematicSubstitution.ground()
        for x in self.SchematicSubstitution.mapping.keys():
            print("\t"+ x.vc+"_i"+" <== "+self.SchematicSubstitution.mapping[x].strAlt("i"))
        print()
        print("==========================================================")

    def print_current_problem(self,current):
        print("Problem "+str(self.count)+":")
        print(current)
        print("==========================================================")
        print()
