from Solver import *
from SubProblemTree import *
class LoopUnif:
    def __init__(self,I,debug=0,toUnif=[]):
        self.debug = debug
        self.shift = lambda l,r: (l,I.increment(r.func.name,r.idx) if type(r) is Rec else r)
        self.solver = Solver(I)
        self.unifier = {}
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
        for x,y in sol.items():
            if not x.vc in self.unifier.keys(): self.unifier[x.vc] = {}
# TODO if we are going to handle nested terms we to unif here not just erase
# Also the case if we are going to handle non-linear variable class usage

# TODO another problem, a variable for which we know it's unifier may be updated.
# To deal with this we need to check for such updates. Probably another source
# of non-deterministic behavior, especially in the non-shallow case.
            self.unifier[x.vc][x.idx]=(x,y)
            x.clean(False)

    def update_subproblems(self,sub):
        subp = list(map(lambda a: self.add_relevent(a),sub))
        if self.debug==3: self.print_sub_results(subp)
        for s in subp:
            if len(subp)!=0: self.subproblems.addBranch(s)

    def unify_current(self):
        probterms = reduce(lambda a,b: a+[self.shift(*b)],self.current().subproblem,[])

        if self.debug==3 or (self.count==0 and self.debug>0): self.print_current_problem(probterms)
        for v,t in probterms: self.solver.add_eq(v,t)
        return self.solver.unify(self.count,self.debug,self.I)

    def add_relevent(self, subp):
        relu = set()
        seen = set()
        def check_for_rel(t):
            if type(t) is Var:
                if t.vc in self.unifier.keys() and t.idx in self.unifier[t.vc].keys():
                    if not type(self.unifier[t.vc][t.idx][1]) is Var: relu.add(self.unifier[t.vc][t.idx])
                    if type(self.unifier[t.vc][t.idx][1]) is Var and not self.unifier[t.vc][t.idx][1] in seen:
                        seen.add(self.unifier[t.vc][t.idx][1])
                        check_for_rel(self.unifier[t.vc][t.idx][1])
            elif type(t) is App:
                for x in t.args: check_for_rel(x)
            elif type(t) is Rec:
                cur_idx = t.idx.number
                for vx,gx in self.I.associated_classes[t.func.name].items():
                    if vx in self.unifier.keys():
                        for j in self.unifier[vx].keys():
                            if j>= cur_idx+gx:
                                relu.add(self.unifier[vx][j]) #if not type(self.unifier[vx][j][1]) is Var:
                                check_for_rel(self.unifier[vx][j][1])
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
        print("Computed Bindings:\n"+ ''.join(["\t"+repr(y[0])+" <= "+str(y[1])+"\n" for c in self.unifier.keys() for x,y in self.unifier[c].items()])+"\n")

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
