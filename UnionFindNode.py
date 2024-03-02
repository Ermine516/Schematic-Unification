# Implements Union-find algorithm 
from __future__ import annotations
from Term import Term


class UnionFindNode:
    val: Term
    rep: UnionFindNode    
    size: int
    terms: list[Term]
    occ: int

    def __init__(self,val:Term):
        self.val = val
        self.rep = self
        self.size =1
        self.terms = []
        self.occ = 0
    
#Magic Methods
    
    def __eq__(self, other:UnionFindNode) -> bool:
        return isinstance(other, __class__) and self.val == other.val

    def __hash__(self) -> int:
        return hash((self.val))
    
    def __str__(self) -> str:
        return str(self.find().val)

# Class Specific Methods 
    
    def union(self:UnionFindNode,y:UnionFindNode) -> UnionFindNode:
        self,y=self.find(),y.find()
        if self==y: return self
        if self.size < y.size: self,y = y,self
        # Updates the size and number of occurances
        self.size, self.occ = self.size+y.size,self.occ+y.occ
        # moves the right side of the multiequation to the representative
        self.terms.extend(y.terms)
        # Resets the non-rep
        y.rep,y.terms, y.occ = self,[],0
        return self
    
    def find(self:UnionFindNode) -> UnionFindNode:
        while self.rep != self: self,self.rep = self.rep,self.rep.rep
        return self
    
    def setocc(self:UnionFindNode,i:int)-> None:
        self.find().occ = self.find().occ+i
    
    def occs(self:UnionFindNode)-> int:
        return self.find().occ
    
    def ts(self:UnionFindNode)-> list[Term]:
        return self.find().terms
    
    def format(self:UnionFindNode)-> str:
        return str(self.find().occ)+":{" +self.__str__()+"}"+" =?= "+"{{"+','.join([str(t) for t in self.ts()])+"}}"