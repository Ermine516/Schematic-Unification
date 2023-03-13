from sys import argv
from LoopUnif import *
from Interpretation import *


if __name__ == "__main__":
    debug = True if len(argv)==2 and argv[1] == "debug" else False
    f_ = Func('f', 2)
    rrec= Func("R",1)
    Y = {i:Var('Y',i) for i in range(0,10)}
    mrec= Func("M",1)
    W = {i:Var('W',i) for i in range(0,10)}
    lrec= Func("L",1)
    X = {i:Var('X',i) for i in range(0,300)}
    Z = {i:Var('Z',i) for i in range(0,10)}
    Q = {i:Var('Q',i) for i in range(0,10)}

    I = Interpretation()

#Example 0 - Not entirely correct set, just not check termination of both chains
    # lterm = f_(lrec(Idx(0)),f_(X[0],X[0]))
    # rterm = f_(f_(Y[0],Y[0]),rrec(Idx(0)))

#Example 1
    # lterm = f_(f_(X[0],X[0]),lrec(Idx(0)))
    # rterm = f_(Y[0],Y[0])

#Example 2
    # sub =f_(f_(X[0],X[0]),f_(X[0],X[0]))
    # lterm = f_(f_(sub,sub),lrec(Idx(0)))
    # rterm = f_(Y[0],Y[0])

#Example 3
    # sub =f_(X[0],f_(X[15],f_(X[60],f_(X[0],f_(X[15],X[60])))))
    # lterm = f_(sub,lrec(Idx(0)))
    # rterm = f_(Y[0],f_(Y[1],f_(Y[2],f_(Y[0],f_(Y[1],Y[2])))))

#Example 4
    # sub =f_(X[1],f_(X[0],f_(X[1],f_(X[0],f_(X[1],X[0])))))
    # lterm  = f_(sub,lrec(Idx(0)))
    # rterm  = f_(Y[0],f_(Y[1],Y[0]))

#Example 5
    # sub =f_(X[0],f_(X[5],f_(X[50],f_(X[0],f_(X[5],X[50])))))
    # lterm = f_(sub,lrec(Idx(0)))
    # rterm =f_(Y[0],f_(Y[1],f_(Y[2],f_(Y[0],f_(Y[1],Y[2])))))

#Example 6
    # sub =f_(X[0],f_(X[5],f_(X[30],f_(X[0],f_(X[5],X[30])))))
    # lterm = f_(sub,lrec(Idx(0)))
    # rterm =f_(Y[0],f_(Y[1],f_(Y[2],f_(Y[0],f_(Y[1],Y[2])))))

#Example 7
    # sub =f_(X[0],f_(X[5],f_(X[40],f_(X[0],f_(X[5],X[40])))))
    # lterm = f_(sub,lrec(Idx(0)))
    # rterm =f_(Y[0],f_(Y[1],f_(Y[2],f_(Y[0],f_(Y[1],Y[2])))))

#Example 8
    # sub =f_(X[0],f_(X[5],f_(X[45],f_(X[0],f_(X[5],X[45])))))
    # lterm = f_(sub,lrec(Idx(0)))
    # rterm =f_(Y[0],f_(Y[1],f_(Y[2],f_(Y[0],f_(Y[1],Y[2])))))

#Example 9
    # sub =f_(X[0],f_(X[10],f_(X[95],f_(X[0],f_(X[10],X[95])))))
    # lterm = f_(sub,lrec(Idx(0)))
    # rterm =f_(Y[0],f_(Y[1],f_(Y[2],f_(Y[0],f_(Y[1],Y[2])))))

#Example 10
    # sub =f_(X[1],f_(Z[0],f_(X[1],f_(X[0],f_(Z[1],X[0])))))
    # lterm  = f_(sub,lrec(Idx(0)))
    # rterm  = f_(Y[0],f_(Y[1],Y[0]))

#Example 11
    # sub =f_(X[1],f_(Z[0],f_(X[1],f_(X[0],f_(Z[1],X[0])))))
    # lterm  = f_(sub,lrec(Idx(0)))
    # rterm  = f_(rrec(Idx(0)),f_(Y[1],f_(Y[2],f_(Y[0],f_(Y[1],Y[2])))))

