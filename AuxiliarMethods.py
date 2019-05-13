from Grammar import *

def CalculateFirst(G:GrammarClass):
    Firsts = {x:{x.name} for x in G.terminals}
    Firsts.update({X:set() for X in G.nonTerminals})
    
    changed = False
    while(changed or not Firsts[G.initialSymbol]):        
        for X in G.nonTerminals:
            for prod in X.productionsBodies:                          
                if prod == [Epsilon()]:
                   changed = Add(Firsts[X], [Epsilon()])
                else:
                    allEpsilon = True
                    for x in prod:
                        print(X, x, sep = "\t")                        
                        changed = Add(Firsts[X], Firsts[x])
                        if not Epsilon() in Firsts[x]: 
                            allEpsilon = False
                            break
                    if allEpsilon : changed = Add(Firsts[X], [Epsilon()])        
    return Firsts
    
def CalculateFollow(G:GrammarClass, Firsts):
    Follows = {X:set() for X in G.nonTerminals}
    Follows[G.initialSymbol] += [FinalSymbol()]
    changed = False
    while(changed or Follows[G.initialSymbol] == [FinalSymbol()]):
        for X in G.nonTerminals:
            for prod in X.productionsBodies:
                for i in range(len(prod)):
                    if prod[i] is NoTerminal:
                        firstBody = FirstsForBody(prod[i:], Firsts)
                        changed = Add(Follows[prod[i]], [x for x in firstBody and x != Epsilon()])
                        if(Epsilon() in firstBody or i == len(prod) - 1):
                            changed = Add(Follows[prod[i]], Follows[X])

    return Follows

def FirstsForBody(productionBody, Firsts):
    result = set()
    allEpsilon = True
    for x in productionBody:
        result.union (Firsts[x])
        if Epsilon() not in Firsts[x]:
            allEpsilon = False
            break
    if allEpsilon:
        result += Epsilon()
    return result

def Add(First, terminalList):
    before = First.copy()
    print(First, terminalList, sep = "\t")
    First.update(terminalList)
    print(First, before, First != before, sep = "\t")    
    return before != First