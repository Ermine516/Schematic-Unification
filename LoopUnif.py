from Solver import Solver
from SubProblemTree import *
from Unifier import *
from Term import *
from Interpretation import *
from Namer import *
import functools
from ThetaUnif import ThetaUnif as tu
from MAndM import MAndM as mm

class LoopUnif:

    def __init__(self,SchematicSubstitution,debug=0,toUnif=[],unifierCompute=False):
        self.debug = debug
        self.shift = lambda l,r: (l,I.increment(r.func.name,r.idx) if type(r) is Rec else r)
        self.foSolver = mm(SchematicSubstitution,debug)
        self.SchSolver = tu(SchematicSubstitution,debug)
        self.unifier = Unifier()
        self.count = 0
        self.SchematicSubstitution = SchematicSubstitution
        self.unifierCompute=unifierCompute
        #starter_var = self.solver.freshvar(False)
        if toUnif ==[] :
            toUnif = [ x(Idx(0))  for x in I.symbols]
        self.subproblems = SubProblemTree(toUnif)


    def loop_unif(self):
        config = Configuration(self.UnifProb,set(),self.I.symbols)  
        count=0
        while count<20:
            config = unify(config,self.I,self.debug)
            if not config:
                print("not Unifiable")
                return
            else:
                print("RESULT:")
                print(config)    
            recursions = [(x.idx,self.I.increment(x.func.name,x.idx),y) for x,y in filter(lambda a: type(a[0]) is Rec, config.store)]
            if len(recursions)>0:
                vars = list(filter(lambda a:  type(a[0]) is Var, config.store))
                toremove = recursions[0] if len(recursions) >0 else None
                while toremove:
                    toremove = None
                    for x,y in vars:
                        for i,x1,y1 in recursions:
                            if  x.occurs(y1) or x.idx >i.number: #technically wrong
                                recursions.append((i,x,y))
                                toremove = (x,y)
                                break  
                        if toremove:
                            break
                    if toremove:
                        vars.remove((x,y)) 
                self.irrelevantProb.extend(vars)
                config = Configuration([(x,y) for i,x,y in recursions],set(),self.I.symbols)  
                # print("Next Problem:")
                # print(config)
                count+=1
            else:
                config.active =[]
                # print(config)
                return


    def loop_unif(self):
        while self.subproblems.getOpenBranch():
            try:
                solved, subp= self.unify_current()
            except Solver.CycleException as e:
                 return e.handle(self.debug)
            except Solver.ClashExeption as e:  return e.handle(self.debug)
            self.update_unifier(solved)
            self.update_subproblems(subp)
            self.update()
        if self.debug >1: self.print_final_results()
        if self.debug in [0,1] and not self.unifierCompute: print("\t unifiable")
## What is below only works if there is a single interpreted Variable
## We will assume the left side always contains the interpreted variables
## and that the original problem only has a single unification Problem
        if self.unifierCompute:
            self.computeTheUnifier()

    def computeTheUnifier(self):
        shiftc = lambda l,r: (l,self.I.increment(r.func.name,r.idx,clean=True) if type(r) is Rec else r)
        shiftu = lambda l: shiftc(None,l)[1]
        recvar = list(self.I.mappings.keys())[0]
        thebranch=self.subproblems.closedbranches[0]
        leafIdx=thebranch.cyclicIdx
        sproutIdx=thebranch.idx
        change = len(range(leafIdx,sproutIdx))
        recterm = Rec(Func(recvar,1),Idx(leafIdx))
## computing the new definition of the interpreted variable
        newmapping= recterm
        for i in range(leafIdx,sproutIdx):
            newmapping= newmapping.inducAppRebuild(shiftu)
## need to shift the interpreted variable occurance down
        recshift = lambda x,y: Rec(x.func,(Idx(y))) if isinstance(x,Rec) else x
        newmapping= newmapping.inducAppRebuild(lambda x:recshift(x,change))
## need to get the original unification problem associated with the branch
        while thebranch.parent !=None:
            thebranch = thebranch.parent

## need to shift the left side of the original problem to the idx of the sprout
        newleft= thebranch.subproblem[0][1]
        for i in range(0,leafIdx):
            newleft= newleft.inducAppRebuild(shiftu)
