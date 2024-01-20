from typing import Set, Tuple, Dict
from collections import defaultdict
from functools import reduce
from Term import *
from abc import ABC, abstractmethod

class Solver(ABC):

    class ClashExeption(Exception):
        def __init__(self,t1,t2):
            self.lterm = t1
            self.rterm = t2
        def handle(self,debug):
            print()
            print("symbol clash: ",self.lterm,set(self.rterm))
            #print("solved set: ",solved)
            print()

            return None
        pass
    class CycleException(Exception):
        def __init__(self,prob,addendum=""):
            self.ununified = prob
            self.addendum=addendum
        def handle(self,debug):
            if debug >0:
                if self.addendum=="":print("Cycle Detected:")
                else:  print("Cycle Detected ("+self.addendum+"):")
                for x in self.ununified:
                    print("\t"+x.format())
                print()
            else: print("\t not unifiable")
            return None
        pass
    @abstractmethod
    def __init__(self,SchematicSubstitution=None,debug=0):
        self.SchematicSubstitution= SchematicSubstitution
        self.debug = debug
        pass
        
    @abstractmethod
    def unify(self,problem):
        pass