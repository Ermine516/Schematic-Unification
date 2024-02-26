from __future__ import annotations
from typing import Any, Tuple
from functools import reduce
from Substitutable import *
from Substitution import Substitution
from TermAttr import TermAttr
from Normalizable import Normalizable
from abc import ABC

class Func:
    name: str
    arity: int

    def __init__(self, name:str, arity:int):
        self.name = name
        self.arity = arity

#Magic Methods
      
    def __eq__(self, other:Func)-> bool:
        return isinstance(other, __class__) and self.name == other.name and self.arity == other.arity

    def __hash__(self):
        return hash((self.name, self.arity))

    def __repr__(self):
        return f"{self.name}/{self.arity}"

    def __call__(self, *args):
        if len(args) != self.arity: raise ValueError()
        else: return App(self, *args)

class Term(ABC):
    pass

class App(Term,TermAttr,Substitutable,Normalizable):
    func: Func
    args: Tuple[Term]

    def __init__(self, func:Func,*args:Tuple[Term]):
        assert func.arity == len(args)
        self.func = func
        self.args = tuple(args)
        self.anchor = None

#Magic Methods

    def __str__(self) -> str:
        argsstr = "("+','.join([str(x) for x in self.args])+")" if len(self.args)>0 else ""
        return self.func.name+argsstr
    
    def __eq__(self, other: App) -> bool:
        return isinstance(other, __class__) and self.func == other.func and self.args == other.args

    def __hash__(self):
        return hash((self.func, self.args))


    def __repr__(self) -> str:
        return f"{self.func.name}{ ("" if not self.args else '(' + ','.join(repr(a) for a in self.args) + ')')}"

# Abstract Methods

    # From Substitutable 
    def handleSubstitution(self, sigma:Substitution)-> Term:
        return self.applyFunc(sigma)
    
    # From Normalizable 
    def normalize(self) -> Term:
        if isinstance(self,App)  and self.anchor: return self.anchor.instance()
        else: return self.func(*map(lambda x: x.normalize(),self.args))
    
    # From TermAttr
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

    def recsOcc(self) -> set[Var]:
        ret = []
        for t in self.args:
            ret.extend(t.recsOcc())
        return ret

    def maxIdx(self) -> int:
        return  (max((x.maxIdx() for x in self.args))if len( self.args)>0 else 0)
    
    def minIdx(self) -> int:
        return  (max((x.minIdx() for x in self.args))if len( self.args)>0 else 0)

    #checks if t occurs in self
    def occurs(self,t: Term) -> bool:
        if self == t: return True
        else: return reduce(lambda a,b: a or b.occurs(t),self.args,False)
    
    def depth(self)-> int:
        return 1+ (max((x.depth() for x in self.args)) if len( self.args)>0 else 0)

    def instance(self)-> App:
        ret= self.func(*map(lambda x: x.instance(),self.args))
        if self.anchor: ret.anchor=self.anchor
        return ret 
    
    def applyFunc(self,f:function) -> App:            
        ret = self.func(*map(lambda x: x.applyFunc(f),self.args))
        if self.anchor: ret.anchor=self.anchor
        return ret


# Class Specific Methods

    def strAlt(self,tag:str)-> str:
        argsstr = "("+','.join([ x.strAlt(tag) for x in self.args])+")" if len(self.args)>0 else ""
        return self.func.name+argsstr

class VarObjects(Term,Domainable,TermAttr,Substitutable,Normalizable,ABC):
    vc: str
    idx: int

    @abstractmethod
    def __init__(self,vc: str,idx: int):
        if not type(idx) is int: raise TypeError()
        self.vc = vc
        self.idx = idx

#Magic Methods
  
    def __eq__(self, other:Var) -> bool:
        return isinstance(other, __class__) and self.vc == other.vc  and self.idx == other.idx

    def __hash__(self):
        return hash((self.vc,self.idx))    
    
# Abstract Methods 

    # From Substitutable 
    def handleSubstitution(self,sigma:Substitution)-> Term:
        if self in sigma.domain(): return sigma.mapping[self].instance()
        else: return self.instance()

    # From Normalizable 
    def normalize(self) -> Var: return self.instance()

    # From TermAttr 

    def maxIdx(self) -> int: return self.idx
 
    def minIdx(self) -> int: return self.idx

    def occurs(self,t:Var)-> bool: return self==t

    def depth(self)-> int: return 1

    def applyFunc(self,f:function)-> Any: return f(self.instance()) 


class Var(VarObjects):

    def __init__(self, vc: str, idx: int):
        super().__init__(vc, idx)

    def __str__(self) -> str:
        return f"{self.vc}"+f"[{self.idx}]"

    def __repr__(self) -> str:
        return f"{self.vc.lower()}_{self.idx}"  

# Abstract Methods 

    # From TermAttr
    def recs(self) -> set[Var]: return set()
    
    def vars(self) -> set[Var]: return set([self])
    
    def varsOcc(self) -> list[Var]: return [self]
    
    def recsOcc(self) -> list[Rec]: return []
    
    def instance(self)-> Var: return Var(self.vc,self.idx)

# Class Specific Methods 

    def strAlt(self,tag:str)-> str:
        return f"{self.vc}"+f"[{ tag if self.idx== 0 else tag+"+"+str(self.idx)}]"

class Rec(VarObjects):


    def __init__(self, vc: str, idx: int):
        super().__init__(vc, idx)
#Magic Methods

    def __str__(self) -> str:
        return self.vc+"_"+str(self.idx)


    def __repr__(self)->str:
        return self.vc.lower()+"_"+"r"+"_"+str(self.idx)

# Abstract Methods
        
    def recs(self) -> set[Rec]: return set([self])

    def vars(self) -> set[Var]: return set()

    def varsOcc(self) -> set[Var]: return []

    def recsOcc(self) -> set[Rec]: return [self]

    def instance(self) -> Rec: return Rec(self.vc,self.idx)
    
#Class Specific Methods

    def strAlt(self,tag:str)->str:
        return self.vc+"_"+("{"+tag+"+"+str(self.idx)+"}")