## need to shift the interpreted variable occurance down
        newleft= newleft.inducAppRebuild(lambda x:recshift(x,0))


## new unification problem with sprout at 1 and leaf at 2
        newunifproblem = [newleft,thebranch.subproblem[1][1]]
        I2 = Interpretation()
        I2.add_relevent_vars(newunifproblem,clean=True)
        recursionVar=Func(recvar,1)
        I2.add_mapping(recursionVar,newmapping,clean=True)
        lu = LoopUnif(I2,-1,newunifproblem,unifierCompute=False)
        lu.loop_unif()
## we use the new solution to build the unifier
        unif_bindings = []
        names = Namer("I")
# We need to build the mappings for variables in the sprout-leaf pairs
        VarMappings= set()
        for cycle in  lu.subproblems.closedbranches:
            for x,y in cycle.cyclic:
                VarMappings.update(LoopUnif.matchedTerms(y[1],x[1]))
        VarMappings = dict(VarMappings)
        for x,y in [ x for x in lu.unifier.local_bindings(1) if str(x[0])[0]!= "*"]:
            if str(y)[0]== "*":
                subproblemclass = Func(names.current_name(),1)
                names.next_name()
                unif_bindings.append((x,subproblemclass(Idx(0))))
                I2.add_mapping(subproblemclass,recursionVar(Idx(change)))
                if x in VarMappings.keys():
                    unif_bindings.append((Var.find(VarMappings[x]),subproblemclass(Idx(change))))

            elif isinstance(x,Var) and isinstance(y,Var):
                unif_bindings.append((x,y))
            else:
                if x in VarMappings.keys():
                    subproblemclass = Func(names.current_name(),1)
                    names.next_name()
                    I2.add_mapping(subproblemclass,y)
                    unif_bindings.append((x,subproblemclass(Idx(0))))
                    unif_bindings.append((Var.find(VarMappings[x]),subproblemclass(Idx(2))))
                elif x in VarMappings.values():
                    continue
                else:
                    unif_bindings.append((x,y))
        for x,y in [ x for x in lu.unifier.local_bindings(0) if str(x[0])[0]!= "*"]:
            if str(y)[0]== "*":
                unif_bindings.append((x,recursionVar(Idx(0))))
                if x in VarMappings.keys():
                    unif_bindings.append((VarMappings[x],recursionVar(Idx(change))))
            elif isinstance(x,Var) and isinstance(y,Var):
                unif_bindings.append((x,y))
            else:
                if x in VarMappings.keys():
                    subproblemclass = Func(names.current_name(),1)
                    names.next_name()
                    I2.add_mapping(subproblemclass,y)
                    unif_bindings.append((x,subproblemclass(Idx(0))))
                    unif_bindings.append((VarMappings[x],subproblemclass(Idx(2))))
                elif x in VarMappings.values():
                    continue
                else:
                    unif_bindings.append((x,y))

    #    if self.debug >=1:
        lu.print_unifier_details(newunifproblem,unif_bindings)

    # def check(self,t):
    #     if isinstance(t,App):
    #         for x in t.args: self.check(x)
    #     elif isinstance(t,Var):
    #         print(repr(t),str(t))

    def matchedTerms(x,y):
        if isinstance(x,App):
            return reduce(lambda a,b: a.union(b),map(lambda a: LoopUnif.matchedTerms(*a),zip(x.args,y.args)),set())
        elif isinstance(x,Var):
            return set([(x,y)])
        else:
            return set()
    def current(self):
        return self.subproblems.current()

    def update(self):
        self.foSolver.clear()
        self.count+=1

    def update_unifier(self,sol):
        if self.debug==3: self.print_unif_results(sol)
        self.unifier.extend(self.current().idx,sol)

    def update_subproblems(self,sub):
        #subp = list(map(lambda a: self.add_relevent(a),sub))
        
        if self.debug==3: self.print_sub_results(sub)
        self.subproblems.addBranch(sub)
    
    def updateRec(self,b):
        RecReplace = lambda x: self.SchematicSubstitution.increment(x.func.name,x.idx) if type(x) is Rec else x
        return (b[0].inducAppRebuild(RecReplace),b[1].inducAppRebuild(RecReplace))
    
    def updateRec2(self,b):
        RecReplace = lambda x: Var(x.func.name,x.idx.number) if type(x) is Rec else x
        return (b[0].inducAppRebuild(RecReplace),b[1].inducAppRebuild(RecReplace))
    
    def unify_current(self):
        current = list(map(self.updateRec,self.current().subproblem))
        if self.debug==3 or (self.count==0 and self.debug>0): self.print_current_problem(current)
        store, context = self.SchSolver.unify(current)
        self.foSolver.count = self.count
        results , subprobs =self.foSolver.unify(list(map(self.updateRec2,context)))
        print(context)
        return  set(filter(lambda a: not a in store, context)), store
       # probterms = reduce(lambda a,b: a+[self.shift(*b)],self.current().subproblem,[])
       # return self.solver.unify(self.count,self.debug,self.I)

    def add_relevent(self, subp):
        relu,seen = set(),set()
        def check_for_rel(t):
            if type(t) is Var:
                b=self.unifier.binding(t.vc,t.idx)
                if b and not type(b[1]) is Var: relu.add(b)
                if b and type(b[1]) is Var and not b[1] in seen:
                    seen.add(b[1])
                    check_for_rel(b[1])
            elif type(t) is App:
                for x in t.args: check_for_rel(x)
            elif type(t) is Rec:
                for vx,gx in self.I.associated_classes[t.func.name].items():
                    for b in self.unifier.bindings(subdom=[vx],bound=t.idx.number+gx):
                        relu.add(b)
                        check_for_rel(b[1])
        for t in subp.terms:
            check_for_rel(t)
            relu.add((subp,t))
        subp.clean(False)
        return relu

    def print_unif_results(self,unif):
        print("Unifier of "+str(self.count)+":\n"+ ''.join(["\t"+repr(x)+" <= "+str(y)+"\n" for x,y in unif])+"\n")

    def print_final_results(self):
        self.subproblems.print_closures()
        print()
        for cb in self.subproblems.closedbranches:
            # l,r = self.unifier.binding("*",cb.cyclicIdx)
            # expanded = r.apply_unif_vc(l,Var("*",cb.idx),self.unifier.global_unifier)
            # expanded = expanded.apply_unif(self.unifier.global_unifier)
            # print(str(l)+" <== "+str(expanded))
            cur = cb.parent
            while cur:
                print("Computed Bindings for subproblem "+str(cur.idx)+":\n"+ ''.join(["\t"+repr(x)+" <= "+str(y)+"\n" for x,y in self.unifier.local_bindings(cur.idx)])+"\n")
                cur = cur.parent
    def print_sub_results(self,subp):
        for i in range(0,len(subp)):
            print("subproblem "+str(i)+" of "+str(self.count)+":\n", ''.join([ "\t"+"{"+repr(x)+"}"+" =?= "+"{{"+str(y)+"}}\n" for x,y in subp]))
        print("----------------------------------------------------------")
        print("----------------------------------------------------------")
    def print_current_problem(self,current):
        if self.count == 0:
            print("Loop Unification Problem:\n" )
            for x,y in current:
                print(f"\t{x} =?= {y}\n")
            print()
            print("Interpreted Class definitions:\n")
            for x in self.SchematicSubstitution.mappings.keys():
                print("\t"+ x+"_i"+" <== "+self.SchematicSubstitution.mappings[x].strAlt("i"))
            print()

        else:
            print("Problem "+str(self.count)+":\n\t"+ '\n\t'.join([str(v)+" =?= "+str(t) for v,t in current])+"\n")
        print("==========================================================")
    def print_unifier_details(self,unif_terms,unif_bindings):
        print("==========================================================")
        print("Unifier Terms:\n")
        for x in unif_terms:
            print("\t"+ repr(x))
        print()
        print("Unifier Interpreted Class definitions:\n")
        for x in self.I.mappings.keys():
            print("\t"+ x+" <== "+repr(self.I.mappings[x]))
        print()
        print("Unifier Bindings (triangular form):\n")
        for x,y in unif_bindings:
            print("\t"+ repr(x)+" <== "+ str(y))
