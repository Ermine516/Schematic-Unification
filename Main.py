from sys import argv
from LoopUnif import *
from Interpretation import *
from functools import reduce
from TermParser import *
from os import listdir
from Test import *
import argparse
CodeDescription='Algorithms for deciding unifiability of simple loop unification problem.'

def parsing_CMD():
        parser = argparse.ArgumentParser(description=CodeDescription)
        parser.add_argument('procedure', choices=['Test','Build','Amm'], help='Currently either Test, Build, or Augmented Martelli-Montanari.')
        parser.add_argument('unif_prob',metavar="file.su", default="",help='The unification problem to Solve. Igored when in Test mode')
        parser.add_argument('--debug',metavar="int",type=int,choices=[0,1,2,3],default=1,help='Debug level: 0 is the lowest and 3 is the highest.')
        parser.add_argument('--unroll',metavar="int",type=int,default=0,help='Used for Build mode: Number of times to unroll the interpreted variables.')
        parser.add_argument('--unifier',default=False,action='store_true',help='Experimental: Computes the unifier.')

        return  parser.parse_args()
def unify():
    tp =TermParser()
    I = Interpretation()
    with open(args.unif_prob) as f:
        try:
            unif, mappings= tp.parse_input(f.readlines())
        except ArityMismatchException as e:
            e.handle()
            return None
        except SymbolTypeMisMatchException as e:
            e.handle()
            return None
        except UndefinedInterpretedException as e:
            e.handle()
            return None
        for m in mappings:I.add_mapping(*m)
        for u in unif:
            I.add_relevent_vars(u)
        lu = LoopUnif(I,args.debug,unif,unifierCompute=args.unifier)
        lu.loop_unif()

if __name__ == "__main__":
    args= parsing_CMD()
    if args.procedure=="Test":
        Test.test()
    elif args.procedure=="Build":
        Test.testExampleSize(args.unif_prob,args.unroll,args.debug)
    elif args.procedure=="Amm":
        unify()
    elif args.procedure=="Exu":
        unify2()
