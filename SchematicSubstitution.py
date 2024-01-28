from Term import *

class SchematicSubstitution:
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
            print("Invalid Recursion: the interpreted class ",self.w+" occured in the definition of the iterpreted class "+self.c)
            return None
    class ClassOverlapException(Exception):
        def __init__(self,c1,c2,m):
            self.c1 =c1
            self.c2= c2
            self.mappings = m
        def handle(self):
            print()
            print("The definitions of "+str(self.c1)+" and "+str(self.c2)+"overlap:\n"+str(self.mappings[self.c1])+"\n"+str(self.mappings[self.c2]))
            return None

    def __init__(self,nesting=False):
        self.symbols = []
        self.mappings = {}
        self.associated_classes = {}
        self.varsenum ={}
        self.revvarsenum ={}
        self.nesting = nesting

    def reset(self,nesting=False):
        self.symbols = []
        self.mappings = {}
        self.associated_classes = {}
        self.varsenum ={}
        self.revvarsenum ={}
        self.nesting = nesting

    def isFutureRelevant(self,r,x):
        if x.vc in self.associated_classes[r.func.name].keys():
            minval = self.associated_classes[r.func.name][x.vc]
            if r.idx.number +minval <= x.idx: return True
        return False
    def add_relevent_vars(self,terms,clean=False):
        for x,y in self.varsenum.items():
            for t in terms:
                self.add_relevent_vars_helper(x,t,clean)
    def add_relevent_vars_helper(self,rec,term,clean=False):
        if  type(term)  is Var:
            if term.vc in self.varsenum[rec].keys():
                if clean: term.reset()
                self.varsenum[rec][term.vc][term.idx],self.revvarsenum[rec][term.vc][term] = term, term.idx
        elif type(term) is App:
            for t in term.args:
                self.add_relevent_vars_helper(rec,t)
    def add_mapping(self,sym,term,clean=False):
        if sym.arity != 1: raise InvalidFunctionException(sym)
        self.associated_classes[sym.name] = {}
        self.extractclasses(sym.name,term)
        self.symbols.append(sym)
        class_groups = list(map(lambda a: (a,set(self.associated_classes[a].keys())),self.associated_classes.keys()))
        while len(class_groups)!= 0:
            vclass,cur = class_groups.pop()
            for x,y in  class_groups:
                if len(cur.intersection(y))!= 0: raise ClassOverlapException(vclass,x,self.mappings)
        self.mappings[sym.name] = term

        self.varsenum[sym.name] = {x:{} for x in self.associated_classes[sym.name] }
        self.revvarsenum[sym.name] ={x:{} for x in self.associated_classes[sym.name]}
        self.initialize(term,sym.name,clean)

    def initialize(self,t,sym,clean=False):
        if type(t) is Var:
            if clean: t.reset()
            if not t in self.revvarsenum[sym][t.vclass()].keys():
                self.varsenum[sym][t.vclass()][t.id()],self.revvarsenum[sym][t.vclass()][t] = t,t.id()
                return t
            elif  t in self.revvarsenum[sym][t.vclass()].keys():
                return t
        elif type(t) is App:
                return t.func(*map(lambda a: self.initialize(a,sym),t.args))
        elif type(t) is Rec:
            return t
        else:
            raise Exception

    def increment(self,sym,idx,clean=False):
        return self.increment_help(self.mappings[sym],sym,idx.number,clean)

    def increment_help(self,t,sym,num,clean=False):
        if type(t) is Var:
            if not t.idx+num in self.varsenum[sym][t.vc].keys():
                newvar = Var(t.vc,(t.idx+num))
                self.varsenum[sym][t.vc][t.idx+num],self.revvarsenum[sym][t.vc][newvar] = newvar, t.idx+num
                return newvar
            else:
                if clean:
                    self.varsenum[sym][t.vc][t.idx+num].reset()
                return Var.find(self.varsenum[sym][t.vc][t.idx+num])
        elif type(t) is App:
            return t.func(*map(lambda a:  self.increment_help(a,sym,num,clean),t.args))
        elif type(t) is Rec:
            return t.func(Idx(num+(t.idx.number if t.func.name == sym else 0)))
        else: raise Exception

    def extractclasses(self,sym,term):
        if type(term) is Var:
            if not term.vc in self.associated_classes[sym].keys():
                self.associated_classes[sym][term.vc] = term.idx
            else:
                self.associated_classes[sym][term.vc] = min(term.idx,self.associated_classes[sym][term.vc])
        elif type(term) is App:
            term.inducApp(lambda a:self.extractclasses(sym,a))
        elif not self.nesting and type(term) is Rec:
            if term.func.name != sym:
                raise self.InvalidRecursionException(term.func.name,sym)
