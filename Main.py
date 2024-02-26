from sys import argv
from SchematicUnification import *
from SchematicSubstitution import *
from UnificationProblem import *

from functools import reduce
from TermParser import *
from os import listdir
from Test import *
import argparse
import time

class ArgumentNotFound(Exception):
    def __init__(self):
        super().__init__()
    def handle(self):
        print("A number must be provide (python main.py Unfold -uf i) in Unfold mode")

CodeDescription='Algorithm for deciding unifiability of Uniform Schematic Unification Problems.'

def parsing_CMD():
        parser = argparse.ArgumentParser(description=CodeDescription)
        parser.add_argument('procedure', choices=['Test','Unif','Unfold'], help='Currently either Test or Unification')
        parser.add_argument('-f',metavar="file.su", default="",help='The unification problem to Solve. Igored when in Test mode')
        parser.add_argument('-uf',metavar="i", default="0",help='number of times to unfold problem before unifying. Usinged with Unfold mode')

        parser.add_argument('--debug',metavar="int",type=int,choices=[-1,0,1,2,3,4,5,6],default=1,help='Debug level: 0 is the lowest and 3 is the highest.')

        return  parser.parse_args()
def readUnifFile():
    tp =TermParser()
    unifProb = UnificationProblem(args.debug)
    try: 
        with open(args.f) as f:
            try:
                unif, mappings= tp.parse_input(f.readlines())
                unifProb.addMappings(mappings.items())
                unifProb.addEquations(unif)
                unifProb.makePrimitive()
            except UnusedVariableDefinitionWarning as e:
                e.handle()
                return None               
            except ArityMismatchException as e:
                e.handle()
                return None
            except SymbolTypeMisMatchException as e:
                e.handle()
                return None
            except UndefinedInterpretedException as e:
                e.handle()
                return None
            except unknownInputException as e:
                e.handle()
                return None
            except noUnificationProblemException as e:
                e.handle()
                return None
            except InvalidRecursionException as e:
                e.handle()
                return None
            except OutofOrderInputException as e:
                return None    
            except nonUniforminputException as e:
                if e.handle(): return None
            except MappingReAssignmentException as e:
                e.handle()
                return None   
    except FileNotFoundError as e:
        print("A file must be provide (python main.py Unif -f file.su) or run test mode (python main.py Test) ")
    return unifProb

def unify():
    unifProb = readUnifFile()
    su = SchematicUnification(unifProb,args.debug)
    start_time = time.time()
    su.unif(time.time())

def unfold():
    unifProb = readUnifFile()
    ufUnifProb = unifProb.instance()
    try:
        unfoldings = int(args.uf)
        for i in range(unfoldings):
            ufUnifProb = ufUnifProb.increment(unifProb.schSubs)
    except ArgumentNotFound as e:
        e.handle()
        return None
    foSolver = MM(unifProb.schSubs,args.debug)
   
    try:
        results , _ = foSolver.unify(ufUnifProb.prob,True)
    except Solver.CycleException as e:
        return e.handle(args.debug)
    except Solver.ClashExeption as e:  
        return e.handle(args.debug)
    toremove =[]
    for x in results:
        if x.vc[0:2]=="MM":
            toremove.append(x)
    for x in toremove:
        results.removebinding(x)
    print(ufUnifProb)
    print(results)

if __name__ == "__main__":
    args= parsing_CMD()
    if args.procedure=="Test":
        Test.test()
    elif args.procedure=="Unif":
        unify()
    elif args.procedure=="Unfold":
        unfold()
