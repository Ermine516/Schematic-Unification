from Term import *
import clingo
import clingo.script
class SubProblem:
    def __len__(self):
        return len(self.subproblem)
        
    def __init__(self,subproblem):        
        self.subproblem = subproblem
        self.vars =set()
        self.cyclic = False

class SubProblemStack:
    clingoBasic = ["#show e/2.", "1{ e(X,Y): varr(Y)}1:- varl(X)." ":- e(X1,Y),e(X2,Y),X1!=X2."]
    def __init__(self,prob,debug=0):
        self.cycle = -1
        self.mapping =None
        self.debug = debug
        self.subproblems = [SubProblem(prob)]
    
    def __len__(self):
        return len(self.subproblems)-1
    
    def __add__(self,val):
        if type(val) is SubProblem:
            self.subproblems.append(val) 
        else:
            raise TypeError(f"Type of val is {type(val)} and should be SubProblem")
        return self
    def Top(self):
        return  self.subproblems[-1]
    
    def Open(self):
        if self.close(): return None
        else: 
            return self.Top()

    def extend(self,prob):
        self.subproblems.append(SubProblemNode(prob))

    def close(self):
        for x in reversed(range(0, len(self))):
            left = self.Top()
            right = self.subproblems[x]
            if len(left) == len(right) and x!=len(self):
                if self.debug > 2: print(f"computing Subsumption between {x} and {len(self)}\n")
                prog = self.computerEncoding(left,right)
                if prog:
                    if self.debug >3: print("Answer Set Program:\n\n\t"+'\n\t'.join(prog)+"\n")
                    return self.solverASP(prog,x)
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
        for p1 in left.subproblem:
            xt1,yt1 = p1
            validpairs={}
            for p2 in right.subproblem:
                xt2,yt2 = p2
                varMaps=compatibleTerms(yt1,yt2)
                if varMaps:
                    varMaps.update(compatibleTerms(xt1,xt2))
                    key = "match("+str(p1)+","+str(p2)+")"
                    validpairs[key] = varMaps
            if len(validpairs) !=0:
                prog.append("1{"+';'.join(validpairs.keys())+"}1.")
                for pairing, map in validpairs.items():
                    for  xl,yl in map: 
                        prog.append(f":- {pairing}, not e({repr(xl)},{repr(yl)}).")
                        varsLeft.add(xl)
                        varsRight.add(yl)
            else:
                if self.debug >2: print("\t Subsumption failed on "+str(p1)+"\n")
                return None
        prog.append(''.join([f"varl({repr(y)})." for y in varsLeft ])) 
        prog.append(''.join([f"varr({repr(y)})." for y in varsRight ]))
        return prog  


    def print_closures(self):
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
