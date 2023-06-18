from pyparsing import *
from Term import *


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
        if not toks[0] in self.found_rec.keys(): raise Exception
        else: return self.found_rec[toks[0]]
    def make_var(self,s,loc,toks):
        if not toks[0] in self.symbols.keys(): self.symbols[toks[0]] = Var
        elif self.symbols[toks[0]] != Var: raise Exception
        if not toks[0] in self.found_vars.keys():self.found_vars[toks[0]] = {}
        if not toks[1] in self.found_vars[toks[0]].keys():self.found_vars[toks[0]][toks[1]] = Var(toks[0],int(toks[1]))
        return self.found_vars[toks[0]][toks[1]]

    def make_const(self,s,loc,toks):
        if not toks[0] in self.symbols.keys(): self.symbols[toks[0]] = App
        elif self.symbols[toks[0]] != App: raise Exception
        if not toks[0] in self.found_symbols.keys():self.found_symbols[toks[0]] = Func(toks[0],0)
        elif self.found_symbols[toks[0]].arity!=0: raise Exception
        return self.found_symbols[toks[0]]()

    def make_function(self,s,loc,toks):
        if not toks[0] in self.symbols.keys(): self.symbols[toks[0]] = App
        elif self.symbols[toks[0]] != App: raise Exception
        if not toks[0] in self.found_symbols.keys():self.found_symbols[toks[0]] = Func(toks[0],len(toks)-1)
        elif self.found_symbols[toks[0]].arity!=len(toks)-1: raise Exception
        return self.found_symbols[toks[0]](*toks[1:len(toks)])

    def make_interpreted(self,s,loc,toks):
        if not toks[0] in self.symbols.keys(): self.symbols[toks[0]] = Rec
        elif self.symbols[toks[0]] != Rec: raise Exception
        if not toks[0] in self.found_rec.keys():self.found_rec[toks[0]] =Func(toks[0],1)
        return self.found_rec[toks[0]](Idx(int(toks[1])))

    def parse_input(self,input):
        unif = None
        mappings =[]
        for l in input:
            if  "##" != l[0:2] and "=?=" in l:
                unif = list(self.unification_problem.parseString(l))
            elif "##" != l[0:2] and "<==" in l:
                mappings.append(tuple(self.mapping_problem.parseString(l)))
            else:
                continue
        return (unif,mappings)
