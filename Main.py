from sys import argv
from SchematicUnification import *
from SchematicSubstitution import *
from functools import reduce
from TermParser import *
from os import listdir
from Test import *
import argparse
import time

CodeDescription='Algorithms for deciding unifiability of Linear Primitive Unification Problems.'

def parsing_CMD():
        parser = argparse.ArgumentParser(description=CodeDescription)
        parser.add_argument('procedure', choices=['Test','Unif'], help='Currently either Test or Unification')
        parser.add_argument('-f',metavar="file.su", default="",help='The unification problem to Solve. Igored when in Test mode')
        parser.add_argument('--debug',metavar="int",type=int,choices=[-1,0,1,2,3,4,5,6],default=1,help='Debug level: 0 is the lowest and 3 is the highest.')

        return  parser.parse_args()
def unify():
    tp =TermParser()
    I = SchematicSubstitution()
    try: 
        with open(args.f) as f:
            try:
                unif, mappings= tp.parse_input(f.readlines())
                for m in mappings.items():I.add_mapping(*m)
                for u in unif:  I.add_relevent_vars(u)
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
            except SchematicSubstitution.InvalidRecursionException as e:
                e.handle()
                return None
            except OutofOrderInputException as e:
                e.handle()
                return None    
            except nonlinearinputException as e:
                return None  
            except nonPrimitiveinputException as e:
                return None
            except MappingReAssignmentException as e:
                e.handle()
                return None
            su = SchematicUnification(I,args.debug,unif)
            start_time = time.time()
            su.unif(time.time())
    except FileNotFoundError as e:
        print("A file must be provide (python main.py Unif -f file.su) or run test mode (python main.py Test) ")

if __name__ == "__main__":
    args= parsing_CMD()
    if args.procedure=="Test":
        Test.test()
    elif args.procedure=="Unif":
        unify()
