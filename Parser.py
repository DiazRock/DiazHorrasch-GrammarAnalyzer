from AuxiliarMethods import *
from Automaton import *
class Parser:
    def __init__(self, grammar:GrammarClass):
        self.inputSymbols = grammar.terminals.union ({FinalSymbol()})
        


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
            return True
        else:
            print ("Error, la gramática no es LL(1):\nConflictos a la hora de escoger entre las decisiones {0} y {1} para el terminal {2}".format(
                (symbolForStack,table[(symbolForStack, inputSymbol)]), (symbolForStack, prod), inputSymbol))
            return False
        
    def __init__(self, grammar):
        super().__init__(grammar)
        self.symbolsForStack = grammar.nonTerminals.copy()         
        self.table = self.buildTable()
class LR_Parser(PredictiveParser):
    def __init__(self, grammar:GrammarClass):
        super().__init__(grammar)
        self.stack = []        
        self.initialSym = grammar.initialSymbol
        self.augmentedGrammar = GrammarClass(initialSymbol = NoTerminal(name = self.initialSym + "'"), terminals = grammar.terminals, nonTerminals={NoTerminal(name = self.initialSym + "'")}.union(grammar.nonTerminals) )

    def canonical_LR(self):
        initialState =canonical_State (setOfItems = [item(label = "I{0}".format(0), grammar = self.augmentedGrammar, nonTerminal= self.augmentedGrammar.initialSymbol, point_Position = 0, production = self.augmentedGrammar.nonTerminals[self.augmentedGrammar.initialSymbol])], grammar = self.augmentedGrammar)          
        canonical_states = [initialState]
        statesQueue = [canonical_states[0]]
        transition_table = {}

        while (statesQueue):
            currentState = statesQueue.pop(0)
            currentState.extend (LR_Parser.closure(self, currentState.kernel_items))
            symbols = {x for x in item.production[item.point_Position:] for item in currentState.setOfItems}    
            for x in symbols:
                new_state = LR_Parser.goto(self, currentState, x)
                if not new_state in canonical_states:
                    canonical_states.append(new_state)
                    statesQueue.append(new_state)
                    transition_table.update({(currentState, x): new_state})

    def goto(self, current_state, grammar_symbol):
        new_state = canonical_State(setOfItems = [], grammar = self.augmentedGrammar)
        for item in current_state.kernel_items:
            if item.production[item.point_Position] == grammar_symbol:
                new_state.extend([])
            pass
        pass

    def closure(self, kernel_items):
        closure = []
        itemsQueue = list(kernel_items)
        visited = {X:False for X in self.augmentedGrammar.nonTerminals}
        for item in kernel_items:
            visited[item.nonTerminal] = True
        while(itemsQueue):
            current = itemsQueue.pop(0)            
            for X in current.production[current.point_Position: ]:
                if (isinstance(X, NoTerminal) and not visited[X]):
                    itemsToQueue = [item(label = "{0} {1} {2}".format(X, 0, prod)) for prod in self.augmentedGrammar.nonTerminals[X]]
                    itemsQueue.extend(itemsToQueue)
                    visited[X] = True
                    closure.extend(itemsToQueue)            
        return closure
