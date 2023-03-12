from Solver import *

class LoopUnif:
    def __init__(self,I,debug=False):
        self.debug = debug
        self.shift = lambda l,r: (l,I.increment(r.func.name,r.idx) if type(r) is Rec else r)
        self.solver = Solver()
        self.unifier = {}
        self.count = 0
        self.I = I
        starter_var = self.solver.freshvar(False)
        start = Idx(0)
        self.subproblems = [[(starter_var,x(start)) for x in I.symbols]]

    def loop_unif(self):
        while not self.check_finished():
            try:
                solved, subp= self.unify_current()
            except Solver.CycleException as e: return e.handle()
            except Solver.ClashExeption as e:  return e.handle()
            self.update_unifier(solved)
            self.update_subproblems(subp)
            self.update()
        self.print_final_results()

    def current(self):
        return self.subproblems[self.count]

    def update(self):
        self.solver.clear()
        self.count+=1

    def update_unifier(self,sol):
        if self.debug: self.print_unif_results(sol)
        for x,y in sol.items():
            if not x.vclass in self.unifier.keys(): self.unifier[x.vclass] = {}
            self.unifier[x.vclass][x.idx]=(x,y)
            x.clean(False)

    def update_subproblems(self,sub):
        subp = list(map(lambda a: self.add_relevent(a),sub))
        if self.debug: self.print_sub_results(subp)
        self.subproblems.extend(subp if len(subp)!= 0 else [[]])

    def unify_current(self):
        probterms = reduce(lambda a,b: a+[self.shift(*b)],self.current(),[])

        if self.debug or self.count==0: self.print_current_problem(probterms)
        for v,t in probterms: self.solver.add_eq(v,t)
        return self.solver.unify(self.count,self.debug)

    def add_relevent(self, subp):
        relu = set()
        seen = set()
        def check_for_rel(t):
            if type(t) is Var:
                if t.vclass in self.unifier.keys() and t.idx in self.unifier[t.vclass].keys():
                    relu.add(self.unifier[t.vclass][t.idx])
                    if type(self.unifier[t.vclass][t.idx][1]) is Var and not self.unifier[t.vclass][t.idx][1] in seen:
                        seen.add(self.unifier[t.vclass][t.idx][1])
                        check_for_rel(self.unifier[t.vclass][t.idx][1])
            elif type(t) is App:
                for x in t.args: check_for_rel(x)
            elif type(t) is Rec:
                cur_idx = t.idx.number
                for vx,gx in self.I.associated_classes[t.func.name].items():
                    if vx in self.unifier.keys():
                        for j in self.unifier[vx].keys():
                            if j>= cur_idx+gx:
                                relu.add(self.unifier[vx][j])
                                check_for_rel(self.unifier[vx][j][1])
        for t in subp.terms:
            check_for_rel(t)
            relu.add((subp,t))
        subp.clean(False)
        return relu

    def check_finished(self):
        if self.subproblems[self.count] == []:
            return True
        else:
            test = list(filter(lambda a: not type(a[1]) is Rec , self.subproblems[self.count]))
            for i in range(0,self.count):
                check = list(filter(lambda a: not type(a[1]) is Rec, self.subproblems[i]))
                if len(test) == len(check):
                    result =[]
                    for vt,t in test:
                        found = None
                        for vs,s in check:
                            if t.isalpha(s):
                                found = (vs,s)
                                break
                        if found:
                            result.append(((vt,t),found))
                            check.remove(found)
                    if check ==[]:
                        print("Recursion Found "+str(self.count)+" => "+str(i)+" :\n\t"+'\n\t'.join([str(x)+" => "+str(y) for x,y in result]))
                        return True
            return False


    def print_unif_results(self,unif):
        print("Unifier of "+str(self.count)+":\n"+ ''.join(["\t"+str(x)+" <= "+str(y)+"\n" for x,y in unif.items()])+"\n")

    def print_final_results(self):
        print()
        print("Computed Bindings:\n"+ ''.join(["\t"+str(y[0])+" <= "+str(y[1])+"\n" for c in self.unifier.keys() for x,y in self.unifier[c].items()])+"\n")

    def print_sub_results(self,subp):
        for i in range(0,len(subp)):
            print("subproblem "+str(i)+" of "+str(self.count)+":\n", ''.join([ "\t"+"{"+str(x)+"}"+" =?= "+"{{"+str(y)+"}}\n" for x,y in subp[i]]))
        print("----------------------------------------------------------")
        print("----------------------------------------------------------")
    def print_current_problem(self,probterms):
        if self.count == 0:
            print("Loop Unification Problem:\n\t"+ str(probterms[0][1])+" =?= "+str(probterms[1][1])+"\n")
        else:
            print("Problem "+str(self.count)+":\n\t"+ '\n\t'.join([str(v)+" =?= "+str(t) for v,t in probterms])+"\n")
        print("==========================================================")
