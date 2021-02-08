from GrammarAnalyzer.Grammar import *
from GrammarAnalyzer.Automaton import *

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

def analize_is_regular(G):
    for n in G.nonTerminals:
        for prod in G.nonTerminals[n]:
            for x in prod[:-1]:
                if isinstance(x, NoTerminal):
                    return False
    return True


def deleteInmediateLeftRecusrive(G:GrammarClass):
    nonRecusriveSet = {}
    for x in G.LeftRecSet:
        newNotTerminal = NoTerminal(x.name + "'")
        toInsert = {x:[], newNotTerminal: [()]}
        for prod in G.nonTerminals[x]:
            if prod[0] == x:
                #if prod == (Epsilon(), ):
                #    toInsert[newNotTerminal].append(((), newNotTerminal))
                #else:
                toInsert[x].append((*prod[1:],newNotTerminal))
                toInsert[newNotTerminal].append((*prod[1:],newNotTerminal))
            else:
                if not (len(prod) == 1 and prod[0] ==  Epsilon()):
                    toInsert[x].append((*prod, newNotTerminal))
        nonRecusriveSet.update(toInsert)
    G.nonTerminals.update(nonRecusriveSet)
    G.isRegular = analize_is_regular(G)
    

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
    generable = { x: True for x in grammar.terminals + [Epsilon()] }
    generable.update( { x: False for x in grammar.nonTerminals } )
    reachable = { x: False for x in grammar.terminals }
    reachable.update( { x : False if not x == grammar.initialSymbol else True for x in grammar.nonTerminals } )
    DFS(grammar, grammar.initialSymbol, { x: False if not x ==  grammar.initialSymbol else True for x in grammar.nonTerminals }, reachable, generable)
    not_reachable_prod_set = [x for x in grammar.terminals if not reachable[x]] + [x for x in grammar.nonTerminals if not reachable[x]]
    not_generable_prod_set = [x for x in grammar.nonTerminals if not generable[x]]
    new_grammar = GrammarClass ( initialSymbol = grammar.initialSymbol.name, terminals =[terminal.name for terminal in grammar.terminals if reachable[terminal] ], nonTerminals = [X.name for X in grammar.nonTerminals if reachable[X] and generable[X]] )
    for x in new_grammar.nonTerminals:
        for prod in grammar.nonTerminals[x]:
            if notProp(reachable, prod) or notProp (generable, prod):
                continue
            new_grammar.addProduction(x.name, [symbol.name for symbol in prod])

    return  not_generable_prod_set, not_reachable_prod_set, new_grammar

def notProp(setProp, prod):
    for x in prod:
        if not setProp[x]: return True
    return False

def DFS(grammar, current, visited, reachable, generable):
    for prod in grammar.nonTerminals [current]:
        allgenerable = True
        for symbol in prod:
            reachable[symbol] = True
            if isinstance(symbol, NoTerminal) and not visited[symbol]:
                visited[symbol] = True
                DFS(grammar, symbol, visited, reachable, generable)
            allgenerable = generable[symbol]
        generable[current]= generable[current] or allgenerable

def delete_unit_productions(grammar: GrammarClass):
    changed = False
    initial = True
    while changed or initial:
        initial = changed = False
        for x in grammar.nonTerminals:
            for prod in grammar.nonTerminals[x]:
                if len(prod) == 1 and isinstance(prod[0], NoTerminal):
                    changed = True
                    grammar.nonTerminals[x] += grammar.nonTerminals[prod[0]]
                    grammar.nonTerminals.pop(prod[0])

def convert_grammar_to_automaton(grammar: GrammarClass):
    refactorization (grammar )
    automaton_states = {x: state(label = x) for x in grammar.nonTerminals}

    automaton = Automaton(states = list(automaton_states.values()), 
                          symbols = set(), 
                          initialState = automaton_states[grammar.initialSymbol],
                          FinalStates = set(), 
                          transitions = {})
    for nonTerminal in automaton_states:
        for prod in grammar.nonTerminals[nonTerminal]:
            symbol = ''
            state_input = None
            if isinstance(prod[-1], NoTerminal):
                if not len(prod) == 1:
                    for x in prod[:-1]:
                        symbol += repr(x)
                    automaton.symbols.update( {symbol} )
                else:
                    symbol = Epsilon()
                state_input = automaton_states[prod[-1]]
            else:
                for x in prod:
                    symbol += repr( x )
                if not prod == tuple([Epsilon() ] ):
                    state_input = state( label = NoTerminal (automaton_states[nonTerminal].label.name + "_" + str(len(automaton.states))) )
                    automaton.FinalStates.update({state_input})
                    automaton.states.append( state_input )                    
                    automaton.symbols.update({symbol})
                else:
                    automaton.FinalStates.update( {automaton_states[nonTerminal]} )
                    continue

            automaton.transitions[automaton_states[nonTerminal], symbol] = \
                automaton.transitions.get((automaton_states[nonTerminal], symbol), ()) + (state_input, )
    
    return automaton

