class GrammarSymbol:
    def __init__(self, name):
        self.name = name

    def __hash__(self):
        return hash (self.name)

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        if other is None: return False        
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
        if isinstance(nonTerminals, list): 
            self.nonTerminals = {NoTerminal(x): [] for x in nonTerminals}
        else:
            self.nonTerminals = nonTerminals
        self.initialSymbol = NoTerminal(name = initialSymbol)
        self.LeftRecSet = []
        self.isRegular = True

    def __repr__(self):
        toReturn = ""
        for x in self.nonTerminals:
            toReturn += repr(x) + ' -> '
            passed = False
            for prod in self.nonTerminals[x]:
                if passed:
                    toReturn += ' |'
                for symbol in prod:
                    toReturn += ' ' +repr(symbol)
                passed = True

            toReturn += '\n'

        return toReturn[:-1]

    def addProduction(self, noTerminal, *productions):
        for production in productions:
            self.nonTerminals[NoTerminal(noTerminal)].append(tuple([NoTerminal(name = x) if NoTerminal(x) in self.nonTerminals else Terminal(x) for x in production]))
            if noTerminal == production[0]: self.LeftRecSet.append(NoTerminal(noTerminal))
            self.isRegular = not noTerminal in production[:-1]
