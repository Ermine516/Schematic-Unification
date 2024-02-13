from Solver import Solver
from SubProblemStack import *
from Unifier import *
from Term import *
from SchematicSubstitution import *
from Namer import *
import functools
from ThetaUnification import ThetaUnification
from MM import MM 
import time

class SchematicUnification:

    def __init__(self,UnifProb,debug=0):
        self.debug = debug
        self.foSolver = MM(UnifProb.schSubs,debug)
        self.SchSolver = ThetaUnification(UnifProb.schSubs,debug)
        self.unifier = Unifier()
        self.count = 0
        self.SchematicSubstitution = UnifProb.schSubs
        self.subproblems = SubProblemStack(UnifProb,debug)


    def unif(self,start_time=-1):
        self.foSolver.setTime(start_time)
        self.SchSolver.setTime(start_time)
        try:
            while self.subproblems.Open(start_time):
                try:
                    solved, subp, recs= self.unify_current()
                except Solver.CycleException as e:
                    return e.handle(self.debug)
                except Solver.ClashExeption as e:  
                    return e.handle(self.debug)
                self.update_unifier(solved)
                self.update_subproblems(subp,recs)
                self.update()
        except StabilityViolationFinalException as e:
            return e.handle(self.debug,start_time)

        if self.debug >1: self.print_final_results()  
        if self.debug in [0,1]: print(f"\t unifiable --- {round(time.time() - start_time,3)} seconds ---")
        return True , (time.time() - start_time)

    def unify_current(self):
        def updateRec2(b):
            RecReplace = lambda x: Var(x.func.name,x.idx) if type(x) is Rec else x
            return (b[0].inducAppRebuild(RecReplace),b[1].inducAppRebuild(RecReplace))
        current = self.current().subproblem.increment(self.SchematicSubstitution)
        if self.debug>2 or (self.count==0 and self.debug>0): 
            self.print_current_problem(self.current().subproblem)
            print()
        if self.debug>4: print("Theta Unification:\n")
        store, context,recs = self.SchSolver.unify(current)
        forUnifier = set(filter(lambda a: not a in store and not type(a[0]) is Rec, context))

        
        if self.debug>3: print("First-order Syntactic Unification:\n")
        self.foSolver.count = self.count
        results , subprobs, unused =self.foSolver.unify(set(map(updateRec2,context)))
        return  forUnifier, store,recs

    def current(self):
        return self.subproblems.Top()

    def update(self):
        self.foSolver.clear()
        self.count+=1

    def update_unifier(self,sol):
        if self.debug>3: self.print_unif_results(sol)
        self.unifier.extend(len(self.subproblems),sol) 
    def update_subproblems(self,sub,recs):
        if self.debug>3: self.print_sub_results(sub)
        self.subproblems += SubProblem(sub)
    
    def print_unif_results(self,unif):
        print("Unifier of "+str(self.count)+":\n"+ ''.join(["\t"+str(x)+" <= "+str(y)+"\n" for x,y in unif])+"\n")

    def print_final_results(self):
        result =self.subproblems.print_closures()
        print()
        for x in range(0,len(self.subproblems)):
            print("Computed Bindings for subproblem "+str(x)+":\n"+ ''.join(["\t"+str(y)+" <= "+str(z)+"\n" for y,z in self.unifier.local_bindings(x)])+"\n")
   
    def print_sub_results(self,subp):
            print("subproblem:\n", ''.join([ "\t"+"{"+str(x)+"}"+" =?= "+"{{"+str(y)+"}}\n" for x,y in subp]))
            print("----------------------------------------------------------")
            print("----------------------------------------------------------")
    
    
    def print_current_problem(self,current):
        if self.count == 0:
            print("Schematic Unification Problem:\n" )
            for x,y in current:
                print(f"\t{x} =?= {y}\n")
            print()
            print("Schematic Substitution:\n")
            self.SchematicSubstitution.clear()
            self.SchematicSubstitution.ground()
            for x in self.SchematicSubstitution.mapping.keys():
                print("\t"+ x.name+"_i"+" <== "+self.SchematicSubstitution.mapping[x].strAlt("i"))
            print()

        else:
            print("Problem "+str(self.count)+":\n\t"+ '\n\t'.join([str(v)+" =?= "+str(t) for v,t in current])+"\n")
        print("==========================================================")
    def print_unifier_details(self,unif_terms,unif_bindings):
        print("==========================================================")
        print("Unifier Terms:\n")
        for x in unif_terms:
            print("\t"+ str(x))
        print()
        print("Unifier Interpreted Class definitions:\n")
        for x in self.SchematicSubstitution.mappings.keys():
            print("\t"+ x+" <== "+str(self.SchematicSubstitution.mappings[x]))
        print()
        print("Unifier Bindings (triangular form):\n")
        for x,y in unif_bindings:
            print("\t"+ str(x)+" <== "+ str(y))


    