from functools import reduce

class Unifier:
    def __init__(self):
        self.global_unifier = {}
        self.local_unifiers = {}

# TODO if we are going to handle nested terms the unifier cannot just erase
#Same holds for non-linear variable class usage
    def extend(self,idx,unif):
        self.local_unifiers[idx] = {}
        for x,y in unif:
            if not x.vc in self.global_unifier.keys():
                self.global_unifier[x.vc] = {}
            if not x.vc in self.local_unifiers[idx].keys():
                self.local_unifiers[idx][x.vc] = {}
            self.global_unifier[x.vc][x.idx]=(x,y)
            self.local_unifiers[idx][x.vc][x.idx]=(x,y)

    def binding(self,v,i):
        try:
            return self.global_unifier[v][i]
        except Exception:
            return None
    def local_binding(self,idx,v,i):
        try:
            return self.local_unifiers[idx][v][i]
        except Exception:
            return None
    def bindings(self,subdom=[],bound=0):
        return map(lambda a: self.binding(a[0],a[1]),[x for x in self.domain(subdom) if x[1]>=bound])
    def local_bindings(self,idx,subdom=[],bound=0):
        return map(lambda a: self.local_binding(idx,a[0],a[1]),[x for x in self.local_domain(idx,subdom) if x[1]>=bound])
    def local_domain(self,idx,subdom=[]):
        tosearch = self.local_unifiers[idx].keys() if subdom ==[] else set(subdom).intersection(self.local_unifiers[idx].keys())
        cprod =  lambda b: list(map(lambda c: (b,c),self.local_unifiers[idx][b].keys()))
        return reduce(lambda a,b: a+cprod(b),tosearch,[])
    def domain(self,subdom=[]):
        tosearch = self.global_unifier.keys() if subdom ==[] else set(subdom).intersection(self.global_unifier.keys())
        cprod =  lambda b: list(map(lambda c: (b,c),self.global_unifier[b].keys()))
        return reduce(lambda a,b: a+cprod(b),tosearch,[])