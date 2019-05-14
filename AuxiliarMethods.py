from Grammar import *

def CalculateFirst(G:GrammarClass):
    Firsts = {x:{x} for x in G.terminals}
    Firsts.update({X:set() for X in G.nonTerminals})   
    changed = False
    while(changed or not Firsts[G.initialSymbol]):        
        for X in G.nonTerminals:            
            for prod in G.nonTerminals[X]:                          
                if prod == [Epsilon()]:                    
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
        for X in G.nonTerminals:            
            for prod in G.nonTerminals[X]:
                for i in range(len(prod)):                                        
                    if str(type (prod[i])) == "<class 'Grammar.NoTerminal'>":                                                
                        firstBody = FirstsForBody(prod[i + 1:], Firsts)
                        changed = Add(Follows[prod[i]], [x for x in firstBody if x != Epsilon()])
                        
                        if(Epsilon() in firstBody or i == len(prod) - 1):                            
                            changed = Add(Follows[prod[i]], Follows[X])
                            
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