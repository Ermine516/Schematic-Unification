from SchematicUnification import *
from SchematicSubstitution import *
from functools import reduce
from TermParser import *
from os import listdir
import time


class Test:
    def test():
        onlyfiles = [f for f in listdir("Examples/tests") if "test" in f]
        onlyfiles.sort(key= lambda a: int(a.split(".")[0][4:]) )
        isunif = {1:"unifiable",2:"unifiable",3:"unifiable",4:"not unifiable",5:"not unifiable",6:"not unifiable", \
        7:"unifiable",8:"unifiable",9:"not unifiable",10:"not unifiable",11:"unifiable",12:"unifiable",\
        13:"not unifiable",14:"unifiable",15:"unifiable",16:"unifiable",17:"unifiable",18:"not unifiable", \
        19:"unifiable"}
        for i in range(1,len(onlyfiles)+1):
            print("Test "+str(i)+ " (should be "+isunif[i]+")")
            tp =TermParser()
            I = SchematicSubstitution()
            with open("Examples/tests/"+onlyfiles[i-1]) as f:
                unif, mappings= tp.parse_input(f.readlines())
                for m in mappings:I.add_mapping(*m)
                su = SchematicUnification(I,0,unif)
                su.unif(time.time())


    def testExampleSize(file,i,debug):
        def build(I,t,i):
            if i == 0: return t
            else:
                if type(t) is Var:
                    return t
                elif type(t) is App:
                    return t.func(*reduce(lambda a,b: a+[build(I,b,i)],t.args,[]))
                elif type(t) is Rec:
                    return build(I,I.increment(t.func.name,t.idx),i-1)
        tp =TermParser()
        I = Interpretation()
        with open(file) as f:
            unif, mappings= tp.parse_input(f.readlines())
            for m in mappings:I.add_mapping(*m)
            unif = [build(I,t,i) for t in unif]
            I.add_relevent_vars(unif)
            lu = LoopUnif(I,debug,unif)
            lu.loop_unif()

    def test2():
        f_ = Func('f', 2)
        rrec= Func("R",1)
        Y = {i:Var('Y',i) for i in range(0,100)}
        lrec= Func("L",1)
        X = {i:Var('X',i) for i in range(0,100)}
        Z = {i:Var('Z',i) for i in range(0,100)}
    # Very Important example!!
        sub =f_(X[1],f_(X[0],f_(X[1],f_(X[0],f_(X[1],X[0])))))
        lterm  = f_(sub,lrec(Idx(0)))
        rterm  = f_(Y[0],f_(Y[1],Y[0]))
        I = Interpretation()
        I.add_mapping(lrec,lterm)
        I.add_mapping(rrec,rterm)
        term = build(I,I.increment("L",Idx(0)),0)
        lu = LoopUnif(I,3,[term,rrec(Idx(0))])
        lu.loop_unif()
