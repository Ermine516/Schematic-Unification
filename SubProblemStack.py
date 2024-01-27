from Term import *
import clingo
import clingo.script
class SubProblem:
    def __len__(self):
        return len(self.subproblem)
   
    def __init__(self,subproblem,recs):
        def getvars(t):
            if type(t) is App:
                ret=set()
                for x in t.args: 
                    ret.update(getvars(x))
                return ret
            elif type(t) is Var:
                return set([t]) 
            else:
                return set()       
        self.subproblem = subproblem
        self.vars =set()
        self.futurevars ={}
        self.recs = recs
        self.futureRel = set()
        self.cyclic = False
        for x,y in subproblem:
            self.vars.update(getvars(x))
            self.vars.update(getvars(y))
        for x in self.vars:
            if not x.vc in self.futurevars.keys():
                self.futurevars[x.vc] =  x 
            if x.idx >self.futurevars[x.vc].idx: 
                self.futurevars[x.vc] =  x 

        





class SubProblemStack:
    clingoBasic = ["#show e/2.","#defined futureRel/1.","#defined match/2.",\
    ":- e(X,Y),futureRel(X),not futureRel(Y). " ,":- e(X,Y),not futureRel(X), futureRel(Y). ",\
    ":- e(X,Y1), e(X,Y2), Y1!=Y2." ,":- other(X), not match(X,_)." ,\
     ":- tops(X), not match(_,X), not reflexive(X).",\
     "reflexive(X):- X=(Y,W), varl(Y),varl(W), tops(X), e(Y,X),e(W,X)." , \
     "1{ e(X,Y): varr(Y)}1:- varl(X).",":-  varr(Y), not e(_,Y).",\
     ":- varl(X),recs(X),#count{Y: recs(Y),X!=Y,e(X,Y)}=0."]
    def __init__(self,prob,dom,debug=0):
        self.cycle = -1
        self.mapping =None
        self.debug = debug
        self.dom = dom 
        def getrecs(t):
            if type(t) is App:
                ret=set()
                for x in t.args: 
                    ret.update(getrecs(x))
                return ret
            elif type(t) is Rec:
                return set([t]) 
            else:
                return set()  
        recs=set()
        for x,y in prob:
            recs.update(getrecs(x))
            recs.update(getrecs(y))
        self.subproblems = [SubProblem(prob,recs)]
    
    def __len__(self):
        return len(self.subproblems)-1
    
    def __add__(self,val):
        if type(val) is SubProblem:
            self.subproblems.append(val) 
        else:
            raise TypeError(f"Type of val is {type(val)} and should be SubProblem")
        return self
    def futureOverlap(self,current,other):
        for r in current.recs:
            for vc,m in other.futurevars.items():
                if self.dom.isFutureRelevant(r,m): return True
        return False
    def Top(self):
        return  self.subproblems[-1]
    
    def Open(self):
        if self.close(): return None
        else: 
            return self.Top()

    def extend(self,prob):
        self.subproblems.append(SubProblemNode(prob))
    
    def close(self):
        def simplify(subp):
            def applys(s,t):    
                if type(t) is App:
                    return t.func(*map(lambda x: applys(s,x),t.args))
                elif type(t) is Var and t in s.keys():
                    return Var(s[t].vc,s[t].idx)
                elif type(t) is Var and not t in s.keys():
                    return Var(t.vc,t.idx)
                else:
                    return Rec(t.func,t.idx)
            def checkfur(y):
                for r in subp.recs:
                    if self.dom.isFutureRelevant(r,y): return True
                return False
            applysub = lambda s:lambda a: (applys(s,a[0]),applys(s,a[1]))
            substitution ={}
            grouping ={}
            vars= set()
            newsubp= []
            furtureRelevant = set()
            for x,y in subp.subproblem:
                if type(x) is Var and type(y) is Var:
                    check = True
                    for g in grouping.keys():
                        if x in grouping[g] or y in grouping[g]:
                            grouping[g].update(set([x,y]))
                            vars.add(x)
                            vars.add(y)
                            check = False
                    if check:
                        grouping[x]= set([x,y])
                elif not type(x) is Var or not type(y) is Var:
                    newsubp.append((x,y))
            for x,y in grouping.items():
                fr = False
                for z in y: 
                    if checkfur(x) or checkfur(z):
                        fr = True
                    substitution[z]=x
                if fr:
                    furtureRelevant.update(y)
            newsubp = set(map(applysub(substitution), newsubp))
            ret = SubProblem(newsubp,subp.recs)
            ret.futureRel = furtureRelevant
            return ret

        for x in reversed(range(0, len(self))):
            left = self.Top()
            right = self.subproblems[x]
            # I don't think this is needed but it speeds things up :: len(left) >= len(right) and
            if  x!=len(self) and not self.futureOverlap(left,right):
                if self.debug > 5: print(f"computing Subsumption between {x} and {len(self)}\n")
                prog = self.computerEncoding(simplify(left),simplify(right))
                if prog:
                    if self.debug >5: print("Answer Set Program:\n\n\t"+'\n\t'.join(prog)+"\n")
                    if self.solverASP(prog,x): return True
        return False
    
    def solverASP(self,prog,subp):
        def backToVars(t):
            shape = t.name.split("_")
            if len(shape) == 2: return Var(shape[0].upper(),int(shape[1]))
            else: return Rec(Func(shape[0].upper(),1),Idx(int(shape[2])))
        solver = clingo.Control([])
        solver.configuration.solve.models = 1
        solver.add('base',[], '\n'.join(prog))
        solver.ground([('base', [])])
        with solver.solve(yield_ = True, async_=True) as handle:
            model = next(iter(handle), None)
            if model:
                self.mapping = [(backToVars(atom.arguments[0]),backToVars(atom.arguments[1])) for atom in model.symbols(shown = True)]
                self.cycle = subp
                return True 
        return False
        
    def computerEncoding(self,left,right):
       # if len(left) < len(right) : return None # Probably not needed
        def compatibleTerms(x,y):
            if type(x) is App and type(y) is App and x.func.name ==y.func.name:
                ret = set()
                for x1,y1 in zip(x.args,y.args):
                    pairs = compatibleTerms(x1,y1)
                    if pairs==None: return None
                    else: ret.update(pairs)
                return ret
            elif not type(x) is App and not type(y) is App: return set([(x,y)])
            else: return None

        prog = []
        prog.extend(SubProblemStack.clingoBasic) 
        varsLeft =set()
        varsRight=set()
        recs =set(left.recs)
        recs.update(right.recs)
        tops =set()
        other=set()
        for p1 in right.subproblem:
            xt1,yt1 = p1
            validpairs={}
            other.add(p1)
            for p2 in left.subproblem:
                xt2,yt2 = p2
                varMaps=compatibleTerms(yt2,yt1)
                tops.add(p2)
                if varMaps:
                    varMaps.update(compatibleTerms(xt2,xt1))
                    key = "match("+str(p1)+","+str(p2)+")"
                    validpairs[key] = (f",other(Y), not match(Y,{str(p2)}), Y!={str(p1)}, not reflexive({str(p2)})",varMaps)
            if len(validpairs) !=0:
                prog.append("{"+';'.join(validpairs.keys())+"}>=1.")
                for pairing, codemap in validpairs.items():
                    code,map=codemap
                    for  xl,yl in map: 
                        prog.append(f":- {pairing}, not e({repr(xl)},{repr(yl)}){code}.")
            else:
                if self.debug >2: print("\t Subsumption failed on "+str(p1)+"\n")
                return None
        prog.append(''.join([f"varl({repr(y)})." for y in left.vars ])) 
        prog.append(''.join([f"varl({repr(y)})." for y in left.recs ])) 
        prog.append(''.join([f"varr({repr(y)})." for y in right.vars ]))
        prog.append(''.join([f"varr({repr(y)})." for y in right.recs ]))
        prog.append(''.join([f"recs({repr(y)})." for y in recs ]))
        prog.append(''.join([f"tops({repr(y)})." for y in tops ]))
        prog.append(''.join([f"other({repr(y)})." for y in other ]))
        prog.append(''.join([f"futureRel({repr(y)})." for y in left.futureRel ]))
        prog.append(''.join([f"futureRel({repr(y)})." for y in right.futureRel ]))

        return prog 


    def print_closures(self):
        if self.mapping:
            print("Recursion Found "+str(len(self))+" => "+str(self.cycle)+ " {"+ ' , '.join([f"{x}=>{y}" for x,y in self.mapping]) +"}")
            print()
            print("Subproblem "+str(len(self))+":")
            for x,y in self.Top().subproblem:
                print(f"\t{x} =?= {y}") 
            print()
            print("Subproblem "+str(self.cycle)+":")
            for x,y in self.subproblems[self.cycle].subproblem:
                print(f"\t{x} =?= {y}") 
            print()
            return True
        else:
            print("Non-Recursive, Finitely Unifiable.")
            return False
