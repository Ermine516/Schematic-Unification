from Term import *
from abc import ABC, abstractmethod
import time
class Solver(ABC):

    class ClashExeption(Exception):
        def __init__(self,t1,t2,start_time=-1):
            self.lterm = t1
            self.rterm = t2
            self.start_time=start_time
        def handle(self,debug):
            if debug>0:
                print()
                print("symbol clash: ",self.lterm,set(self.rterm))
                print()
            elif debug == 0:
                print(f"\t Not unifiable --- {round(time.time() - self.start_time,3)} seconds ---")

            return False, (time.time() - self.start_time)
        pass
    class CycleException(Exception):
        def __init__(self,prob,addendum="",start_time=-1):
            self.ununified = prob
            self.addendum=addendum
            self.start_time=start_time
        def handle(self,debug):
            if debug >0:
                if self.addendum=="":print("Cycle Detected:")
                else:  print("Cycle Detected ("+self.addendum+"):")
                print(self.ununified)             
            
            elif debug == 0:
                print(f"\t Not unifiable --- {round(time.time() - self.start_time,3)} seconds ---")
            return False, (time.time() - self.start_time)
        pass
    @abstractmethod
    def __init__(self,SchematicSubstitution=None,debug=0,start_time=-1):
        self.SchematicSubstitution= SchematicSubstitution
        self.debug = debug
        self.start_time = start_time

        pass
        
    @abstractmethod
    def unify(self,problem):
        pass

    def setTime(self,t): 
        self.start_time=t