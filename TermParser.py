from pyparsing import *
from Term import *


class UnusedVariableDefinitionWarning(Exception):
    def __init__(self,var):
        self.var = var

    def handle(self):
        print("Warning: The interpretation of "+self.var+" is not used by the provided unification problem.")
        print()
class UndefinedInterpretedException(Exception):
    def __init__(self,var):
        self.var = var

    def handle(self):
        print("The interpreted variable "+self.var+" is undefined. All interpreted variables must be defined.")

class ArityMismatchException(Exception):
    def __init__(self,symbol,arity,expectedArity):
        self.sym = symbol
        self.ari = arity
        self.eari = expectedArity

    def handle(self):
        print("The symbol "+self.sym.name+" has arity "+str(self.ari)+" but is used with arity "+str(self.eari)+"."+ "check for missing \'(\',\')\', or \',\'")

class SymbolTypeMisMatchException(Exception):
    def __init__(self,symbol,type,expectedtype):
        self.sym = symbol
        self.type = type
        self.etype = expectedtype

    def handle(self):
        print("The symbol "+self.sym+" has type "+str(self.type)+" but is used with type "+str(self.etype)+"."+ "check for misplaced \'(\',\')\',\'[\',\']\', or \'_\'")

class TermParser:

    def __init__(self):

        self.found_vars = {}
        self.found_symbols = {}
        self.found_rec = {}
        self.symbols = {}
        self.term_construct = Forward()
        self.variable_symbol = (Word(alphas)+Suppress("[")+Word(nums)+Suppress("]")).set_parse_action(self.make_var)
        self.Interpreted_symbol = (Word(alphas)+Suppress("_")+Word(nums)).set_parse_action(self.make_interpreted)
        self.function_symbol = (Word(alphas)+Suppress("(")+ZeroOrMore(self.term_construct+Suppress(","))+self.term_construct+Suppress(")")).set_parse_action(self.make_function)
        self.constant_symbol = Word(alphas).set_parse_action(self.make_const)
        self.app_construct = self.function_symbol | self.constant_symbol
        self.term_construct <<=  self.variable_symbol | self.Interpreted_symbol | self.app_construct
        self.a_rec  = Word(alphas).set_parse_action(self.is_interpreted)
        self.unification_problem = self.term_construct +Suppress("=?=")+ self.term_construct
        self.mapping_problem = self.a_rec +Suppress("<==")+ self.term_construct


    def is_interpreted(self,s,loc,toks):
        if not toks[0] in self.found_rec.keys():
            UnusedVariableDefinitionWarning(toks[0]).handle()
        else: return self.found_rec[toks[0]]
    def make_var(self,s,loc,toks):
        if not toks[0] in self.symbols.keys(): self.symbols[toks[0]] = Var
        elif self.symbols[toks[0]] != Var: raise SymbolTypeMisMatchException(toks[0],self.symbols[toks[0]],Var)
        if not toks[0] in self.found_vars.keys():self.found_vars[toks[0]] = {}
        if not toks[1] in self.found_vars[toks[0]].keys():self.found_vars[toks[0]][toks[1]] = Var(toks[0],int(toks[1]))
        return self.found_vars[toks[0]][toks[1]]

    def make_const(self,s,loc,toks):
        if not toks[0] in self.symbols.keys(): self.symbols[toks[0]] = App
        elif self.symbols[toks[0]] != App: raise SymbolTypeMisMatchException(toks[0],self.symbols[toks[0]],App)
        if not toks[0] in self.found_symbols.keys():self.found_symbols[toks[0]] = Func(toks[0],0)
        elif self.found_symbols[toks[0]].arity!=0: raise ArityMismatchException(self.found_symbols[toks[0]],self.found_symbols[toks[0]].arity,0)
        return self.found_symbols[toks[0]]()

    def make_function(self,s,loc,toks):
        if not toks[0] in self.symbols.keys(): self.symbols[toks[0]] = App
        elif self.symbols[toks[0]] != App: raise SymbolTypeMisMatchException(toks[0],self.symbols[toks[0]],App)
        if not toks[0] in self.found_symbols.keys():self.found_symbols[toks[0]] = Func(toks[0],len(toks)-1)
        elif self.found_symbols[toks[0]].arity!=len(toks)-1: raise  ArityMismatchException(self.found_symbols[toks[0]],self.found_symbols[toks[0]].arity,len(toks)-1)
        return self.found_symbols[toks[0]](*toks[1:len(toks)])

    def make_interpreted(self,s,loc,toks):
        if not toks[0] in self.symbols.keys(): self.symbols[toks[0]] = Rec
        elif self.symbols[toks[0]] != Rec: raise  SymbolTypeMisMatchException(toks[0],self.symbols[toks[0]],Rec)
        if not toks[0] in self.found_rec.keys():self.found_rec[toks[0]] =Func(toks[0],1)
        return self.found_rec[toks[0]](Idx(int(toks[1])))

    def parse_input(self,input):
        unif = set()
        mappings =[]
        for l in input:
            if  "##" != l[0:2] and "=?=" in l:
                unif.add(tuple(self.unification_problem.parseString(l)))
            elif "##" != l[0:2] and "<==" in l:
                mappings.append(tuple(self.mapping_problem.parseString(l)))
            else:
                continue
        test=[ l.name for l,r in mappings]
        for x in self.found_rec.keys():
            if not x in test:
                raise UndefinedInterpretedException(x)
        return (unif,mappings)
