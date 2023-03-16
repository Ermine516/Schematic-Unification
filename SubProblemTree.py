from Term import *
class SubProblemNode:
    def __init__(self,subproblem,idx,parent=None,children=[]):
        self.subproblem = subproblem
        self.parent = parent
        self.children = children
        self.idx = idx
        self.cyclic = None
        self.cyclicIdx =-1
    def addchild(self,child):
        self.children.append(child)

class SubProblemTree:


    def __init__(self,prob):
        self.counter = 1
        self.openbranches= [SubProblemNode(prob,0)]
        self.closedbranches=[]
        self.cur= None

    def current(self):
        return self.cur

    def getOpenBranch(self):
        if len(self.openbranches) == 0: return None
        self.cur = self.openbranches.pop()
        if self.closeBranch(): return self.getOpenBranch()
        else: return self.cur

    def addBranch(self,prob):
        nb = SubProblemNode(prob,self.counter,self.cur)
        self.cur.addchild(nb)
        self.openbranches.append(nb)
        self.counter+=1

#TODO Needs backtrackng to be fully correct
    def closeBranch(self):
        def consistent(fa,pa):
            return  reduce(lambda a,b: a and (fa[b]==pa[b] if b in pa.keys() else True),fa.keys(),True)
        test = list(self.cur.subproblem)
        previousprob = self.cur.parent
        closed = iter(self.closedbranches)
        while previousprob:
            check = list(previousprob.subproblem)
            if len(test) == len(check):
                result =[]
                leftalpha = {}
                rightalpha = {}
                for vt,t in test:
                    found = None
                    curmap = leftalpha[vt] if vt in leftalpha.keys() else None
                    if not curmap and vt in rightalpha.keys():
                        curmap =  rightalpha[vt]
                        leftalpha[vt] = curmap
                    checkfiltered = filter(lambda a: a[0]==curmap,check) if curmap else check
                    for vs,s in checkfiltered:
                        partalpha = t.isalpha(s)
                        if partalpha != None and consistent(rightalpha,partalpha):
                            found = (vs,s)
                            for x in partalpha.keys():
                                rightalpha[x] = partalpha[x]
                            break
                    if found:
                        result.append(((vt,t),found))
                        check.remove(found)
                    else: break
                if check ==[]:
                    self.cur.cyclic = result
                    self.cur.cyclicIdx = previousprob.idx
                    self.closedbranches.append(self.cur)
                    return True
            previousprob = previousprob.parent if  previousprob.parent else next(closed,None)

        return False
    def print_closures(self):
        for cycle in self.closedbranches:
            print("Recursion Found "+str(cycle.idx)+" => "+str(cycle.cyclicIdx)+" :\n\t"+'\n\t'.join([str(x)+" => "+str(y) for x,y in cycle.cyclic]))
            print()
