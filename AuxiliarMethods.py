from Grammar import *


def CalculateFirst(G:GrammarClass):
    Firsts = {x:{x} for x in G.terminals}
    Firsts.update({X:set() for X in G.nonTerminals})
    Firsts.update({specialChar():{specialChar()} for specialChar in (Epsilon, FinalSymbol)})   
    changed = False
    while(changed or not Firsts[G.initialSymbol]):
        for X in G.nonTerminals:            
            for prod in G.nonTerminals[X]:                          
                if len(prod) ==1 and prod[0] == Epsilon():                    
                   changed = Add(Firsts[X], [Epsilon()])
                else:
                    allEpsilon = True
                    for x in prod:
                        changed = Add(Firsts[X], Firsts[x])
                        if not Epsilon() in Firsts[x]: 
                            allEpsilon = False
                            break                            
                    if allEpsilon : changed = Add(Firsts[X], [Epsilon()])

#Recordar que los elementos de los First son de tipo GrammarSymbol.
    return Firsts
    
def CalculateFollow(G:GrammarClass, Firsts):
    Follows = {X:set() for X in G.nonTerminals}

    changed = False    
    while(changed or not Follows[G.initialSymbol]):
        Follows[G.initialSymbol].update({FinalSymbol()})
        changed = False    
        for X in G.nonTerminals:            
            for prod in G.nonTerminals[X]:
                for i in range(len(prod)):
                    if isinstance(prod[i], NoTerminal):
                        firstBody = FirstsForBody(prod[i + 1:], Firsts)
                        changed = changed or Add(Follows[prod[i]], [x for x in firstBody if x != Epsilon()])
                        
                        if(Epsilon() in firstBody or i == len(prod) - 1):                            
                            changed = changed or Add(Follows[prod[i]], Follows[X])                            
    return Follows

def FirstsForBody(productionBody, Firsts):    
    result = set()
    allEpsilon = True and productionBody
    for x in productionBody:
        result.update({y for y in Firsts[x] if y != Epsilon()})
        if Epsilon() not in Firsts[x]:
            allEpsilon = False
            break
    if allEpsilon:
        result.update ({Epsilon()})
    return result

def Add(First, terminalList):
    before = First.copy()    
    First.update(terminalList)    
    return before != First

def deleteInmediateLeftRecusrive(G:GrammarClass):
    nonRecusriveSet = {}
    for x in G.LeftRecSet:
        newNotTerminal = NoTerminal(x.name + "'")
        toInsert = {x:[], newNotTerminal: [tuple([Epsilon()])]}
        for prod in G.nonTerminals[x]:
            if prod[0] == x:
                toInsert[newNotTerminal].append((*prod[1:],newNotTerminal))
            else:
                if not (len(prod) == 1 and prod[0] ==  Epsilon()):
                    toInsert[x].append((*prod, newNotTerminal))
        nonRecusriveSet.update(toInsert)
    G.nonTerminals.update(nonRecusriveSet)

def refactorization(G:GrammarClass):
    while True:            
        commonPrefixForNonTerminal = {}
        for X in G.nonTerminals:
            G.nonTerminals[X], temp = refactorNonTerminal(X, G.nonTerminals[X])
            if not temp: return 
            commonPrefixForNonTerminal.update(temp)
        G.nonTerminals.update(commonPrefixForNonTerminal)                   
            
def refactorNonTerminal(X: NoTerminal, productions):
    
    preffixForProduction = {}
    i = 0
    for prod in productions:
        preffixForProduction.update({prod:([],NoTerminal("{0}{1}".format(X.name,i)))})
        i+=1
    
    
    for i in range(len(productions)):
        for j in range(i+1,len(productions)):
            commonPref = commonPreffix(productions[i], productions[j])
            representativeNonTerminal = preffixForProduction[productions[j]][1]
            if len(preffixForProduction[productions[i]][0]) < len(commonPref):
                preffixForProduction[productions[i]] = (commonPref, representativeNonTerminal)
                
            preffixForProduction[productions[j]] = (commonPref, representativeNonTerminal)
    
    newProductionsForX = []
    newNonTerminals = {}
    for prod in productions:
        currentRepresentativeNonTerminal = preffixForProduction[prod][1]
        if preffixForProduction[prod][0]:
            toInsert = prod[len(preffixForProduction[prod][0]):] if prod[len(preffixForProduction[prod][0]):] else tuple([Epsilon()])
            if not currentRepresentativeNonTerminal in newNonTerminals:
                newNonTerminals.update({currentRepresentativeNonTerminal: [toInsert]})
            else:
                newNonTerminals[currentRepresentativeNonTerminal].append(toInsert)
                newProductionsForX.append(preffixForProduction[prod][0] + tuple([currentRepresentativeNonTerminal]))
        else:
            newProductionsForX.append(prod)
    return newProductionsForX, newNonTerminals
        

def commonPreffix(prod1, prod2):
    for i in range(min(len(prod1), len(prod2))):
        if(prod1[i] != prod2[i]):
            return prod1[:i]
    return prod1[:min(len(prod1), len(prod2))]        
