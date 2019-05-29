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

    def __init__(self, label, setOfItems, grammar:GrammarClass):
        self.label = label
        self.setOfItems = setOfItems
        self.kernel_items = [x for x in setOfItems if x.isKernel]
        self.grammar =grammar

    def extend(self, otherList):
        self.setOfItems.extend(otherList)
        self.kernel_items.extend(x for x in otherList if x.isKernel)

    def __eq__(self, other, notLookLabel = False):
        if not notLookLabel:
            return self.kernel_items == other.kernel_items
        if len(self.kernel_items) != len(other.kernel_items): return False
        for x in self.kernel_items:
            founded = False
            for y in other.kernel_items:
                if x.__eq__(y,notLookLabel):
                    founded = True
                    break
            if not founded: return False
        return True

    def __repr__(self):
        l = []
        for x in self.setOfItems:
            l.append (repr(x))
        return repr(self.label) + ": " + repr(l) 


    def __hash__(self):
        toReturn = 0
        for item in self.kernel_items:            
            toReturn += hash(item)
        return toReturn 

class Item(state):
    def __init__(self, label, grammar:GrammarClass, nonTerminal, point_Position, production):
        super().__init__(label, grammar)
        self.nonTerminal = nonTerminal
        self.production = production
        self.point_Position = point_Position * (self.production !=tuple([Epsilon()]))
        self.isKernel = not self.point_Position is 0 or grammar.initialSymbol == self.nonTerminal 

    def __repr__(self):
        toReturn = repr(self.nonTerminal) + "->" + repr(self.production[:self.point_Position]) + "." + repr (self.production[self.point_Position:])
        if self.label: toReturn += ", " + repr(self.label)
        return toReturn

    def __hash__(self):
        return hash(self.nonTerminal) + hash(self.point_Position) + hash(self.production)
    
    def __eq__(self, other, notLookLabel = False):
        return self.production == other.production and self.point_Position == other.point_Position and self.nonTerminal == other.nonTerminal and (self.label == other.label or notLookLabel)