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
    def inducAppRebuild(self,f):
        if isinstance(self,App):
            return self.func(*map(lambda x: x.inducAppRebuild(f),self.args))
        else:
            return f(self)
    def inducApp(self,f):
        if isinstance(self,App):
            ret =[]
            for x in self.args: ret.append(f(x))
            return ret
        else:
            return f(self)
    def occurs(self,t):
        if self == t:
            return True
        elif type(t) is App:
            return reduce(lambda a,b: a or self.occurs(b),t.args,False)
        else:
            False
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

    def reset(self):
        self.rep = self
        self.size =1
        self.terms = []
        self.occ = 0

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


    def __init__(self, vc,idx,active = False):
        self.vc = vc
        self.idx = idx
        # for union-find
        self.rep = self
        self.size =1
        self.terms = []
        self.occ = 0

#We need to remember the largest subordinate class.

    def format(self):
        return str(Var.find(self).occ)+":{" +self.__str__()+"}"+" =?= "+"{{"+','.join([str(t) for t in self.ts()])+"}}"

    def __eq__(self, other):
        return isinstance(other, __class__) and self.vc == other.vc  and self.idx == other.idx

    def __hash__(self):
        return hash((self.vc,self.idx))

    def __str__(self):
        c = self.vclass()
        i = self.id()
        return f"{c}"+f"[{i}]"


    def strAlt(self,tag):
        c = self.vclass()
        i= str(self.id())
        i = tag if i=="0" else tag+"+"+i
        return f"{c}"+f"[{i}]"
    def __repr__(self):
        return f"{self.vc.lower()}_{self.idx}"

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
    def strAlt(self,tag):
        argsstr = "("+','.join([ x.strAlt(tag) for x in self.args])+")" if len(self.args)>0 else ""
        return self.func.name+argsstr
    def __eq__(self, other: "App"):
        return isinstance(other, __class__) and self.func == other.func and self.args == other.args

    def __hash__(self):
        return hash((self.func, self.args))


    def __repr__(self):
        args = ("" if not self.args
                else '(' + ','.join(repr(a) for a in self.args) + ')')
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


    def strAlt(self,tag):
        i=str(self.idx)
        return self.func.name+"_"+( tag if  i== "0" else "{"+tag+"+"+str(self.idx)+"}")

    def __eq__(self, other: "Rec"):
        return isinstance(other, __class__) and self.func == other.func and self.idx == other.idx

    def __hash__(self):
        return hash((self.func, self.idx))

    def __repr__(self):
        return self.func.name.lower()+"_"+"r"+"_"+str(self.idx)
