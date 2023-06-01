from typing import Set, Tuple, Dict
from collections import defaultdict
from functools import reduce



class Func:
    """Immutable data type representing a function symbol."""
    name: str
    arity: int
    def __init__(self, name, arity):
        self.name = name
        self.arity = arity

    def __eq__(self, other):
        return isinstance(other, __class__) and self.name == other.name and self.arity == other.arity

    def __hash__(self):
        return hash((self.name, self.arity))

    def __repr__(self):
        return f"{self.name}/{self.arity}"

    def __call__(self, *args):
        if len(args) != self.arity: raise ValueError()
        if len(args) == 1 and type(args[0]) is Idx: return Rec(self, *args)
        else: return App(self, *args)


class Term:
    """Type of terms for which we can do unification and instantiation."""
    def inducApp(self,f):
        ret =[]
        for x in self.args: ret.append(f(x))
        return ret
    def containsVar(self,v):
            if type(self) is Var and self==v: return True
            elif type(self) is App: return reduce(lambda a,b: a or b.containsVar(v),self.args,False)
            return False
    def apply_unif(self,unif):
            if type(self) is Var:
                if self.vc in unif.keys() and self.idx in unif[self.vc].keys():
                    l,r = unif[self.vc][self.idx]
                    return r.apply_unif(unif)
                else: return self
            elif type(self) is App: return self.func(*map(lambda a: a.apply_unif(unif),self.args))
            elif type(self) is Rec: return self
    def apply_unif_vc(self,rVar,cVar,unif):
            if type(self) is Var and self.vc==rVar.vc:
                l,r = unif[rVar.vc][self.idx]
                return r.apply_unif_vc(rVar,cVar,unif)
            elif type(self) is Var and self.vc!=rVar.vc:
                if self.vc in unif.keys() and self.idx in unif[self.vc].keys() and unif[self.vc][self.idx][1].containsVar(cVar):
                    return unif[self.vc][self.idx][1].apply_unif({cVar.vc:{cVar.idx:(cVar,rVar)}})
                else: return self
            elif type(self) is App: return self.func(*map(lambda a: a.apply_unif_vc(rVar,cVar,unif),self.args))
            elif type(self) is Rec: return self

    def occurs(self,t):
        if self == t:
            return True
        elif type(t) is App:
            return reduce(lambda a,b: a or self.occurs(b),t.args,False)
        else:
            False
    def isalpha(self,t):
            varpairs = Term.isalphahelper(self,t)
            if not varpairs: return None
            check = {}
            for x,y in varpairs:
                if type(x) is Rec: continue
                elif x in check.keys() and check[x] != y: return None
                elif x.vclass() != y.vclass(): return None
                check[x] = y
            return check

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
        elif type(s) is Rec  and s.func == t.func and s.idx.number >=t.idx.number: return [(s,t)]
        else: return None
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
             for c in y.maxsub.keys():
                 if not c in x.maxsub.keys(): x.maxsub[c]=0
                 x.maxsub[c] = max(x.maxsub[c],y.maxsub[c])
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

    def reset(self):
        self.rep = self
        self.size =1
        self.terms = []
        self.occ = 0
        self.active = False

    def vclass(self):
        return Var.find(self).vc
    def id(self):
        return Var.find(self).idx
    def ts(self):
        return Var.find(self).terms
    def occs(self):
        return Var.find(self).occ
    def setocc(self,i):
        Var.find(self).occ = Var.find(self).occ+i
    def act(self):
        return Var.find(self).active

    def __init__(self, vc,idx,active = False):
        self.vc = vc
        self.idx = idx
        # for union-find
        self.rep = self
        self.size =1
        self.terms = []
        self.occ = 0
        self.active=active
#We need to remember the largest subordinate class.
        self.maxsub = {}
        self.maxsub[vc]= idx

    def format(self):
        return str(Var.find(self).occ)+":{" +self.__str__()+"}"+" =?= "+"{{"+','.join([str(t) for t in self.ts()])+"}}"

    def __eq__(self, other):
        return isinstance(other, __class__) and self.vc == other.vc  and self.idx == other.idx

    def __hash__(self):
        return hash((self.vc,self.idx))

    def __str__(self):
        c = self.vclass()
        i = self.id()
        return f"{c}"+f"{i}"

    def __repr__(self):
        return f"{self.vc}"+f"{self.idx}"

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
        return hash((self.func, self.args))

    def __repr__(self):
        args = ("" if not self.args
                else '(' + ','.join(str(a) for a in self.args) + ')')
        return f"{self.func.name}{args}"

class Rec(Term):
    class InvalidFunctionException(Exception):
        def __init__(self,idx):
            self.idx = idx
        def handle(self):
            print()
            print("Invalid Arugment: ",str(self.idx)+" has type "+type(self.idx)+", should have type Idx.")
            return None

    def __init__(self, func, idx):
        assert func.arity == 1
        self.func = func
        if not type(idx) is Idx: raise InvalidArgumentException(idx)
        self.idx = idx

    def __str__(self):
        return self.func.name+"_"+str(self.idx)

    def __eq__(self, other: "Rec"):
        return isinstance(other, __class__) and self.func == other.func and self.idx == other.idx

    def __hash__(self):
        return hash((self.func, self.idx))

    def __repr__(self):
        return self.func.name+"_"+str(self.idx)