#Example 12
    # sub =f_(X[1],f_(Z[1],f_(X[0],f_(X[0],f_(Z[0],X[1])))))
    # lterm  = f_(sub,lrec(Idx(0)))
    # rterm  = f_(rrec(Idx(0)),f_(Y[1],f_(Y[2],f_(Y[0],f_(Y[1],Y[2])))))
    #
    # I.add_mapping(lrec,lterm)
    # I.add_mapping(rrec,rterm)
    # lu = LoopUnif(I,debug)
    # lu.loop_unif()


#Example 12
    # lsub1 = f_(X[0],X[0])
    # lsub2 = f_(f_(Z[0],f_(Z[0],f_(Z[0],f_(Z[0],Z[0])))),lrec(Idx(0)))
    # lterm  = f_(lsub1,f_(lsub2,f_(Q[0],Q[0])))
    # rsub1 = f_(Y[0],f_(Y[0],f_(Y[0],f_(Y[0],Y[0]))))
    # rterm  = f_(mrec(Idx(0)), f_(rsub1,rrec(Idx(0))))
    # mterm  = f_(f_(W[0],W[0]),mrec(Idx(0)))
    # I.add_mapping(lrec,lterm)
    # I.add_mapping(rrec,rterm)
    # I.add_mapping(mrec,mterm)
    # lu = LoopUnif(I,debug,[lrec(Idx(0)),rrec(Idx(0))])
    # lu.loop_unif()

#Example 10 Many examples at once
# The issue present in this code concerns nesting
# not linear. Linear is still ok
# Linear nesting might work if we can figure out how to handle
# the unifier.
    # l=2
    # for (x1,x2,x3,x4,x5,x6) in [(y1,y2,y3,y4,y5,y6) for y1 in range(0,l) for y1 in range(0,l) for y2 in range(0,l) for y3 in range(0,l) for y4 in range(0,l) for y5 in range(0,l) for y6 in range(0,l)]:
    #     sub =f_(X[x1],f_(Z[x2],f_(X[x3],f_(X[x4],f_(f_(Z[x5],Z[x5]),X[x6])))))
    #     lterm  = f_(sub,lrec(Idx(0)))
    #     rterm  = f_(rrec(Idx(0)),f_(Y[1],f_(Y[2],f_(Y[0],f_(mrec(Idx(0)),Y[3])))))
    #     mterm  = f_(f_(W[0],W[0]),mrec(Idx(0)))
    #
    #     I.add_mapping(lrec,lterm)
    #     I.add_mapping(rrec,rterm)
    #     I.add_mapping(mrec,mterm)
    #     lu = LoopUnif(I,debug,[lrec(Idx(0)),rrec(Idx(0))])
    #     lu.loop_unif()
    #     for x in X.values(): x.reset()
    #     for y in Y.values(): y.reset()
    #     for z in Z.values(): z.reset()
    #     for w in W.values(): w.reset()
#Example 10 Many examples at once
    # l=3
    # for (x1,x2,x3,x4,x5,x6) in [(y1,y2,y3,y4,y5,y6) for y1 in range(0,l) for y1 in range(0,l) for y2 in range(0,l) for y3 in range(0,l) for y4 in range(0,l) for y5 in range(0,l) for y6 in range(0,l)]:
    #     sub =f_(X[x1],f_(X[x2],f_(X[x3],f_(X[x4],f_(X[x5],X[x6])))))
    #     lterm = f_(sub,lrec(Idx(0)))
    #     rterm = f_(Y[0],f_(Y[1],Y[0]))
    #     I.add_mapping(lrec,lterm)
    #     I.add_mapping(rrec,rterm)
    #     lu = LoopUnif(I,debug)
    #     lu.loop_unif()
    #     for x in X.values(): x.reset()
    #     for y in Y.values(): y.reset()

#Example 10 Many examples at once

    # for i in range(1,100):
    #         for j in range(1,100):
    #             sub =f_(X[0],f_(X[i],f_(X[j],f_(X[0],f_(X[i],X[j])))))
    #             lterm = f_(sub,lrec(Idx(0)))
    #             rterm = f_(Y[0],f_(Y[1],f_(Y[2],f_(Y[0],f_(Y[1],Y[2])))))
    #             lu = LoopUnif(lterm,l,r,debug)
    #             lu.loop_unif()
    #             I.add_mapping(lrec,lterm)
    #             I.add_mapping(rrec,rterm)
    #             lu = LoopUnif(I,debug)
    #             lu.loop_unif()
    #             for x in X.values(): x.reset()
    #             for y in Y.values(): y.reset()