def from_epsilonNFA_to_DFA(automaton: Automaton):

    initial, isFinalState = epsilon_closure(automaton,automaton.initialState)
    DFA_states = [initial]
    DFA_transitions = {}
    queue = [initial]
    finalStates = []

    if isFinalState: 
        finalStates.append(initial)
    while queue:
        current_state = queue.pop()        
        for symbol in automaton.symbols:             
            state_to_enqueue = move(automaton, current_state, symbol) 
            if state_to_enqueue.label:
                state_to_enqueue, isFinalState = epsilon_closure(automaton, state_to_enqueue)
                DFA_transitions.update({(current_state, symbol): state_to_enqueue})
                if not state_to_enqueue in DFA_states:                    
                    queue.append(state_to_enqueue)
                    DFA_states.append(state_to_enqueue)
                    if isFinalState: 
                        finalStates.append(state_to_enqueue)
    

    return Automaton(states = DFA_states, symbols = automaton.symbols, initialState = initial, FinalStates = finalStates, transitions = DFA_transitions)
    
def move(automaton, current_state, symbol):
    superState = state(label =tuple())
    setStates = current_state.label
    for s in setStates:                
        if (s, symbol ) in automaton.transitions:
            superState.label += tuple (automaton.transitions[s, symbol])
    return superState

def epsilon_closure(automaton: Automaton, superState:state):    
    e_closure = state(label = tuple([superState]) if isinstance(superState.label, NoTerminal) else superState.label) 
    stack = list (e_closure.label)
    isFinalState = False
    while stack:
        current_state = stack.pop()
        if not isFinalState:
            isFinalState = current_state in automaton.FinalStates
        if (current_state, Epsilon() ) in automaton.transitions:
            for u in automaton.transitions[ current_state, Epsilon()]:
                if not u in e_closure.label:
                    e_closure.label += tuple( [u] )
                    stack.append(u)
    return e_closure , isFinalState
    
def regular_expresion_from_automaton(automaton: Automaton):
    dp = initialize_table(automaton)
    for k in range(len(automaton.states )):
        current_dp = dp.copy()
        for i in range(len( automaton.states) ):
            for j in range( len(automaton.states) ):
                state_i, state_j, state_k = automaton.states[i],automaton.states[j], automaton.states[k]
                dp[state_i, state_j] += current_dp[state_i,state_k].concat(current_dp[state_k,state_k].toClosure()).concat(current_dp[state_k, state_j])

    expr = emptyRegExp()
    for i in range(len(automaton.states)):        
        expr += dp[automaton.states[0], automaton.states[i]]
    return expr

def initialize_table(automaton: Automaton):
    table_toReturn = {(state_i, state_j): epsilonRegExp() for state_i in automaton.states for state_j in automaton.states}
    for state_out in automaton.states:
        for symbol in automaton.symbols:
            if (state_out,symbol) in automaton.transitions:
                state_in = automaton.transitions[state_out, symbol]
                if isinstance (table_toReturn[state_out, state_in], epsilonRegExp):
                    table_toReturn[state_out, state_in] = regularExpr(isLeaf=True, symbol= symbol)
                else:
                    table_toReturn[state_out, state_in] += regularExpr(isLeaf=True, symbol = symbol)
    return table_toReturn

def brzozowski_dfa_to_regexp(automaton: Automaton):
    B = [ epsilonRegExp() if s in automaton.FinalStates else emptyRegExp() for s in automaton.states]
    A = {(si,sj): emptyRegExp() for si in automaton.states for sj in automaton.states}
    for s in automaton.states:
        for symbol in automaton.symbols:
            if (s, symbol) in automaton.transitions:
                A[s, automaton.transitions[s, symbol]] += regularExpr(symbol= symbol, isLeaf = True)
    for n in range(len(automaton.states) - 1, -1, -1):
        B[n] = A[automaton.states[n], automaton.states[n]].toClosure().concat(B[n])
        for j in range(n):
            A[automaton.states[n], automaton.states[j]] = A[automaton.states[n], automaton.states[n]].toClosure().concat(A[automaton.states[n], automaton.states[j]])
        for i in range(n):
            B[i] += A[automaton.states[i], automaton.states[n]].concat(B[n])
            for j in range(n):
                A[automaton.states[i], automaton.states[j]] += A[automaton.states[i], automaton.states[n]].concat(A[automaton.states[n], automaton.states[j]])
        
    return B[0]

