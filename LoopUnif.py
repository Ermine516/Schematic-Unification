from Solver import *
from SubProblemTree import *
from Unifier import *
class LoopUnif:
    def __init__(self,I,debug=0,toUnif=[]):
        self.debug = debug
        self.shift = lambda l,r: (l,I.increment(r.func.name,r.idx) if type(r) is Rec else r)
        self.solver = Solver(I)
        self.unifier = Unifier()
        self.count = 0
        self.I = I
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
        print("\t unifiable")
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
