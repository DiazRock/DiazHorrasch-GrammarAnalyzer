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
            otherCurrent = None
            if not isinstance(statesQueue[0], tuple):
                currentState = statesQueue.pop(0)
            else:
                currentState, otherCurrent = statesQueue.pop(0)
            currentState.setOfItems = (LR_Parser.closure(self, currentState.kernel_items))            
            symbols = {item.production[item.point_Position] for item in currentState.setOfItems if item.point_Position < len(item.production)}
            for x in symbols:                
                new_state = LR_Parser.goto(self, currentState, x, len(canonical_states))
                if otherCurrent:
                    if transition_table[(otherCurrent,x)] != new_state:
                        return Fail("No se puede hacer la mezcla LALR, ya que hay indeterminismo para los estados {0}:{3} y {1}:{4} con el símbolo {2}".format(currentState, otherCurrent, x, new_state, transition_table[(otherCurrent, x)]))
                    
                founded = False
                state_for_mixed = None
                for state in canonical_states:
                    if state == new_state:
                        if need_lookahead :
                            if state.equal_looksahead(new_state):
                                founded = True
                            if founded:
                                break
                            state_for_mixed = state if need_lookahead is 2 else None
                            if state_for_mixed: 
                                break
                        else:
                            founded = True
                            break                           

                if not founded:
                    if not state_for_mixed:
                        canonical_states.append(new_state)
                        statesQueue.append(new_state)
                    else:
                        changed = False
                        for i in range(len(state_for_mixed.kernel_items)):
                            before = len(state_for_mixed.kernel_items[i].label)
                            state_for_mixed.kernel_items[i].label.update(new_state.kernel_items[i].label)
                            changed = not before == len(state_for_mixed.kernel_items[i].label)
                        if changed:    
                            state_for_mixed.label += "-" + new_state.label
                            statesQueue.append((new_state,state_for_mixed))
                
                transition_table.update({(currentState, x): new_state})     

        grammar_symbols = {x for x in self.augmentedGrammar.nonTerminals}.union(self.augmentedGrammar.terminals)        
        return Automaton(states = canonical_states, symbols = grammar_symbols, initialState =canonical_states[0], FinalStates = canonical_states, transitions = transition_table )            

    def goto(self, current_state, grammar_symbol, index):
        new_state = canonical_State(label = "I{0}".format(index), setOfItems = [], grammar = self.augmentedGrammar)
        
        for item in current_state.setOfItems:
            if item.point_Position < len(item.production):
                if item.production[item.point_Position] == grammar_symbol:
                    to_extend = Item(label = item.label.copy() if item.label else None, grammar = self.augmentedGrammar, nonTerminal = item.nonTerminal, point_Position = item.point_Position + 1, production = item.production)                    
                    new_state.extend([to_extend])        
        return new_state
        

    def closure(self, kernel_items):
        closure = list(kernel_items)
        itemsQueue = list(kernel_items)        
        while(itemsQueue):
            current = itemsQueue.pop(0)
            if current.point_Position < len(current.production):
                X = current.production[current.point_Position]

                if current.label:
                    looks_ahead = set()
                    for ahead_symbol in current.label:
                        to_update = FirstsForBody(current.production[current.point_Position +1:] + tuple([ahead_symbol]), self.Firsts)
                        looks_ahead.update(to_update)
                else:
                    looks_ahead = None

                if looks_ahead and Epsilon() in looks_ahead: looks_ahead = {current.label}
                if (isinstance(X, NoTerminal)):
                    itemsToQueue = []
                    for prod in self.augmentedGrammar.nonTerminals[X]:
                        itemToAppend = Item(label = looks_ahead.copy() if looks_ahead else None, grammar = self.augmentedGrammar, nonTerminal= X, point_Position = 0, production = prod if prod != tuple([Epsilon()]) else ())
                        founded = False
                        for item in closure:
                            if item == itemToAppend:
                                if item.label: item.label.update(itemToAppend.label)
                                founded = True                                
                        if not founded:
                            itemsToQueue.append(itemToAppend)
                                                                           
                    itemsQueue.extend(itemsToQueue)                    
                    closure.extend(itemsToQueue)            
        return closure

    def buildTable(self, parser_type = 0):        
        LR_Automaton = LR_Parser.canonical_LR(self, parser_type)
        inputSymbols = self.augmentedGrammar.terminals.union(self.augmentedGrammar.nonTerminals).union({FinalSymbol()})
        table = {(state,symbol):[] for state in LR_Automaton.states for symbol in inputSymbols}
        conflict_info = {state:[] for state in LR_Automaton.states}
        was_conflict = False
        for state in LR_Automaton.states:
            for item in state.setOfItems:
                shift_reduce_conflict = reduce_reduce_conflict = False
                conflict_symbol = None
                if item.point_Position < len(item.production):
                    symbol = item.production[item.point_Position]
                    shift_reduce_conflict = table[(state, symbol)]
                    conflict_symbol = symbol                                          
                    table[(state,symbol)] = shift(table_tuple = tuple([state,symbol]), response = item, label = "S" + LR_Automaton.transitions[(state, symbol)].label[1:] if isinstance(symbol, Terminal) else LR_Automaton.transitions[(state, symbol)].label )

                else:
                    looks_ahead = self.Follows[item.nonTerminal] if not parser_type else item.label
                    for symbol in looks_ahead:
                        if table[state,symbol]:
                            conflict_symbol = symbol
                            if isinstance(table[state,symbol], shift):
                                shift_reduce_conflict = table[state,symbol]
                            else:
                                reduce_reduce_conflict = table[state, symbol]
                        
                        table[state,symbol] = reduce(table_tuple = (state, symbol), response = item, label = repr(item)) 
                        
                if shift_reduce_conflict:
                    was_conflict = True
                    conflict_info[state].append(shift_reduce_fail(shift_decision = shift_reduce_conflict, reduce_decision = table[state,symbol], conflict_symbol = conflict_symbol))
                if reduce_reduce_conflict:
                    was_conflict = True
                    conflict_info[state].append(reduce_reduce_fail(reduce_decision1 = reduce_reduce_conflict, reduce_decision2 = table[state,symbol], conflict_symbol = conflict_symbol))
        return table, conflict_info, was_conflict

class Fail:
    def __init__(self, error_message):
        self.error_message = error_message

    def __repr__(self):
        return self.error_message
                
class automaton_fail(Fail):
    def __init__(self, fail_type, decision1, decision2, conflict_symbol):
        self.decision1 = decision1
        self.decision2 = decision2
        self.conflict_symbol = conflict_symbol
        self.error_message = "Conflicto {3} entre las decisiones {0} y {1} para el símbolo {2}".format(decision1, decision2 , conflict_symbol, fail_type)

class shift_reduce_fail(Fail):
    def __init__(self, shift_decision, reduce_decision, conflict_symbol):
        super().__init__(fail_type = "shift-reduce", decision1= shift_decision, decision2 = reduce_decision, conflict_symbol = conflict_symbol)

class reduce_reduce_fail(Fail):
    def __init__(self, reduce_decision1, reduce_decision2, conflict_symbol):
        super().__init__(fail_type = "reduce-reduce", decision1= reduce_decision1, decision2 = reduce_decision2, conflict_symbol = conflict_symbol)

class Action:
    def __init__(self, table_tuple, response, label):
        self.table_tuple = table_tuple
        self.response = response
        self.label = label

    def __repr__(self):
        return self.label

class reduce(Action):
    pass

class shift(Action):
    pass

class accept(Action):
    pass

class error(Action, Fail):
    pass

