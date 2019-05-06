from Grammar import *

def CalculateFirst(G:GrammarClass):
    Firsts = {x:x.name for x in G.terminals}
    Firsts.update({X:{} for X in G.nonTerminals})
    changed = False
    while(changed or not Firsts[G.initialSymbol]):
        for X in G.nonTerminals:
            for prod in X.productionsBodies:
                if prod == ProductionBody(Epsilon):
                   changed = Add(Firsts[X], [Epsilon])
                else:
                    allEpsilon = True
                    for x in prod:                    
                        changed = Add(Firsts[X], Firsts[x])
                        if not Epsilon in Firsts[x]: break
                    if allEpsilon : changed = Add(Firsts[X], [Epsilon])        
    return Firsts
def CalculateFollow(G:GrammarClass, Firsts):
    Follows = {X:{} for X in G.nonTerminals}
    Follows[G.initialSymbol].Add(FinalSymbol)
    
    return Follows
def Add(First, terminalList):
    before = First.copy()
    First += terminalList
    return before != First