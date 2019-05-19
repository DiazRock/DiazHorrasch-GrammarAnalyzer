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
    commonPrefixForNonTerminal = {}
    for nonTerminal in G.nonTerminals:
        for i in range(min(len(prod) for prod in G.nonTerminals[nonTerminal]),0,-1):
            isCommonPrefix = False
            for j in range(len(G.nonTerminals[nonTerminal]) - 1):
                if G.nonTerminals[nonTerminal][j][:i] != G.nonTerminals[nonTerminal][j + 1][:i]:
                    isCommonPrefix = False
                    break
                isCommonPrefix = True
            if isCommonPrefix:
                commonPrefixForNonTerminal.update({nonTerminal:G.nonTerminals[nonTerminal][0][:i]})

    if not commonPrefixForNonTerminal: return False
    for nonTerminal in commonPrefixForNonTerminal:
        for prod in G.nonTerminals[nonTerminal]:
            refactoredNonTerminal = NoTerminal(nonTerminal.name + "'")
            G.nonTerminals.update({refactoredNonTerminal:[]})
            if prod[:len(commonPrefixForNonTerminal[nonTerminal])] == commonPrefixForNonTerminal[nonTerminal]:
                G.nonTerminals[refactoredNonTerminal].append((*prod[len(commonPrefixForNonTerminal[nonTerminal]):]))     
                G.nonTerminal[nonTerminal].remove(prod)
        
        G.nonTerminals[nonTerminal].append((*prod[:len(commonPrefixForNonTerminal[nonTerminal])], refactoredNonTerminal))
    return True               
            
