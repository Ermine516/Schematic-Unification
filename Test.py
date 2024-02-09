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
        isunif = {1:True,2:True,3:True,4:False,5:False,6:False, \
        7:True,8:True,9:False,10:False,11:True,12:True,\
        13:False,14:True,15:True,16:True,17:True,18:False, \
        19:True,20:True,21:False,22:False}
        for i in range(1,len(onlyfiles)+1):
            tp =TermParser()
            unifProb = UnificationProblem(-1)
            with open("Examples/tests/"+onlyfiles[i-1]) as f:
                unif, mappings= tp.parse_input(f.readlines())
                unifProb.addMappings(mappings.items())
                unifProb.addEquations(unif)
                unifProb.makePrimitive()
                su = SchematicUnification(unifProb,-1)
                start_time = time.time()
                worked, tottime = su.unif(time.time())
                print(f"Test {str(i)} {"Passed" if worked == isunif[i]  else "Failed" } -- {round(tottime, 3)} Seconds")
