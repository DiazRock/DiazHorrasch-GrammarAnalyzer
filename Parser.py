
from AuxiliarMethods import *

class Parser:
    def __init__(self, grammar:GrammarClass):
        self.inputSymbols = grammar.terminals.union ({FinalSymbol()})
        self.symbolsForStack = grammar.nonTerminals.copy()         


class PredictiveParser(Parser):
    def __init__(self, grammar:GrammarClass):
        super().__init__(grammar)
        self.Firsts = CalculateFirst(grammar)
        for productions in grammar.nonTerminals.values():
            for prod in productions:
                self.Firsts.update({prod: FirstsForBody(prod, self.Firsts)})        
        self.Follows = CalculateFollow(grammar,self.Firsts)
        

class LL_Parser(PredictiveParser):
    def buildTable(self):
        table = {(x,y):[] for x in self.symbolsForStack.keys() for y in self.inputSymbols}
        for X in self.symbolsForStack:
            for prod in self.symbolsForStack[X]:
                if len(prod) == 1 and prod[0] == Epsilon():
                    for t in self.Follows[X]:
                        if not self.Asign(table, X, t, prod):return None
                else:
                    for t in self.Firsts[prod]:
                        if t == Epsilon():
                            for terminal in self.Follows[X]:
                                if not self.Asign(table, X, terminal, prod): return None
                        else:
                            if not self.Asign(table, X, t, prod): return None
        return table

    def printTable(self):
        print(end ='\t')
        for x in self.inputSymbols:
            print(x, end= '\t')
        print('\n')
        for y in self.symbolsForStack:
            print(y,end ='\t')
            for x in self.inputSymbols:
                print(self.table[y,x],end ='\t')
            print('\n')

    def Asign(self,table, symbolForStack, inputSymbol, prod):
        if not table[(symbolForStack,inputSymbol)]:
            table[(symbolForStack, inputSymbol)] = prod
        else:
            print ("Error, la gramática no es LL(1):\nConflictos a la hora de escoger entre las decisiones {0} y {1} para el terminal {2}".format((symbolForStack,table[(symbolForStack, inputSymbol)]), (symbolForStack, inputSymbol), inputSymbol))
            return None
        
    def __init__(self, grammar):
        super().__init__(grammar)
        self.table = self.buildTable()            
