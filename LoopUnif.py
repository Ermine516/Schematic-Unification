from Solver import *
from SubProblemTree import *
from Unifier import *
from Term import *
from Interpretation import *
from Namer import *
class LoopUnif:
    def __init__(self,I,debug=0,toUnif=[],unifierCompute=False):
        self.debug = debug
        self.shift = lambda l,r: (l,I.increment(r.func.name,r.idx) if type(r) is Rec else r)
        self.solver = Solver(I)
        self.unifier = Unifier()
        self.count = 0
        self.I = I
        self.unifierCompute=unifierCompute
        starter_var = self.solver.freshvar(False)
        if toUnif ==[] :
            toUnif = [ x(Idx(0))  for x in I.symbols]

        self.subproblems = SubProblemTree([(starter_var,x) for x in toUnif ])

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
        if self.debug != -1: print("\t unifiable")
## What is below only works if there is a single interpreted Variable
        if self.unifierCompute:
            self.computeTheUnifier()

    def computeTheUnifier(self):
            shiftu = lambda l: self.shift(None,l)[1]
            recvar = list(self.I.mappings.keys())[0]
            thebranch=self.subproblems.closedbranches[0]
            loopingIdx=thebranch.cyclicIdx
            recterm = Rec(Func(recvar,1),Idx(loopingIdx))
            newmapping= recterm
            for i in range(loopingIdx,thebranch.idx):
                newmapping= newmapping.inducAppRebuild(shiftu)
            change = len(range(loopingIdx,thebranch.idx))
            recshift = lambda x,y: Rec(x.func,(Idx(y))) if isinstance(x,Rec) else x

            newmapping= newmapping.inducAppRebuild(lambda x:recshift(x,change))
            while thebranch.parent !=None:
                thebranch = thebranch.parent
## We will assume the left side always contains the interpreted variables
## and that the original problem only has a single unification Problem
            newleft= thebranch.subproblem[0][1]
            for i in range(0,loopingIdx):
                newleft= newleft.inducAppRebuild(shiftu)
            newleft= newleft.inducAppRebuild(lambda x:recshift(x,0))
            newunifproblem = [newleft,thebranch.subproblem[1][1]]
            I2 = Interpretation()
            I2.add_relevent_vars(newunifproblem)
            recursionVar=Func(recvar,1)
            I2.add_mapping(recursionVar,newmapping)
            lu = LoopUnif(I2,-1,newunifproblem,unifierCompute=False)
            lu.loop_unif()
            unif_bindings = []
            names = Namer("I")
            for x,y in [ x for x in lu.unifier.local_bindings(0) if str(x[0])[0]!= "*"]:
                if str(y)[0]== "*": unif_bindings.append((x,recursionVar(Idx(0))))
                else: unif_bindings.append((x,y))
            for x,y in [ x for x in lu.unifier.local_bindings(1) if str(x[0])[0]!= "*"]:
                if str(y)[0]== "*":
                    subproblemclass = Func(names.current_name(),1)
                    unif_bindings.append((x,subproblemclass(Idx(0))))
                    I2.add_mapping(subproblemclass,recursionVar(Idx(change)))
                else: unif_bindings.append((x,y))
            if self.debug >=1: lu.print_unifier_details(newunifproblem,unif_bindings)
            for cycle in  lu.subproblems.closedbranches:
                print('\n\t'.join([str(x)+" => "+str(y) for x,y in cycle.cyclic]))
                
    def current(self):
        return self.subproblems.current()

    def update(self):
        self.solver.clear()
        self.count+=1

    def update_unifier(self,sol):
        if self.debug==3: self.print_unif_results(sol)
        self.unifier.extend(self.current().idx,sol.items())

    def update_subproblems(self,sub):
        subp = list(map(lambda a: self.add_relevent(a),sub))
        if self.debug==3: self.print_sub_results(subp)
        for s in subp: self.subproblems.addBranch(s)

    def unify_current(self):
        probterms = reduce(lambda a,b: a+[self.shift(*b)],self.current().subproblem,[])
        if self.debug==3 or (self.count==0 and self.debug>0): self.print_current_problem(probterms)
        for v,t in probterms: self.solver.add_eq(v,t)
        return self.solver.unify(self.count,self.debug,self.I)

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
        print("Unifier of "+str(self.count)+":\n"+ ''.join(["\t"+repr(x)+" <= "+str(y)+"\n" for x,y in unif.items()])+"\n")

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
            print("subproblem "+str(i)+" of "+str(self.count)+":\n", ''.join([ "\t"+"{"+repr(x)+"}"+" =?= "+"{{"+str(y)+"}}\n" for x,y in subp[i]]))
        print("----------------------------------------------------------")
        print("----------------------------------------------------------")
    def print_current_problem(self,probterms):
        if self.count == 0:
            print("Loop Unification Problem:\n\t"+ str(probterms[0][1])+" =?= "+str(probterms[1][1])+"\n")
            print()
            print("Interpreted Class definitions:\n")
            for x in self.I.mappings.keys():
                print("\t"+ x+"_0"+" <== "+str(self.I.mappings[x]))
            print()

        else:
            print("Problem "+str(self.count)+":\n\t"+ '\n\t'.join([str(v)+" =?= "+str(t) for v,t in probterms])+"\n")
        print("==========================================================")
    def print_unifier_details(self,unif_terms,unif_bindings):
        print("==========================================================")
        print("Unifier Terms:\n")
        for x in unif_terms:
            print("\t"+ str(x))
        print()
        print("Unifier Interpreted Class definitions:\n")
        for x in self.I.mappings.keys():
            print("\t"+ x+"_0"+" <== "+str(self.I.mappings[x]))
        print()
        print("Unifier Bindings:\n")
        for x,y in unif_bindings:
            print("\t"+ str(x)+" <== "+ str(y))
