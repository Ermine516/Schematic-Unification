from __future__ import annotations
from typing import Set, Tuple, Dict
from collections import defaultdict
from functools import reduce

class Func:
    """Immutable data type representing a function symbol."""
    name: str
    arity: int
    anchor: Term # using for normalization
    def __init__(self, name:str, arity:int):
        self.name = name
        self.arity = arity
        
    def __eq__(self, other)-> bool:
        return isinstance(other, __class__) and self.name == other.name and self.arity == other.arity

    def __hash__(self):
        return hash((self.name, self.arity))

    def __repr__(self):
        return f"{self.name}/{self.arity}"

    def __call__(self, *args):
        if len(args) != self.arity: raise ValueError()
        if len(args) == 1 and type(args[0]) is Idx: return Rec(self, *args)
        else: return App(self, *args)
    def instance(self):
        return Func(self.name,self.arity)
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
    
    def depth(self):
        if isinstance(self,App):
            return 1+ (max((x.depth() for x in self.args)) if len( self.args)>0 else 0)
        else:
            return 1 
    def maxIdx(self):
        if isinstance(self,App):
            return  (max((x.maxIdx() for x in self.args))if len( self.args)>0 else 0)
        elif isinstance(self,Var):
            return self.idx
        elif isinstance(self,Rec):
            return self.idx.number

    def occurs(self,t):
        if self == t:
            return True
        elif type(t) is App:
            return reduce(lambda a,b: a or self.occurs(b),t.args,False)
        else:
            False
    def normalizedInstance(self):
        if isinstance(self,App)  and self.anchor:
            return self.anchor.instance()
        elif isinstance(self,Var) or isinstance(self,Rec):
            return self.instance()
        elif isinstance(self,App):
            return self.func.instance()(*map(lambda x: x.normalizedInstance(),self.args))



    pass

class Var(Term):
    """Immutable named variable that is unifiable with any other term."""
    vc: str
    idx: int
    def __init__(self,vc,idx):
        self.vc = vc
        self.idx = idx
    
    def __eq__(self, other):
        return isinstance(other, __class__) and self.vc == other.vc  and self.idx == other.idx

    def __hash__(self):
        return hash((self.vc,self.idx))

    def __str__(self):
        return f"{self.vc}"+f"[{self.idx}]"

    def __repr__(self):
        return f"{self.vc.lower()}_{self.idx}"  

    def strAlt(self,tag):
        i= str(self.idx)
        i = tag if i=="0" else tag+"+"+i
        return f"{self.vc}"+f"[{i}]"

    def recs(self): return set()
    
    def vars(self): return set([self])
    
    def varsOcc(self): return [self]
    
    def instance(self): return Var(self.vc,self.idx)

class App(Term):
    """Immutable fully-applied function term."""
    func: Func
    args: Tuple[Term]
    def __init__(self, func,*args):
        assert func.arity == len(args)
        self.func = func
        self.args = tuple(args)
        self.anchor = None

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

    def instance(self)-> App:
        ret= self.func.instance()(*map(lambda x: x.instance(),self.args))
        if self.anchor: ret.anchor=self.anchor
        return ret 
    def recs(self)-> set[Rec]:
        ret=set()
        for t in self.args:
            ret.update(t.recs())
        return ret
    
    def vars(self) -> set[Var]:
        ret = set()
        for t in self.args:
            ret.update(t.vars())
        return ret
    def varsOcc(self) -> set[Var]:
        ret = []
        for t in self.args:
            ret.extend(t.varsOcc())
        return ret
    def applyFunc(self,f):            
            ret = self.func(*map(lambda x: f(x),self.args))
            if self.anchor: ret.anchor=self.anchor
            return ret
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

class Rec(Term):
    name: str
    func: Func
    arity: int
    idx: Idx
    class InvalidFunctionException(Exception):
        def __init__(self,idx):
            self.idx = idx
        def handle(self):
            print()
            print("Invalid Arugment: ",str(self.idx)+" has type "+type(self.idx)+", should have type Idx.")
            return None

    def __init__(self, func:Func, idx:Idx):
        if not type(idx) is Idx: raise InvalidArgumentException(idx)
        assert func.arity == 1
        self.func = func
        self.name = func.name
        self.idx = idx

    def __str__(self):
        return self.func.name+"_"+str(self.idx)


    def strAlt(self,tag:str)->str:
        return self.func.name+"_"+("{"+tag+"+"+str(self.idx)+"}")

    def __eq__(self, other: "Rec"):
        return isinstance(other, __class__) and self.func == other.func and self.idx == other.idx

    def __hash__(self):
        return hash((self.func, self.idx))

    def __repr__(self)->str:
        return self.func.name.lower()+"_"+"r"+"_"+str(self.idx)

    def instance(self)-> Rec:
        return Rec(self.func.instance(),Idx(self.idx.number))

    def recs(self)-> set[Rec]:
        return set([self])

    def vars(self)-> set[Var]:
        return set()

    def varsOcc(self)-> set[Var]:
        return []
    