from SchematicSubstitution import SchematicSubstitution
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
    cycle:int # the position of the subProblemStack which cycles with the top
    mapping : list[tuple[Var,Var]]
    debug: int # debug level
    dom : SchematicSubstitution # used for computing subproblems and future relevance
    stabProb : UnificationProblem # The problem used for computing stability bounds
    stabBound : int # the stability bound
    stabRatio : int # the stability ratio 
    subproblems : list[SubProblem] # The stack of subproblems
    iterstate : int
# The base for the ASP problem computing subsumption   
    clingoBasic : list[str] = [\
# e/2 is the mapping and is the only atom returned by clingo
# futureRel/2 and match/2 are not always present in the ASP program
    "#show e/2.","#defined futureRel/2.","#defined match/2.",\
# the mapping must map current future relevant variables to past future relevant variables
    ":- e(X,Y),futureRel(l,X),not futureRel(r,Y). " ,":- e(X,Y),not futureRel(l,X), futureRel(r,Y). ",\
# a variable cannot be mapped to two distinct variables
    ":- e(X,Y1), e(X,Y2), Y1!=Y2." ,\
# For every binding in the right subproblem there must be a match with a binding in the left subproblem
    ":- right(X), not match(X,_)." ,\
# For every binding in the left subproblem there must be a match with a binding in the right subproblem
    ":- left(X), not match(_,X).",\
# For each variable in the left subproblem there is a unique variable in the right subproblem it is mapped to
     "1{ e(X,Y): varr(Y)}1:- varl(X).",\
# Every variable in the right subproblem must be part of the mapping
     ":-  varr(Y), not e(_,Y).",\
# recs must map to recs
    ":- varl(X),recs(X),e(X,Y), not recs(Y).",\
# Variables should map to variables of the same class
     ":- e(X,Y),classmatch(Z1,X),classmatch(Z2,Y), Z1!=Z2.",\
# No variable should be future relevant to both problems
    ":-futureRel(l,X),futureRel(r,X).",\
# If a variable is in both problems then it must map to itself
     ":-  varl(X), varr(X), not e(X,X)."\
    ]


    def __init__(self,unifProb:UnificationProblem,schSubs:SchematicSubstitution,debug:int=0):
        self.cycle = -1
        self.mapping =None
        self.debug = debug
        self.dom = schSubs
        stabProb = unifProb.increment(self.dom)
        self.stabBound = max(stabProb.depth(),stabProb.maxIdx())
        self.stabRatio = -1
        self.subproblems = [SubProblem(unifProb)]
# We precompute the simplified normal form of the problem and its stability value.
        self.subproblems[0].NormalSimplifiedForm= self.subproblems[0].simplify(self.dom).normalization() 
        self.subproblems[0].stab = len(self.subproblems[0].NormalSimplifiedForm .subproblem.vos(Var))
# Used for interating through the subproblem
        self.iterstate =0
    
    def __len__(self):
        return len(self.subproblems)-1
    
    def __add__(self,val):
        if type(val) is SubProblem: self.subproblems.append(val) 
        else: raise TypeError(f"Type of val is {type(val)} and should be SubProblem")
        return self
    
    def __iter__(self):
        self.iterstate=0
        return self
    
    def __next__(self):
        if self.iterstate ==len(self)+1: raise StopIteration
        ret = self.subproblems[self.iterstate]
        self.iterstate = self.iterstate +1
        return ret
    
    def Top(self):
        return  self.subproblems[-1]
    
    def Open(self,start_time):
        try:
            if self.close(): return None
            else: return self.Top()
        except StabilityViolationException as e: return e.handle(self.debug,start_time,self.Top())
    
    def close(self):
        left = self.Top()
        left.NormalSimplifiedForm = left.simplify(self.dom).normalization()
        left.stab = len(left.NormalSimplifiedForm .subproblem.vos(Var))
# We only check subsumption once we reach the stability bound
        if len(self) < self.stabBound: return False
        for x in reversed(range(0, len(self))):
            right = self.subproblems[x]
# checks if there are variables in right which are future relevent to left
            if  [ m for _,m in right.futurevars.items() if self.dom.isFutureRelevantTo(left.recs,m)] != []: continue
            if self.debug > 5: print(f"computing Subsumption between {x} and {len(self)}\n")
