from Grammar import *
from Automaton import *

def CalculateFirst(G:GrammarClass):
    Firsts = {x:{x} for x in G.terminals}
    Firsts.update({X:set() for X in G.nonTerminals})
    Firsts.update({specialChar():{specialChar()} for specialChar in (Epsilon, FinalSymbol)})   
    changed = False
    while(changed or not Firsts[G.initialSymbol]):
        for X in G.nonTerminals:            
            for prod in G.nonTerminals[X]:                          
                if tuple(prod) == tuple([Epsilon()]):                    
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
    changed = True
    while changed:
        changed = False
        for X in G.nonTerminals:
            G.nonTerminals[X], temp = refactorNonTerminal(X, G.nonTerminals[X])
            if temp : changed = True
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
            if len(preffixForProduction[productions[j]][0]) < len(commonPref):
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


def cleanGrammar(grammar:GrammarClass):
    generable = {x:True for x in grammar.terminals}
    generable.update({x:False for x in grammar.nonTerminals})
    reachable = {x:False for x in grammar.terminals}
    reachable.update({x:False for x in grammar.nonTerminals})
    DFS(grammar.initialSymbol, {x:False if not x ==  grammar.initialSymbol else True for x in grammar.nonTerminals}, reachable, generable)
    not_reachable_prod_set = {}
    not_generable_prod_set = {}
    for x in grammar.nonTerminals:
        for prod in grammar.nonTerminals[x]:
            was_generable_conflict = False
            was_reachable_conflict = False
            for symbol in prod:
                if not generable[x]:
                    if not was_generable_conflict:
                        not_generable_prod_set.update({(x,prod): [symbol]})
                        was_generable_conflict = True
                    else:
                        not_generable_prod_set[x,prod].append(symbol)
                    
                if not reachable[x]:
                    if not was_reachable_conflict:
                        was_reachable_conflict = True
                        not_reachable_prod_set.update({(x,prod) : [symbol]})
                    else:
                        not_reachable_prod_set[(x,prod)].append(symbol)
            if was_generable_conflict or was_reachable_conflict:
                grammar.nonTerminals[x].remove(prod)
                for symbol in not_reachable_prod_set[x,prod]:
                    if isinstance(symbol, Terminal):
                        grammar.terminals.remove(symbol)
                    else:
                        grammar.nonTerminals.pop(symbol)
                for symbol in not_generable_prod_set[x,prod]:
                    if isinstance(symbol, Terminal):
                        grammar.terminals.remove(symbol)
                    else:
                        grammar.nonTerminals.pop(symbol)

    return  not_generable_prod_set, not_reachable_prod_set                   
                

def DFS(current, visited, reachable, generable):
    for prod in current.productions:
        allgenerable = True
        for symbol in prod:
            reachable[symbol] = True
            if isinstance(symbol, NoTerminal) and not visited[symbol]:
                visited[symbol] = True
                DFS(symbol, visited, reachable, generable)
            allgenerable = generable[symbol]
    generable[current] = allgenerable

def delete_unit_productions(grammar: GrammarClass):
    changed = False
    initial = True
    while changed or initial:
        initial = changed = False
        for x in grammar.nonTerminals:
            for prod in grammar.nonTerminals[x]:
                if len(prod) is 1 and isinstance(prod[0], NoTerminal):
                    changed = True
                    grammar.nonTerminals[x] += grammar.nonTerminals[prod[0]]
                    grammar.nonTerminals.pop(prod[0])

