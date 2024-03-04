from Term import *
from Namer import Namer
from Substitution import * 
from collections import defaultdict

from UnificationProblem import UnificationProblem
class InvalidFunctionException(Exception):
        def __init__(self,f):
            self.func = f
        def handle(self):
            print()
            print("Invalid Function: ",self.func.name+"/"+(self.func.arity))
            return None
class InvalidRecursionException(Exception):
        def __init__(self,w,c):
            self.w =w
            self.c= c
        def handle(self):
            print()
            print("Invalid Recursion: the interpreted class ",self.w+" occured in the definition of the iterpreted class "+str(self.c))
            return None
class SchematicSubstitution(Substitution):
    
    def __init__(self):
        super().__init__()
        self.symbols = []
        self.occuringVariables=set()
#Holds the mutually recursive  intrepreted variables
        self.mutual = defaultdict(set)
#Holds the indices of intrepreted variables
        self.recursions = defaultdict(set)
#Holds the variable classes associated with each interpreted class
# and the minimum and maximum value in each class. 
# for example, {'L': {'X': 0, 'R': 2, 'W': 0, 'Q': 0, 'Y': 2, 'Z': 0}}
        self.associated_classes_min = {}
        self.associated_classes_max = {}
        self.incrementors = {}   
        self.nesting = False
        self.primitive = True
        self.uniform =True
        self.simple = True

    def ground(self,i=0,localRecs=None):
        R =  localRecs  if localRecs else self.incrementors.keys()
        for x in R: 
            self.addBinding(*self.incrementors[x.vc if localRecs else x](x.idx if localRecs else i))
        for x,y in self.mapping.items():
            if type(y) is App: y.anchor=x

    def clear(self):
        self.mapping = {}

    def vars(self):
        return self.occuringVariables
    
    def updateType(self):
        if len(self.mutual.keys()) !=0:
            self.primitive= False
            self.uniform= False
            self.simple = False
            self.nesting = True
        for s in self.recursions.values():
            if len(s) > 1:
                self.primitive= False
                self.uniform= False
            if len(list(filter(lambda x: x > 1,s)))> 0:
                self.primitive= False

    def associated_classes(self,name):
        return self.associated_classes_max[name].keys()

    def isFutureRelevantTo(self,Recs:set[Rec],x:Var):
        for r in Recs:
            if self.isFutureRelevant(r,x): return True
        return False

    def isFutureRelevant(self,r:Rec,x:Var):
        if x.vc in self.associated_classes_min[r.vc].keys():
            minval = self.associated_classes_min[r.vc][x.vc]
            if r.idx +minval <= x.idx: return True
        return False

    def add_interpreted(self,sym,term,clean=False):
        def insert(i,term):
            if type(term) is App: return term.func(*map(lambda x: insert(i,x),term.args))
            elif type(term) is Var: return Var(term.vc,i+term.idx)
            elif type(term) is Rec: return Rec(term.vc,i+term.idx)
        
        self.associated_classes_min[sym] = {}
        self.associated_classes_max[sym] = {}
        self.extractclasses(sym,term)
        self.symbols.append(sym)
        self.updateType()
        self.occuringVariables.update(term.vos(Var))
        self.incrementors[sym]=lambda i: (Rec(sym,i),insert(i,term))


    def extractclasses(self,sym,term):
        if type(term) is Var:
            if not term.vc in self.associated_classes_min[sym].keys():
                self.associated_classes_min[sym][term.vc] = term.idx
                self.associated_classes_max[sym][term.vc] = term.idx
            else:
                self.associated_classes_min[sym][term.vc] = min(term.idx,self.associated_classes_min[sym][term.vc])
                self.associated_classes_max[sym][term.vc] = max(term.idx,self.associated_classes_max[sym][term.vc])
        elif type(term) is App:
            term.applyFunc(lambda a:self.extractclasses(sym,a))
        elif type(term) is Rec:
            if term.vc != sym: self.mutual[sym].add(term)
            self.recursions[sym].add(term.idx)
                
    def makePrimitive(self, uProb:UnificationProblem = None):
        if not self.uniform: return None, None
        if self.primitive: return self, Substitution()
        nu = Substitution()
# set of recursions defined in the schematic substitution which have index greater than 1
        symIdxPairs = [(x,list(y)[0])for x,y in self.recursions.items() if list(y)[0]> 1]
# We sort the resursions, reverse sort, by there in index
        symIdxPairs.sort(key=lambda x: x[1],reverse=True)
# We ground the schematic substitution at zero to extra the terms defining the step case 
        self.clear()
        self.ground(0)
        symtoTerm = { x.vc:y.instance() for x,y in self.mapping.items()}
        TermsToConsider = set(symtoTerm.values()).union(uProb.vos(Var) if uProb else set())
# This function collects all variables with the given variable class in a set of terms
        varsByVC = lambda vc,terms: [ x for x in reduce(lambda acc,val: acc.union(val),map(lambda t: t.vos(Var),terms)) if x.vc == vc]

#We loop through the non-primitive definition is the schematic substitution
        for i in range(0,len(symIdxPairs)):
            sym,idx = symIdxPairs[i]
# We apply the the current renaming to the term associated with sym in the current schematic substitution
            symTerm = symtoTerm[sym]
            assLCls = set([x.vc  for x in symTerm.vos(Var)])
            mu = Substitution()
            for x in assLCls:
                byModIdx = {i:set() for i in range(0,idx)}
                mNames=Namer(x+sym)
                occOfx = varsByVC(x,TermsToConsider)
# we collect the variables which are indexed the same mod idx
                for inst in occOfx: byModIdx[inst.idx % idx].add(inst)
# we collect the variables which are indexed the same mod idx
               
# We construct the substitution for the current symbol sym
                for i,v in byModIdx.items():
                    newName = mNames.current_name()
                    for inst in v:
                       mu += (inst,Var(newName,(inst.idx-i)//idx))
                    mNames.next_name()
# We construct the substitution reducing the current recursion to 1
            recSwap = Substitution() + ( Rec(sym,idx),Rec(sym,1))
# We apply both to the term found in the mapping.
            symtoTerm = {x:mu(y) for x,y in symtoTerm.items()}
            symtoTerm[sym] = recSwap(symtoTerm[sym])
# We compose the two substitutions
            nu = nu(mu)        
# construct the new primitive substitution
        prim = SchematicSubstitution()
        for x,y in symtoTerm.items(): prim.add_interpreted(x,y)
        return prim, nu