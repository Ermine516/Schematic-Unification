from sys import argv
from LoopUnif import *



if __name__ == "__main__":
    debug = True if len(argv)==2 and argv[1] == "debug" else False
    f_ = Func('f', 2)
    rvar = {i:Var('y',i) for i in range(0,10)}
    recsym = Func("L",1,True)
    recsym.add_class("X",1)
    I = {i:Idx(i) for i in range(0,300)}
    # sub =f_(I[0],I[0])
    # lterm = recterm(f_(sub,recsym(I[0])))
    # l,r = recsym(I[0]),f_(rvar[0],rvar[0])

    # sub =f_(f_(I[0],I[0]),f_(I[0],I[0]))
    # lterm = recterm(f_(f_(sub,sub),recsym(I[0])))
    # l,r = recsym(I[0]),f_(rvar[0],rvar[0])

    # sub =f_(I[0],f_(I[15],f_(I[15],f_(I[0],f_(I[15],I[15])))))
    # lterm = recterm(f_(sub,recsym(I[0])))
    # l,r = recsym(I[0]),f_(rvar[0],f_(rvar[1],f_(rvar[2],f_(rvar[0],f_(rvar[1],rvar[2])))))

    # sub =f_(I[0],f_(I[15],f_(I[60],f_(I[0],f_(I[15],I[60])))))
    # lterm = recterm(f_(sub,recsym(I[0])))
    # l,r = recsym(I[0]),f_(rvar[0],f_(rvar[1],f_(rvar[2],f_(rvar[0],f_(rvar[1],rvar[2])))))
    l=3
    for (x1,x2,x3,x4,x5,x6) in [(y1,y2,y3,y4,y5,y6) for y1 in range(0,l) for y1 in range(0,l) for y2 in range(0,l) for y3 in range(0,l) for y4 in range(0,l) for y5 in range(0,l) for y6 in range(0,l)]:
        sub =f_(I[x1],f_(I[x2],f_(I[x3],f_(I[x4],f_(I[x5],I[x6])))))
        lterm = recterm(f_(sub,recsym(I[0])))
        l,r = recsym(I[0]),f_(rvar[0],f_(rvar[1],rvar[0]))

    # sub =f_(I[0],f_(I[1],f_(I[0],f_(I[0],f_(I[1],I[0])))))
    # lterm = recterm(f_(sub,recsym(I[0])))
    # l,r = recsym(I[0]),f_(rvar[0],f_(rvar[1],f_(rvar[2],f_(rvar[3],f_(rvar[4],rvar[1])))))

    # sub =f_(I[0],f_(I[1],f_(I[0],f_(I[0],f_(I[1],I[0])))))
    # lterm = recterm(f_(sub,recsym(I[0])))
    # l,r = recsym(I[0]),f_(rvar[0],f_(rvar[1],f_(rvar[4],f_(rvar[3],f_(rvar[4],rvar[1])))))

    # sub =f_(I[0],f_(I[1],f_(I[0],f_(I[0],f_(I[1],I[0])))))
    # lterm = recterm(f_(sub,recsym(I[0])))
    # l,r = recsym(I[0]),f_(rvar[0],f_(rvar[1],f_(rvar[4],f_(rvar[0],f_(rvar[4],rvar[1])))))

    # sub =f_(I[0],f_(I[5],f_(I[50],f_(I[0],f_(I[5],I[50])))))
    # lterm = recterm(f_(sub,recsym(I[0])))
    # l,r = recsym(I[0]),f_(rvar[0],f_(rvar[1],f_(rvar[2],f_(rvar[0],f_(rvar[1],rvar[2])))))

    # sub =f_(I[0],f_(I[5],f_(I[30],f_(I[0],f_(I[5],I[30])))))
    # lterm = recterm(f_(sub,recsym(I[0])))
    # l,r = recsym(I[0]),f_(rvar[0],f_(rvar[1],f_(rvar[2],f_(rvar[0],f_(rvar[1],rvar[2])))))
    #
    # sub =f_(I[0],f_(I[5],f_(I[40],f_(I[0],f_(I[5],I[40])))))
    # lterm = recterm(f_(sub,recsym(I[0])))
    # l,r = recsym(I[0]),f_(rvar[0],f_(rvar[1],f_(rvar[2],f_(rvar[0],f_(rvar[1],rvar[2])))))
    #
    # sub =f_(I[0],f_(I[5],f_(I[45],f_(I[0],f_(I[5],I[45])))))
    # lterm = recterm(f_(sub,recsym(I[0])))
    # l,r = recsym(I[0]),f_(rvar[0],f_(rvar[1],f_(rvar[2],f_(rvar[0],f_(rvar[1],rvar[2])))))

    # sub =f_(I[0],f_(I[10],f_(I[95],f_(I[0],f_(I[10],I[95])))))
    # lterm = recterm(f_(sub,recsym(I[0])))
    # l,r = recsym(I[0]),f_(rvar[0],f_(rvar[1],f_(rvar[2],f_(rvar[0],f_(rvar[1],rvar[2])))))

        lu = LoopUnif(lterm,l,r,debug)
        lu.loop_unif()
    # for i in range(15,100):
    #     sub =f_(I[0],f_(I[15],f_(I[i],f_(I[0],f_(I[15],I[i])))))
    #     lterm = recterm(f_(sub,recsym(I[0])))
    #     l,r = recsym(I[0]),f_(rvar[0],f_(rvar[1],f_(rvar[2],f_(rvar[0],f_(rvar[1],rvar[2])))))
    # lu = LoopUnif(lterm,l,r,debug)
    # lu.loop_unif()
