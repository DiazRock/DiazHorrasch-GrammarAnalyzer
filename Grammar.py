class GrammarSymbol:
    def __init__(self, name):
        self.name = name

class Terminal(GrammarSymbol):
    pass

class NoTerminal(GrammarSymbol):
    def __init__(self, name, productionsBodies):
        super().__init__(name)
        self.productionsBodies = productionsBodies
    
class Grammar:
    def __init__(self, initialSymbol, terminals, nonTerminals):
        self.terminals = terminals
        self.nonTerminals = nonTerminals
        self.initialSymbol = initialSymbol