# Checks if we reached the stability bound and computes the stability ratio
            if len(self) >= self.stabBound and self.stabRatio==-1: self.stabRatio = max((p.stab for p in self.subproblems))
# If we over shoot the stability ratio raise an exception
            if left.stab > self.stabRatio and len(self) >= self.stabBound: raise StabilityViolationException(left.NormalSimplifiedForm ,self,left.stab) 
# Constructs the ASP program computing mappings    
            prog = self.computerEncoding(left.NormalSimplifiedForm ,right.NormalSimplifiedForm)
            if not prog: continue
            if self.debug >5: print("Answer Set Program:\n\n\t"+'\n\t'.join(prog)+"\n")
# Runs the ASP program and returns true if a model is found
            if self.solverASP(prog,x): return True
        return False
    
    def solverASP(self,prog,subp):
# converts the ASP output into variables 
        def backToVars(t):
            shape = t.name.split("_")
            if len(shape) == 2: return Var(shape[0].upper(),int(shape[1]))
            return Rec(shape[0].upper(),int(shape[2]))
        
        solver = clingo.Control([])
        solver.configuration.solve.models = 1
        solver.add('base',[], '\n'.join(prog))
        solver.ground([('base', [])])
        with solver.solve(yield_ = True, async_=True) as handle:
            model = next(iter(handle), None)
            if not model: return False
            self.mapping = [(backToVars(atom.arguments[0]),backToVars(atom.arguments[1])) for atom in model.symbols(shown = True) if  atom.arguments[0] != atom.arguments[1]]
            self.cycle = subp
            return True 
        
    def computerEncoding(self,left,right):
# Some variables may remain in all instances 
# These "dead variables" are always mapped to themselves
# be futureRel and thus are essentially constants
        for x in left.vars.intersection(right.vars):
            if x in left.futureRel or x in right.futureRel: return None
# Checks if the terms x and y are compatible in that a mapping can make them equivalent
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

        prog = list(SubProblemStack.clingoBasic)
        recs =set(left.recs).union(set(right.recs))
        leftBind =set()
        rightBind=set()
        for p1 in right.subproblem:
            xt1,yt1 = p1
            validpairs={}
            rightBind.add(p1)
            for p2 in left.subproblem:
                xt2,yt2  = p2
                varMaps=compatibleTerms(yt2,yt1)
                leftBind.add(p2)
                if not varMaps: continue
                varMaps.update(compatibleTerms(xt2,xt1))
                key = "match("+repr(p1)+","+repr(p2)+")"
                validpairs[key] = (f",right(Y), not match(Y,{repr(p2)}), Y!={repr(p1)}",varMaps)
            if len(validpairs) ==0: 
                if self.debug >2: print("\t Subsumption failed on "+str(p1)+"\n")
                return None
#encodes all the pairings between p1 and the left subproblem and states that at least one must hold
            prog.append("{"+';'.join(validpairs.keys())+"}>=1.")
#encodes the cases when the match holds but the mapping does not include the appropriate variable mappings
            for pairing, codemap in validpairs.items():
                for  xl,yl in codemap[1]: prog.append(f":- {pairing}, not e({repr(xl)},{repr(yl)}){codemap[0]}.")
#adding all the properties of the subproblems required for computing the mapping                
        prog.append(''.join([f"varl({repr(y)}). classmatch({y.vc.lower()},{repr(y)})." for y in left.vars ])) 
        prog.append(''.join([f"varl({repr(y)}). classmatch({y.vc.lower()},{repr(y)})." for y in left.recs ])) 
        prog.append(''.join([f"varr({repr(y)}). classmatch({y.vc.lower()},{repr(y)})." for y in right.vars ]))
        prog.append(''.join([f"varr({repr(y)}). classmatch({y.vc.lower()},{repr(y)})." for y in right.recs ]))
        prog.append(''.join([f"recs({repr(y)})." for y in recs ]))
        prog.append(''.join([f"left({repr(y)})." for y in leftBind ]))
        prog.append(''.join([f"right({repr(y)})." for y in rightBind ]))
        prog.append(''.join([f"futureRel(l,{repr(y)})." for y in left.futureRel ])) 
        prog.append(''.join([f"futureRel(r,{repr(y)})." for y in right.futureRel ])) 
        return prog 


    def print_closures(self):
        if not self.mapping:
            print("Non-Recursive, Finitely Unifiable.")
            return False
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
           
