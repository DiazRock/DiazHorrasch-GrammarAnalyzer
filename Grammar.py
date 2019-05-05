class GrammarSymbol:
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return self.name
class Terminal(GrammarSymbol):
    pass

class NoTerminal(GrammarSymbol):
    def __init__(self, name, *productionsBodies):
        super().__init__(name)
        self.productionsBodies = productionsBodies
    
class GrammarClass:
    def __init__(self, initialSymbol, terminals, nonTerminals):
        self.terminals = terminals
        self.nonTerminals = nonTerminals
        self.initialSymbol = initialSymbol
    def __repr__(self):
        return "S: {0}\nT: {1}\nNT: {2}".format(self.initialSymbol, self.terminals, self.nonTerminals)
    def __getitem__(self, index):
        if index is self.initialSymbol : return self.initialSymbol
        if index in self.nonTerminals : return self.nonTerminals[index]
        if index in self.terminals : return self.terminals[index]
        return False
class ProductionBody:
    def __init__(self, *grammarSymbols):
        self.grammarSymbols = grammarSymbols