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
        d = {initialSymbol : [tuple([grammar.initialSymbol])]}
        d.update(grammar.nonTerminals)
        self.augmentedGrammar = GrammarClass(initialSymbol = None, terminals = [], nonTerminals=[] )
        self.augmentedGrammar.initialSymbol = initialSymbol
        self.augmentedGrammar.terminals = grammar.terminals
        self.augmentedGrammar.nonTerminals = d
        self.Firsts = CalculateFirst(self.augmentedGrammar)
        self.Follows = CalculateFollow(self.augmentedGrammar, self.Firsts)
        

    def canonical_LR(self, need_lookahead = False):
        initialState =canonical_State (label = "I{0}".format(0), setOfItems = [Item(label = {FinalSymbol()} if need_lookahead else None, grammar = self.augmentedGrammar, nonTerminal= self.augmentedGrammar.initialSymbol, point_Position = 0, production = self.augmentedGrammar.nonTerminals[self.augmentedGrammar.initialSymbol][0])], grammar = self.augmentedGrammar)          
        canonical_states = [initialState]
        statesQueue = [canonical_states[0]]
        transition_table = {}
        
        while (statesQueue):
            currentState = statesQueue.pop(0)
            currentState.setOfItems = (LR_Parser.closure(self, currentState.kernel_items))            
            symbols = {item.production[item.point_Position] for item in currentState.setOfItems if item.point_Position < len(item.production)}
            for x in symbols:                
                new_state = LR_Parser.goto(self, currentState, x, len(canonical_states))
                if isinstance(new_state, Fail): return new_state                
                if not new_state in canonical_states:
                    canonical_states.append(new_state)
                    statesQueue.append(new_state)
                transition_table.update({(currentState, x): new_state})     

        grammar_symbols = {x for x in self.augmentedGrammar.nonTerminals}.union(self.augmentedGrammar.terminals)        
        return Automaton(states = canonical_states, symbols = grammar_symbols, initialState =canonical_states[0], FinalStates = canonical_states, transitions = transition_table )            

    def goto(self, current_state, grammar_symbol, index):
        new_state = canonical_State(label = "I{0}".format(index), setOfItems = [], grammar = self.augmentedGrammar)
        item_reduces = item_shifts = []
        for item in current_state.setOfItems:
            if item.point_Position < len(item.production):
                if item.production[item.point_Position] == grammar_symbol:
                    to_extend = Item(label = item.label, grammar = self.augmentedGrammar, nonTerminal = item.nonTerminal, point_Position = item.point_Position + 1, production = item.production)                    
                    new_state.extend([to_extend])
                    if to_extend.point_Position == len(to_extend.production):
                        item_reduces.append(to_extend)
                    else:
                        item_shifts.append(to_extend)

        for item in item_reduces:
            #Buscando reduce-reduce
            for to_compare in item_reduces:
                if Item(label = "item", grammar = self.augmentedGrammar, nonTerminal= to_compare.nonTerminal, point_Position = to_compare.point_Position, production = to_compare.production) == Item(label = "item", grammar = self.augmentedGrammar, nonTerminal= item.nonTerminal, point_Position = item.point_Position, production = item.production): continue
                intersection = self.Follows[item.nonTerminal].intersection(self.Follows[to_compare.nonTerminal])
                if item.production == to_compare.production and intersection:
                    return Fail(error_message="Conflicto reduce-reduce para los items {0} y {1} al tener el símbolo de entrada {2} en el estado {3}".format(item, to_compare, item.production[item.point_Position-1], new_state))
            #Buscando shift-reduce    
            for to_compare in item_shifts:
                if item.production == to_compare.production[:item.point_Position -1]:
                    if isinstance (to_compare.production[item.point_Position], NoTerminal):
                         if item.production[item.point_Position] in self.Follows[to_compare.production[item.point_Position]]:
                            return Fail(error_message="Conflicto shift-reduce para los items {0} y {1} al tener el símbolo de entrada {2} en el estado {3}".format(item, to_compare, item.production[item.point_Position-1], new_state))

        return new_state
        

    def closure(self, kernel_items):
        closure = list(kernel_items)
        itemsQueue = list(kernel_items)        
        while(itemsQueue):
            current = itemsQueue.pop(0)
            if current.point_Position < len(current.production):
                X = current.production[current.point_Position]
                looks_ahead = { symbol for symbol in FirstsForBody(current.production[current.point_Position +1:] + tuple(current.label), self.Firsts) } if current.label else None
                if looks_ahead and Epsilon() in looks_ahead: looks_ahead = {current.label}
                if (isinstance(X, NoTerminal)):
                    itemsToQueue = []
                    for prod in self.augmentedGrammar.nonTerminals[X]:
                        itemToAppend = Item(label = looks_ahead, grammar = self.augmentedGrammar, nonTerminal= X, point_Position = 0, production = prod)
                        if not itemToAppend in closure:
                            itemsToQueue.append(itemToAppend)                        
                    itemsQueue.extend(itemsToQueue)                    
                    closure.extend(itemsToQueue)            
        return closure

    def LALR(self):
        LR_Automaton = LR_Parser.canonical_LR(self,need_lookahead= True)
        if isinstance(LR_Automaton, Fail): return LR_Automaton


class Fail:
    def __init__(self, error_message):
        self.error_message = error_message