def convert_grammar_to_automaton(grammar: GrammarClass):
    refactorization(grammar)
    automaton_states = {x: state(label = x, grammar = grammar) for x in grammar.nonTerminals}
    for state in automaton_states:
        state.label = [state]
    automaton = Automaton(states = list(automaton_states.values()), symbols = set(), initialState = automaton_states[grammar.initialSymbol], FinalStates = set(), transitions = {})
    for current_state in automaton.states:
        for prod in grammar.nonTerminals[current_state.label]:
            string = ''
            if isinstance(prod[-1], NoTerminal):
                if not len(prod) == 1:
                    for x in prod[:-1]:
                        string += repr(x)
                else:
                    string = Epsilon()            
                automaton.symbols.update({string})                
                automaton.add_transition(state_out = current_state, symbol= string, state_in =automaton_states[prod[-1]])
            else:
                for x in prod:
                    string += repr(x)            
                automaton.FinalStates.update({current_state})
                if not prod == tuple([Epsilon()]):
                    automaton.add_transition(state_out = current_state, symbol = string, state_in = current_state)
                    automaton.symbols.update({string})
    return automaton

def from_epsilonNFA_to_DFA(automaton: Automaton):
    initial, isFinalState = epsilon_closure(automaton,automaton.initialState)
    DFA_states = {epsilon_closure(automaton,automaton.initialState)}
    DFA_transitions = {}
    queue = [initial]
    finalStates = [] 
    while queue:
        current_state = queue.pop()
        if isFinalState: finalStates.append(current_state)
        for symbol in automaton.symbols:
            state_to_enqueue, isFinalState = epsilon_closure(automaton,move(automaton, current_state, symbol))
            before = len(DFA_states)
            DFA_states.update({state_to_enqueue})
            if not before == len(DFA_states):
                queue.append(state_to_enqueue)
            DFA_transitions.update({(current_state, symbol): state_to_enqueue})

    return Automaton(states = list(DFA_states),symbols = automaton.symbols, initialState = initial, FinalStates = finalStates, transitions = DFA_transitions)
    
def move(automaton, current_state, symbol):
    superState = state(label =[ ], grammar = current_state.grammar)
    for s in current_state:
        if (s,symbol) in automaton.transitions:
            for i in automaton.transitions[s, symbol]:
                for x in i.label:
                    superState.label.append(x)
    return superState
def epsilon_closure(automaton: Automaton, superState:state):
    e_closure = stack = [state_in_super for state_in_super in superState.label]
    isFinalState = False
    while stack:
        current_state = stack.pop()
        isFinalState = current_state in automaton.FinalStates
        for u in automaton.transitions[current_state, Epsilon()].label:
            if not u in e_closure:
                e_closure.append(u)
                stack.append(u)
    return e_closure, isFinalState
    
def regular_expresion_from_automaton(automaton: Automaton):
    dp = initialize_table(automaton)
    for k in range(len(automaton.states)):
        for i in range(len(automaton.states)):
            for j in range(len(automaton.states)):
                state_i, state_j, state_k = automaton.states[i],automaton.states[j], automaton.states[k]
                dp[state_i, state_j] = regularExpr(isUnion=True, left = dp[state_i,state_j], right= regularExpr(left= dp[state_i,state_k], right= regularExpr(left=dp[state_k,state_k].toClosure(), right= dp[k,j])))

    expr = regularExpr(isLeaf=True, symbol= '')
    for i in range(len(automaton.states)):
        if(not dp[automaton.states[0],automaton.states[i]].symbol == ''):
            expr = regularExpr(left = expr, right=dp[automaton.states[0], automaton.states[i]], isUnion= True)
    return expr

def initialize_table(automaton: Automaton):
    table_toReturn = {(state_i, state_j): regularExpr(isLeaf=True, symbol='') for state_i in automaton.states for state_j in automaton.states}
    for state_out in automaton.states:
        for symbol in automaton.symbols:
            if (state_out,symbol) in automaton.transitions:
                state_in = automaton.transitions[state, symbol]
                if table_toReturn[state_out, state_in].symbol == '':
                    table_toReturn[state_out, state_in] = regularExpr(isLeaf=True, symbol= symbol)
                else:
                    table_toReturn[state_out, state_in] = regularExpr(isUnion=True, left = table_toReturn[state_out, state_in], right= regularExpr(isLeaf=True, symbol = symbol))
    return table_toReturn