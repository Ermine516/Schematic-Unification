from typing import Set, Tuple, Dict
from collections import defaultdict
from functools import reduce

class recterm:

    def __init__(self, term,vclass="X"):
        self.enum=0
        self.vclass = vclass
        self.varsenum = {}
        self.revvarsenum = {}
        def initialize(t):
            if type(t) is Idx:
                v= Var(self.vclass,t.number)
                self.varsenum[t.number],self.revvarsenum[v] = v,t.number
                self.enum = max(t.number,self.enum)+1
                return t
            elif type(t) is Var:
                if not t in self.revvarsenum.keys():
                    self.varsenum[self.enum],self.revvarsenum[t] = t,self.enum
                    replace = Idx(self.enum)
                    self.enum+=1
                    return replace
                elif  t in self.revvarsenum.keys():
                    return Idx(self.revvarsenum[t])
            elif type(t) is App and not t.func.Rec:
                    return t.func(*map(lambda a: initialize(a),t.args))
            elif type(t) is App and t.func.Rec:
                self.func = t.func
                return t
            else:
                raise Exception

        self.term = initialize(term)



    def increment(self,idx):
        return self.increment_help(self.term,idx.number)
    def increment_help(self,t,num):
        if type(t) is Idx:
            if not t.number+num in self.varsenum.keys():
                self.varsenum[t.number+num] = Var(self.vclass,(t.number+num))
            return self.varsenum[t.number+num]
        elif type(t) is App and not t.func.Rec:
            return t.func(*map(lambda a:  self.increment_help(a,num),t.args))
        elif type(t) is App and t.func.Rec:
            return t.func(Idx(num+1))
        else: raise Exception

class Func:
    """Immutable data type representing a function symbol."""
    name: str
    arity: int
    Rec:bool
    def __init__(self, name, arity,rec=False):
        self.name = name
        self.arity = arity
        self.Rec = rec
        self.assoc_classes=[]
    def add_class(self,vclass,gap):
        self.assoc_classes.append((vclass,gap))

    def __eq__(self, other):
        return isinstance(other, __class__) and self.name == other.name and self.arity == other.arity

    def __hash__(self):
        #TODO: can be cached
        return hash((self.name, self.arity))

    def __repr__(self):
        return f"{self.name}/{self.arity}"

    def __call__(self, *args):
        if len(args) != self.arity:
            raise ValueError()
        return App(self, *args)


class Term:
    """Type of terms for which we can do unification and instantiation."""
    def inducApp(self,f):
        ret =[]
        for x in self.args: ret.append(f(x))
        return ret
    def occurs(self,t):
        if self == t:
            return True
        elif type(t) is App:
            return reduce(lambda a,b: a or self.occurs(b),t.args,False)
        else:
            False
    def isalpha(self,t):
            varpairs = Term.isalphahelper(self,t)
            if not varpairs: return False
            check = {}
            for x,y in varpairs:
                if x in check.keys() and check[x] != y: return False
                elif x.vclass != y.vclass: return False
                check[x] = y
            return True

    def isalphahelper(s,t):
        if type(s) != type(t): return None
        if type(s) is Idx: return []
        elif type(s) is Var: return [(Var.find(s),Var.find(t))]
        elif type(s) is App and s.func!= t.func: return None
        elif type(s) is App:
            ret =[]
            for x,y in zip(s.args,t.args):
                res = Term.isalphahelper(x,y)
                if not res: return None
                ret.extend(res)
            return ret
        else: raise Exception
    pass

class Var(Term):
    """Immutable named variable that is unifiable with any other term."""
    name: str
    def union(x,y):
         if type(x) is Var and type(y) is Var:
             x,y=Var.find(x),Var.find(y)
             if x==y: return x
             if x.size < y.size: x,y = y,x
#Updates the size and number of occurances
             x.size, x.occ = x.size+y.size,x.occ+y.occ
#moves the right side of the multiequation to the representative
             x.terms.extend(y.terms)
#Resets the non-rep
             y.rep,y.terms, y.occ =x,[],0
         return x
    def find(x):
        if type(x) is Var:
            while x.rep != x: x,x.rep = x.rep,x.rep.rep
            return x
        else:
            return x
    def clean(self,active):
        self.terms = []
        self.occ = 0
        self.active = active

    def __init__(self, vclass,idx,active = False):
        self.vclass = vclass
        self.idx = idx
        # for union-find
        self.rep = self
        self.size =1
        self.terms = []
        self.occ = 0
        self.active=active
    def format(self):
        return str(self.occ)+":{" +self.__str__()+"}"+" =?= "+"{{"+','.join([str(t) for t in self.terms])+"}}"
    def __eq__(self, other):
        return isinstance(other, __class__) and self.vclass == other.vclass  and self.idx == other.idx

    def __hash__(self):
        #TODO: can be cached
        return hash((self.vclass,self.idx))

    def __str__(self):
        return f"{Var.find(self).vclass}"+f"{Var.find(self).idx}"

    def __repr__(self):
        return f"{self.vclass}"+f"{self.idx}"

class Idx(Term):
    def __init__(self,idx):
        self.number = idx

    def __str__(self):
        return str(self.number)

    def __eq__(self, other):
        return isinstance(other, __class__) and self.number == other.number

    def __hash__(self):
        return hash((self.number))

    def __repr__(self):
        return str(self.number)

class App(Term):
    """Immutable fully-applied function term."""
    func: Func
    args: Tuple[Term]

    def __init__(self, func, *args):
        assert func.arity == len(args)
        self.func = func
        self.args = tuple(args)

    def __str__(self):
        argsstr = "("+','.join([str(x) for x in self.args])+")" if len(self.args)>0 else ""
        return self.func.name+argsstr

    def __eq__(self, other: "App"):
        return isinstance(other, __class__) and self.func == other.func and self.args == other.args

    def __hash__(self):
        #TODO: can be cached
        return hash((self.func, self.args))

    def __repr__(self):
        args = ("" if not self.args
                else '(' + ','.join(str(a) for a in self.args) + ')')
        return f"{self.func.name}{args}"
