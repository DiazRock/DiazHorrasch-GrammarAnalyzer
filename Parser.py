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
        initialSymbol = NoTerminal(name = grammar.initialSymbol.name + "'")                
        d = {initialSymbol : tuple([grammar.initialSymbol])}
        d.update(grammar.nonTerminals)
        self.augmentedGrammar = GrammarClass(initialSymbol = None, terminals = [], nonTerminals=[] )
        self.augmentedGrammar.initialSymbol = initialSymbol
        self.augmentedGrammar.terminals = grammar.terminals
        self.augmentedGrammar.nonTerminals = d

    def canonical_LR(self, need_lookahead = False):
        initialState =canonical_State (label = "I{0}".format(0), setOfItems = [Item(label = {FinalSymbol()} if need_lookahead else None, grammar = self.augmentedGrammar, nonTerminal= self.augmentedGrammar.initialSymbol, point_Position = 0, production = self.augmentedGrammar.nonTerminals[self.augmentedGrammar.initialSymbol])], grammar = self.augmentedGrammar)          
        canonical_states = [initialState]
        statesQueue = [canonical_states[0]]
        transition_table = {}
        
        while (statesQueue):
            currentState = statesQueue.pop(0)
            currentState.setOfItems = (LR_Parser.closure(self, currentState.kernel_items))
            symbols = {item.production[item.point_Position] for item in currentState.setOfItems if item.point_Position < len(item.production)}
            for x in symbols:                
                new_state = LR_Parser.goto(self, currentState, x, len(canonical_states))
                if not new_state in canonical_states:
                    canonical_states.append(new_state)
                    statesQueue.append(new_state)
                transition_table.update({(currentState, x): new_state})     

        grammar_symbols = {x for x in self.augmentedGrammar.nonTerminals}.union(self.augmentedGrammar.terminals)        
        return Automaton(states = canonical_states, symbols = grammar_symbols, initialState =canonical_states[0], FinalStates = canonical_states, transitions = transition_table )            

    def goto(self, current_state, grammar_symbol, index):
        new_state = canonical_State(label = "I{0}".format(index), setOfItems = [], grammar = self.augmentedGrammar)
        for item in current_state.setOfItems:
            if item.point_Position < len(item.production):
                if item.production[item.point_Position] == grammar_symbol:
                    new_state.extend([Item(label = item.label, grammar = self.augmentedGrammar, nonTerminal = item.nonTerminal, point_Position = item.point_Position + 1, production = item.production)])
        return new_state
        

    def closure(self, kernel_items):
        closure = list(kernel_items)
        itemsQueue = list(kernel_items)
        visited = {X:False for X in self.augmentedGrammar.nonTerminals}
        while(itemsQueue):
            current = itemsQueue.pop(0)
            if current.point_Position < len(current.production):                        
                X = current.production[current.point_Position]
                looks_ahead = { symbol for symbol in FirstsForBody(current.production[current.point_Position +1:] + tuple(current.label), self.Firsts) } if current.label else None
                if looks_ahead and Epsilon() in looks_ahead: looks_ahead = {current.label}
                if (isinstance(X, NoTerminal)):
                    itemsToQueue = []
                    for prod in self.augmentedGrammar.nonTerminals[X]:
                        if not visited[X]:
                            itemToAppend = Item(label = looks_ahead, grammar = self.augmentedGrammar, nonTerminal= X, point_Position = 0, production = prod)
                            itemsToQueue.append(itemToAppend)
                        elif not looks_ahead: break
                        if looks_ahead:                        
                            for item in closure:
                                if item.nonTerminal == X:
                                    item.label.update(looks_ahead)                            
                    itemsQueue.extend(itemsToQueue)
                    visited[X] = True
                    closure.extend(itemsToQueue)            
        return closure
