from SchematicUnification import *
from SchematicSubstitution import *
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
        19:True,20:False,21:False,22:False,23:True,24:True, \
        25:True,26:False,27:False,28:False,29:True,30:True, \
        31:True,32:True,33:True,34:True,35:False}
        for i in range(1,len(onlyfiles)+1):
            tp =TermParser()
            unifProb = UnificationProblem(-1)
            schsub = SchematicSubstitution()
            with open("Examples/tests/"+onlyfiles[i-1]) as f:
                unif, mappings= tp.parse_input(f.readlines())
                for x,y in mappings.items(): schsub.add_interpreted(x,y)
                unifProb.addEquations(unif)
                schsub = unifProb.makePrimitive(schsub)
                su = SchematicUnification(unifProb,schsub,-1)
                start_time = time.time()
                worked, tottime = su.unif(time.time())
                sp1 = " "*(9-len(str(round(tottime, 3))))
                sp2 = " "*(4-len(str(i)))
                print(f"Test {str(i)}{sp2}{"Passed" if worked == isunif[i]  else "Failed" } -- {round(tottime, 3)}{sp1}Seconds")
                

