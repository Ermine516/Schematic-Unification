from Term import *
import clingo
import clingo.script
from SubProblem import *
import time

class StabilityViolationFinalException(Exception):
        def __init__(self):
            self.nothing = None
        def handle(self,debug,start_time):           
            if debug == 0:
                print(f"\t Not Stable --- {round(time.time() - start_time,3)} seconds ---")
            return False, (time.time() - start_time)
        pass

class StabilityViolationException(Exception):
        def __init__(self,left,sps,stab):
            self.left = left
            self.sps = sps
            self.st =stab
        def handle(self,debug,start_time,ret):
            print(f"Problem not stable (stab Bound:{self.sps.stabRatio}, current:{self.st}):")
            print("\t",self.left)   
            print("""Do you wish to continue and update the stability point? To continue type OK and Press Enter.""")
            x = input()
            if x.lower() =="ok":
                self.sps.stabRatio=self.st 
                return ret
            else:      
                raise StabilityViolationFinalException()
        pass

class SubProblemStack:
# Base ASP program
    
    clingoBasic = ["#show e/2.","#defined futureRel/2.","#defined match/2.",\
    ":- e(X,Y),futureRel(l,X),not futureRel(r,Y). " ,":- e(X,Y),not futureRel(l,X), futureRel(r,Y). ",\
    ":- e(X,Y1), e(X,Y2), Y1!=Y2." ,":- other(X), not match(X,_)." ,\
     ":- tops(X), not match(_,X).",\
     "1{ e(X,Y): varr(Y)}1:- varl(X).",":-  varr(Y), not e(_,Y).",\
     ":- varl(X),recs(X),#count{Y: recs(Y),X!=Y,e(X,Y)}=0.",\
     ":- e(X,Y),classmatch(Z1,X),classmatch(Z2,Y), Z1!=Z2.",":-futureRel(l,X),futureRel(r,X).",\
     ":-  varl(X), varr(X), not e(X,X)." ]


   

    def __init__(self,unifProb,schSubs,debug=0):
        self.cycle = -1
        self.mapping =None
        self.debug = debug
        self.dom = schSubs
        stabProb = unifProb.increment(self.dom)
        self.stabBound = max(stabProb.depth(),stabProb.maxIdx())
        self.stabRatio = -1
        self.subproblems = [SubProblem(unifProb)]
        self.subproblems[0].NormalSimplifiedForm= self.subproblems[0].simplify(self.dom).normalization() 
        self.iterstate =0
    def __len__(self):
        return len(self.subproblems)-1
    
    def __add__(self,val):
        if type(val) is SubProblem:
            self.subproblems.append(val) 
        else:
            raise TypeError(f"Type of val is {type(val)} and should be SubProblem")
        return self
    def __iter__(self):
        self.iterstate=0
        return self
    
    def __next__(self):
        if self.iterstate ==len(self)+1: raise StopIteration
        ret = self.subproblems[self.iterstate]
        self.iterstate = self.iterstate +1
        return ret
    
    def futureOverlap(self,current,other):
        for _,m in other.futurevars.items():
            if self.dom.isFutureRelevantTo(current.recs,m): return True
        return False
    def Top(self):
        return  self.subproblems[-1]
    
    def Open(self,start_time):
        try:
            if self.close(): 
                return None
            else: 
                return self.Top()
        except StabilityViolationException as e:
            return e.handle(self.debug,start_time,self.Top())
    def close(self):
        left = self.Top()
        leftNorm = left.NormalSimplifiedForm if  left.NormalSimplifiedForm else left.simplify(self.dom).normalization()
        left.NormalSimplifiedForm = leftNorm
        left.stab = len(leftNorm.subproblem.vos(Var))
        for x in reversed(range(0, len(self))):
            right = self.subproblems[x]
            if  x!=len(self) and not self.futureOverlap(left,right):
                if self.debug > 5: print(f"computing Subsumption between {x} and {len(self)}\n")
                rightNorm = right.simplify(self.dom).normalization()
                if len(self) >= self.stabBound and self.stabRatio==-1:
                    for p in self.subproblems: 
                        if p.stab ==-1: p.stab = len(rightNorm.subproblem.vos(Var))
                    self.stabRatio = max((p.stab for p in self.subproblems))
                if left.stab > self.stabRatio and len(self) >= self.stabBound: 
                    raise StabilityViolationException(leftNorm,self,left.stab) 
                if len(self) < self.stabBound:
                    return False
                prog = self.computerEncoding(leftNorm,rightNorm)
                if prog:
                    if self.debug >5: print("Answer Set Program:\n\n\t"+'\n\t'.join(prog)+"\n")
                    if self.solverASP(prog,x): return True
        return False
    
    def solverASP(self,prog,subp):
        def backToVars(t):
            shape = t.name.split("_")
            if len(shape) == 2: return Var(shape[0].upper(),int(shape[1]))
            else: return Rec(shape[0].upper(),int(shape[2]))
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
# Some variables may remain in all instances 
# These "dead variables" are ok as eventually they will no longer 
# be futureRel and thus are essentially constants
        for x in left.vars.intersection(right.vars):
            if x in left.futureRel or x in right.futureRel: return None
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
        recs =set(left.recs)
        recs.update(right.recs)
        tops =set()
        other=set()
        for p1 in right.subproblem:
            xt1,yt1 = p1[0],p1[1]
            validpairs={}
            other.add(p1)
            for p2 in left.subproblem:
                xt2,yt2  = p2[0],p2[1]
                varMaps=compatibleTerms(yt2,yt1)
                tops.add(p2)
                if varMaps:
                    varMaps.update(compatibleTerms(xt2,xt1))
                    key = "match("+repr(p1)+","+repr(p2)+")"
                    validpairs[key] = (f",other(Y), not match(Y,{repr(p2)}), Y!={repr(p1)}",varMaps)
            if len(validpairs) !=0:
                prog.append("{"+';'.join(validpairs.keys())+"}>=1.")
                for pairing, codemap in validpairs.items():
                    code,map=codemap
                    for  xl,yl in map: 
                        prog.append(f":- {pairing}, not e({repr(xl)},{repr(yl)}){code}.")
            else:
                if self.debug >2: print("\t Subsumption failed on "+str(p1)+"\n")
                return None
        prog.append(''.join([f"varl({repr(y)}). classmatch({y.vc.lower()},{repr(y)})." for y in left.vars ])) 
        prog.append(''.join([f"varl({repr(y)}). classmatch({y.vc.lower()},{repr(y)})." for y in left.recs ])) 
        prog.append(''.join([f"varr({repr(y)}). classmatch({y.vc.lower()},{repr(y)})." for y in right.vars ]))
        prog.append(''.join([f"varr({repr(y)}). classmatch({y.vc.lower()},{repr(y)})." for y in right.recs ]))
        prog.append(''.join([f"recs({repr(y)})." for y in recs ]))
        prog.append(''.join([f"tops({repr(y)})." for y in tops ]))
        prog.append(''.join([f"other({repr(y)})." for y in other ]))
        prog.append(''.join([f"futureRel(l,{repr(y)})." for y in left.futureRel ])) 
        prog.append(''.join([f"futureRel(r,{repr(y)})." for y in right.futureRel ])) 
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
