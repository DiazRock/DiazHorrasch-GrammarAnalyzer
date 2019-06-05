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

    
    def add_transition(self, state_out, symbol, state_in):
        if not (state_out, symbol) in self.transitions :
            self.transitions.update({(state_out, symbol) : state_in})
        else:
            self.transitions[state_out, symbol] =state(label = [self.transitions[state_out, symbol]] + [state_in], grammar= state_out.grammar)  
    


class state:
    def __init__(self, label, grammar: GrammarClass):
        self.label = label
        self.grammar = grammar

    def __equal__(self,other):
        return self.label == other.label
    
    def __hash__(self):
        return hash(self.label)

    def __repr__(self):
        return repr(self.label)


class canonical_State(state):    

    def __init__(self, label, setOfItems, grammar:GrammarClass):
        self.label = label
        self.setOfItems = setOfItems
        self.kernel_items = [x for x in setOfItems if x.isKernel]
        self.grammar =grammar

    def extend(self, otherList):
        self.setOfItems.extend(otherList)
        self.kernel_items.extend(x for x in otherList if x.isKernel)

    def __eq__(self, other):
        return self.kernel_items == other.kernel_items

    def equal_looksahead(self, other):
        if not self.kernel_items and not other.kernel_items: return True
        if self.kernel_items != other.kernel_items: return False
        for x in self.kernel_items:
            for y in other.kernel_items:
                if x==y and x.label!=y.label: return False
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
    
    def __eq__(self, other):
        return self.production == other.production and self.point_Position == other.point_Position and self.nonTerminal == other.nonTerminal

    def equal_look_ahead(self,other):
        return self.label == other.label


class Tree:
    def __init__(self, label, children = [], parent = None):
        self.label = label
        self.children = children
        self.parent = parent

    def append(self, child):
        self.children.append(child)

class regularExpr:
    def __init__(self, left = None, right = None, isClosure = False, isUnion = False, isLeaf = False, symbol = None):
        if isLeaf:
            self.left=self.right =None            
            self.isUnion = False
            self.symbol = symbol            
        else:
            self.left = left
            self.right = right
            self.isUnion = isUnion
            if self.isUnion:
                self.symbol = self.left.symbol + '|' + self.right.symbol
            else:
                self.symbol = self.left.symbol + self.right.symbol

        self.isClosure = isClosure            
        if self.isUnion or self.isClosure:
            self.symbol = '(' + self.symbol + ')'
        if self.isClosure and not(self.symbol[-1] == '*'):
            self.symbol += '*'            

    def __repr__(self):
        return repr(self.symbol)
    def toClosure(self):
        self.isClosure = True
        if not self.symbol[-1] == '*' and not self.symbol == '':
            self.symbol += '*'
