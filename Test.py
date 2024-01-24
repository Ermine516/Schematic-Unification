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
        isunif = {1:"unifiable",2:"unifiable",3:"unifiable",4:"not unifiable",5:"not unifiable",6:"not unifiable", \
        7:"unifiable",8:"unifiable",9:"not unifiable",10:"not unifiable",11:"unifiable",12:"unifiable",\
        13:"not unifiable",14:"unifiable",15:"unifiable",16:"unifiable",17:"unifiable",18:"not unifiable", \
        19:"unifiable"}
        for i in range(1,len(onlyfiles)+1):
            print("Test "+str(i)+ " (should be "+isunif[i]+")")
            tp =TermParser()
            I = SchematicSubstitution()
            with open("Examples/tests/"+onlyfiles[i-1]) as f:
                unif, mappings= tp.parse_input(f.readlines())
                for m in mappings:I.add_mapping(*m)
                su = SchematicUnification(I,0,unif)
                su.unif(time.time())
