from sys import argv
from LoopUnif import *
from Interpretation import *
from functools import reduce
from TermParser import *
from os import listdir
from Test import *



if __name__ == "__main__":
    assert(len(argv)>=2)
    if argv[1] =="Test":
        Test.test()
    if argv[1] =="Build":
        debug = int(argv[5]) if len(argv)==6 and argv[4] == "debug" else 0
        Test.testExampleSize(argv[2],int(argv[3]),debug)
    else:
        debug = int(argv[3]) if len(argv)==4 and argv[2] == "debug" else 0
        assert(4>=debug and debug>=0)
        tp =TermParser()
        I = Interpretation()
        with open(argv[1]) as f:
            unif, mappings= tp.parse_input(f.readlines())
            for m in mappings:I.add_mapping(*m)
            I.add_relevent_vars(unif)
            lu = LoopUnif(I,debug,unif)
            lu.loop_unif()
