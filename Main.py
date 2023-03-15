from sys import argv
from LoopUnif import *
from Interpretation import *
from functools import reduce
def build(I,t,i):
    if i == 0: return t
    else:
        if type(t) is Var:
            return t
        elif type(t) is App:
            return t.func(*reduce(lambda a,b: a+[build(I,b,i)],t.args,[]))
        elif type(t) is Rec:
            return build(I,I.increment(t.func.name,t.idx),i-1)
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


def test1():
    f_ = Func('f', 2)
    rrec= Func("R",1)
    Y = {i:Var('Y',i) for i in range(0,100)}
    mrec= Func("M",1)
    W = {i:Var('W',i) for i in range(0,100)}
    lrec= Func("L",1)
    X = {i:Var('X',i) for i in range(0,100)}
    Z = {i:Var('Z',i) for i in range(0,100)}
    Q = {i:Var('Q',i) for i in range(0,100)}
    I = Interpretation()
    debug =0
    #Example 0
    print("Test 1 (should be unifiable)")
    lterm = f_(lrec(Idx(0)),f_(X[0],X[0]))
    rterm = f_(f_(Y[0],Y[0]),rrec(Idx(0)))
    I.add_mapping(lrec,lterm)
    I.add_mapping(rrec,rterm)
    lu = LoopUnif(I,debug)
    lu.loop_unif()
    I.reset()
    for x in X.values(): x.reset()
    for y in Y.values(): y.reset()


    #Example 1
    print("Test 2 (should be unifiable)")
    lterm = f_(f_(X[0],X[0]),lrec(Idx(0)))
    rterm = f_(Y[0],Y[0])
    I.add_mapping(lrec,lterm)
    I.add_mapping(rrec,rterm)
    lu = LoopUnif(I,debug)
    lu.loop_unif()
    I.reset()
    for x in X.values(): x.reset()
    for y in Y.values(): y.reset()

    #Example 2
    print("Test 3 (should be unifiable)")
    sub =f_(f_(X[0],X[0]),f_(X[0],X[0]))
    lterm = f_(f_(sub,sub),lrec(Idx(0)))
    rterm = f_(Y[0],Y[0])
    I.add_mapping(lrec,lterm)
    I.add_mapping(rrec,rterm)
    lu = LoopUnif(I,debug)
    lu.loop_unif()
    I.reset()
    for x in X.values(): x.reset()
    for y in Y.values(): y.reset()

    print("Test 5 (should be not unifiable)")
    sub =f_(X[1],f_(X[0],f_(X[1],f_(X[0],f_(X[1],X[0])))))
    lterm  = f_(sub,lrec(Idx(0)))
    rterm  = f_(Y[0],f_(Y[1],Y[0]))
    I.add_mapping(lrec,lterm)
    I.add_mapping(rrec,rterm)
    lu = LoopUnif(I,debug)
    lu.loop_unif()
    I.reset()
    for x in X.values(): x.reset()
    for y in Y.values(): y.reset()


    print("Test 6 (should be not unifiable)")
    sub =f_(X[0],f_(X[5],f_(X[30],f_(X[0],f_(X[5],X[30])))))
    lterm = f_(sub,lrec(Idx(0)))
    rterm =f_(Y[0],f_(Y[1],f_(Y[2],f_(Y[0],f_(Y[1],Y[2])))))
    I.add_mapping(lrec,lterm)
    I.add_mapping(rrec,rterm)
    lu = LoopUnif(I,debug)
    lu.loop_unif()
    I.reset()
    for x in X.values(): x.reset()
    for y in Y.values(): y.reset()


    print("Test 7 (should be not unifiable)")
    sub =f_(X[0],f_(X[10],f_(X[95],f_(X[0],f_(X[10],X[95])))))
    lterm = f_(sub,lrec(Idx(0)))
    rterm =f_(Y[0],f_(Y[1],f_(Y[2],f_(Y[0],f_(Y[1],Y[2])))))
    I.add_mapping(lrec,lterm)
    I.add_mapping(rrec,rterm)
    lu = LoopUnif(I,debug)
    lu.loop_unif()
    I.reset()
    for x in X.values(): x.reset()
    for y in Y.values(): y.reset()

    print("Test 8 (should be unifiable)")
    sub =f_(X[1],f_(Z[0],f_(X[1],f_(X[0],f_(Z[1],X[0])))))
    lterm  = f_(sub,lrec(Idx(0)))
    rterm  = f_(Y[0],f_(Y[1],Y[0]))
    I.add_mapping(lrec,lterm)
    I.add_mapping(rrec,rterm)
    lu = LoopUnif(I,debug)
    lu.loop_unif()
    I.reset()
    for x in X.values(): x.reset()
    for y in Y.values(): y.reset()
    for z in Z.values(): z.reset()

    print("Test 9 (should be unifiable)")
    sub =f_(X[1],f_(Z[1],f_(X[0],f_(X[0],f_(Z[0],X[1])))))
    lterm  = f_(sub,lrec(Idx(0)))
    rterm  = f_(rrec(Idx(0)),f_(Y[1],f_(Y[2],f_(Y[0],f_(Y[1],Y[2])))))
    I.add_mapping(lrec,lterm)
    I.add_mapping(rrec,rterm)
    lu = LoopUnif(I,debug)
    lu.loop_unif()
    I.reset()
    for x in X.values(): x.reset()
    for y in Y.values(): y.reset()
    for z in Z.values(): z.reset()

    print("Test 10 (should be not unifiable)")
    sub =f_(X[0],f_(X[11],f_(X[6],f_(X[0],f_(X[11],X[6])))))
    lterm = f_(sub,lrec(Idx(0)))
    rterm =f_(Y[0],f_(Y[1],f_(Y[2],f_(Y[0],f_(Y[3],Y[2])))))
    I.add_mapping(lrec,lterm)
    I.add_mapping(rrec,rterm)
    lu = LoopUnif(I,debug)
    lu.loop_unif()
    I.reset()
    for x in X.values(): x.reset()
    for y in Y.values(): y.reset()

    print("Test 11 (should be not unifiable)")
    sub =f_(X[0],f_(X[0],f_(X[0],f_(X[0],f_(X[1],X[1])))))
    lterm = f_(sub,lrec(Idx(0)))
    rterm = f_(f_(Y[2],Y[0]),f_(Y[1],Y[0]))
    I.add_mapping(lrec,lterm)
    I.add_mapping(rrec,rterm)
    lu = LoopUnif(I,debug)
    lu.loop_unif()
    I.reset()
    for x in X.values(): x.reset()
    for y in Y.values(): y.reset()

    print("Test 12 (should be unifiable)")
    sub =f_(X[1],f_(X[1],f_(X[1],f_(X[1],f_(X[1],X[1])))))
    lterm = f_(sub,lrec(Idx(0)))
    rterm = f_(f_(Y[2],Y[0]),f_(Y[1],Y[0]))
    I.add_mapping(lrec,lterm)
    I.add_mapping(rrec,rterm)
    lu = LoopUnif(I,debug)
    lu.loop_unif()
    I.reset()
    for x in X.values(): x.reset()
    for y in Y.values(): y.reset()



