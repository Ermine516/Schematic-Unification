from Term import *
class Interpretation:
    class InvalidFunctionException(Exception):
        def __init__(self,f):
            self.func = f
        def handle(self):
            print()
            print("Invalid Function: ",self.func.name+"/"+(self.func.arity))
            return None
    class InvalidRecursionError(Exception):
        def __init__(self,w,c):
            self.w =w
            self.c= c
        def handle(self):
            print()
            print("Invalid Recursion: ",self.w+" occured in the definition of "+self.c)
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

    def __init__(self):
        self.symbols = []
        self.mappings = {}
        self.associated_classes = {}
        self.varsenum ={}
        self.revvarsenum ={}

    def add_mapping(self,sym,term):
        if sym.arity != 1: raise InvalidFunctionException(sym)
        self.symbols.append(sym)
        self.associated_classes[sym.name] = {}
        self.extractclasses(sym.name,term)
        class_groups = list(map(lambda a: (a,set(self.associated_classes[a].keys())),self.associated_classes.keys()))
        while len(class_groups)!= 0:
            vclass,cur = class_groups.pop()
            for x,y in  class_groups:
                if len(cur.intersection(y))!= 0: raise ClassOverlapException(vclass,x,self.mappings)
        self.mappings[sym.name] = term

        self.varsenum[sym.name] = {x:{} for x in self.associated_classes[sym.name] }
        self.revvarsenum[sym.name] ={x:{} for x in self.associated_classes[sym.name]}
        self.initialize(term,sym.name)

    def initialize(self,t,sym):
        if type(t) is Var:
            if not t in self.revvarsenum[sym][t.vclass].keys():
                self.varsenum[sym][t.vclass][t.idx],self.revvarsenum[sym][t.vclass][t] = t,t.idx
                return t
            elif  t in self.revvarsenum[sym][t.vclass].keys():
                return t
        elif type(t) is App:
                return t.func(*map(lambda a: self.initialize(a,sym),t.args))
        elif type(t) is Rec:
            return t
        else:
            raise Exception

    def increment(self,sym,idx):
        return self.increment_help(self.mappings[sym],sym,idx.number)

    def increment_help(self,t,sym,num):
        if type(t) is Var:
            if not t.idx+num in self.varsenum[sym][t.vclass].keys():
                newvar = Var(t.vclass,(t.idx+num))
                self.varsenum[sym][t.vclass][t.idx+num],self.revvarsenum[sym][t.vclass][newvar] = newvar, t.idx+num
                return newvar
            else: return self.varsenum[sym][t.vclass][t.idx+num]
        elif type(t) is App:
            return t.func(*map(lambda a:  self.increment_help(a,sym,num),t.args))
        elif type(t) is Rec:
            return t.func(Idx(num+1))
        else: raise Exception

    def extractclasses(self,sym,term):
        if type(term) is Var:
            if not term.vclass in self.associated_classes[sym].keys():
                self.associated_classes[sym][term.vclass] = term.idx
            else:
                self.associated_classes[sym][term.vclass] = min(term.idx,self.associated_classes[sym][term.vclass])
        elif type(term) is App:
            term.inducApp(lambda a:self.extractclasses(sym,a))
        elif type(term) is Rec:
            if term.func.name != sym:
                raise InvalidRecursionError(term.func.name,sym)
