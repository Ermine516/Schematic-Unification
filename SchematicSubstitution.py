from Term import *
from Namer import Namer
from Substitution import * 
from collections import defaultdict
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
                
    def makePrimitive(self):
        def makeSub(sym,idx,names,t):
            mu =Substitution()
            if type(t) is App:
                nArgs = []
                for x in t.args:
                    tt, mu2 =  makeSub(sym,idx,names,x)
                    nArgs.append(tt)
                    mu = mu(mu2)
                return t.func(*tuple(nArgs)),mu 
            elif type(t) is Var:
                idxMod = t.idx % idx
                nName = names[t.vc][idxMod]
                nidx = 0 if idxMod == 0 else t.idx/idxMod
                nVar = Var(nName,idxMod)
                return nVar, mu+(t,Var(nName,idxMod))
            elif type(t) is Rec:
                return Rec(t.vc,1), mu
        if not self.uniform: return None, None
        if self.primitive: return self, Substitution()

        prim = SchematicSubstitution()
        symIdxPairs = [(x,list(y)[0])for x,y in self.recursions.items() if list(y)[0]> 1]
        symIdxPairs.sort(key=lambda x: x[1],reverse=True)
        nonPrimSyms,_ = zip(*symIdxPairs)
        nu = Substitution()
        self.clear()
        self.ground(0)
        pairs = {x:self.mapping[Rec(x,0)].instance() for x in self.symbols if not x in nonPrimSyms}
        for i in range(0,len(symIdxPairs)):
            sym,idx = symIdxPairs[i]
            assLCls = self.associated_classes_min[sym].keys()
            symTerm = nu(self.mapping[Rec(sym,0)])
            assLClsNames = {}
            for x in assLCls:
                mNames=Namer(x+sym)
                names = {0:x}
                for y in range(1,idx):
                    names[y]=mNames.current_name()
                    mNames.next_name()
                assLClsNames[x]= names
            nt, mu = makeSub(sym,idx,assLClsNames,symTerm)
            nu = nu(mu)
            pairs[sym] = nt
        pairs = [(x,nu(y)) for x,y in pairs.items()]
        for x,y in pairs:
            prim.add_interpreted(x,y)
        return prim, nu