def test3():
    f_ = Func('f', 2)
    rrec= Func("R",1)
    Y = {i:Var('Y',i) for i in range(0,100)}
    lrec= Func("L",1)
    X = {i:Var('X',i) for i in range(0,100)}
    I = Interpretation()
    for i in range(5,50):
            for j in range(1,100):
                sub =f_(X[0],f_(X[i],f_(X[j],f_(X[0],f_(X[i],X[j])))))
                lterm = f_(sub,lrec(Idx(0)))
                rterm = f_(Y[0],f_(Y[1],f_(Y[2],f_(Y[0],f_(Y[3],Y[2])))))
                I.add_mapping(lrec,lterm)
                I.add_mapping(rrec,rterm)
                lu = LoopUnif(I,2)
                lu.loop_unif()
                for x in X.values(): x.reset()
                for y in Y.values(): y.reset()
def test4():
    f_ = Func('f', 2)
    rrec= Func("R",1)
    Y = {i:Var('Y',i) for i in range(0,100)}
    lrec= Func("L",1)
    X = {i:Var('X',i) for i in range(0,100)}
    Z = {i:Var('Z',i) for i in range(0,100)}
    I = Interpretation()
    l=3
    for (x1,x2,x3,x4,x5,x6) in [(y1,y2,y3,y4,y5,y6) for y1 in range(0,l) for y1 in range(0,l) for y2 in range(0,l) for y3 in range(0,l) for y4 in range(0,l) for y5 in range(0,l) for y6 in range(0,l)]:
        sub =f_(X[x1],f_(X[x2],f_(X[x3],f_(X[x4],f_(X[x5],X[x6])))))
        lterm = f_(sub,lrec(Idx(0)))
        rterm = f_(f_(Y[2],Y[0]),f_(Y[1],Y[0]))
        I.add_mapping(lrec,lterm)
        I.add_mapping(rrec,rterm)
        lu = LoopUnif(I,2)
        lu.loop_unif()
        for x in X.values(): x.reset()
        for y in Y.values(): y.reset()


if __name__ == "__main__":
    debug = True if len(argv)==2 and argv[1] == "debug" else False
    test1()
