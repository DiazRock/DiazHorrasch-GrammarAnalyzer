class GrammarSymbol:
    def __init__(self, name):
        self.name = name

    def __hash__(self):
        return hash (self.name)

    def __repr__(self):
        return self.name

    def __eq__(self, other):        
        return self.name == other.name

class Terminal(GrammarSymbol):
    pass

class Epsilon(Terminal):
    def __init__(self):
        super().__init__(name="œ")

class FinalSymbol(Terminal):
    def __init__(self):
        super().__init__(name="$")
        
class NoTerminal(GrammarSymbol):
    pass
            
class GrammarClass:
    def __init__(self, initialSymbol, terminals, nonTerminals):
        self.terminals = {Terminal(x) for x in terminals}
        self.nonTerminals = {NoTerminal(x): [] for x in nonTerminals}
        self.initialSymbol = NoTerminal(name = initialSymbol)
        
    def __repr__(self):
        return "S: {0}\nT: {1}\nNT: {2}".format(self.initialSymbol, self.terminals, self.nonTerminals)

    def addProduction(self, noTerminal, *productions):
        for production in productions:            
            self.nonTerminals[NoTerminal(noTerminal)].append([NoTerminal(name = x) if NoTerminal(x) in self.nonTerminals else Terminal(x) for x in production])
                    

