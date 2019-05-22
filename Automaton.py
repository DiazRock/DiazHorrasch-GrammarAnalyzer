from Grammar import GrammarClass, Epsilon, NoTerminal
class Automaton:
    def __init__(self, states, symbols, initialState, FinalStates, transitions):
        self.states = states
        self.symbols = symbols
        self.initialState = initialState
        self.FinalStates = FinalStates
        self.transitions = transitions
        self.currentState = initialState

    def trans(self, inputSymbol):
        return self.transitions[(self.currentState, inputSymbol)]        

    def accept(self):
        return self.currentState in self.FinalStates

class state:
    def __init__(self, label, grammar: GrammarClass):
        self.label = label
        self.grammar = grammar

    def __equal__(self,other):
        return self.label == other.label


class canonical_State(state):    

    def __init__(self, setOfItems, grammar:GrammarClass):
        self.setOfItems = setOfItems
        self.kernel_items = [x for x in setOfItems if x.isKernel]
        self.grammar =grammar

    def extend(self, otherList):
        self.label.extend(otherList)
        self.kernel_items.extend(x for x in otherList if x.isKernel)

    def __eq__(self, other):
        return hash(self) is hash(other)



    def __hash__(self):
        toReturn = 0
        for item in self.kernel_items:            
            toReturn += item(hash)
        return toReturn 

class item(state):
    def __init__(self, label, grammar:GrammarClass, nonTerminal, point_Position, production):
        super().__init__(label, grammar)
        self.nonTerminal = nonTerminal
        self.production = production
        self.point_Position = point_Position * (len (self.production) == 1 and self.production[0] !=Epsilon())
        self.isKernel = not self.point_Position is 0 or grammar.initialSymbol == self.nonTerminal 

    def __repr__(self):
        return self.nonTerminal + "->" + self.production[:self.point_Position] + "." + self.production[self.point_Position:]
    
    def __hash__(self):
        return hash(self.nonTerminal) + hash(self.point_Position) + hash(self.production)