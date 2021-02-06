from GrammarAnalyzer.AuxiliarMethods import *
from GrammarAnalyzer.Automaton import *

class Parser:
	def __init__(self, grammar):
		self.inputSymbols = [FinalSymbol()] + grammar.terminals


class PredictiveParser(Parser):
	def __init__(self, grammar):
		super().__init__(grammar)
		self.Firsts = CalculateFirst(grammar)
		for productions in grammar.nonTerminals.values():
			for prod in productions:
				self.Firsts.update({prod: FirstsForBody(prod, self.Firsts)})        
		self.Follows = CalculateFollow(grammar,self.Firsts)
		

class LL_Parser(PredictiveParser):
	def __init__(self, grammar):
		super().__init__(grammar)
		self.initialSymbol = grammar.initialSymbol
		self.symbolsForStack = grammar.nonTerminals          
		self.table = self.buildTable()

	def buildTable(self):
		table = {(x,y):[] for x in self.symbolsForStack for y in self.inputSymbols}
		for X in self.symbolsForStack:
			for prod in self.symbolsForStack[X]:
				if len(prod) == 1 and prod[0] == Epsilon():
					for t in self.Follows[X]:
						a = self.Asign(table, X, t, prod), Fail
						if isinstance (a, Fail):return a
				else:
					for t in self.Firsts[prod]:
						if t == Epsilon():
							for terminal in self.Follows[X]:
								a = self.Asign(table, X, terminal, prod)
								if isinstance(a,Fail): return a
						else:
							a = self.Asign(table, X, t, prod)
							if isinstance(a, Fail) : return a
		return table

	def parse_tree(self, tokens):
		index_tokens= 0
		index_node_tree= 0
		derivation_tree = Tree(label = str (self.initialSymbol) + "_" + str(index_node_tree), children = [], parent = None)
		stack_symbols = [(self.initialSymbol, derivation_tree)]        
		column_tracking= 1
		row_tracking= 1
		
		while(stack_symbols and index_tokens < len(tokens)):
			symbol, current_tree = stack_symbols.pop()

			if isinstance(symbol, Terminal):
				if not tokens[index_tokens] == symbol:
					return Fail("({0}, {1}): Syntax error at or near {2}".format(row_tracking, column_tracking, tokens[index_tokens]))
				index_tokens += 1
				column_tracking += 1

			if isinstance(symbol, NoTerminal):
				prod = self.table[symbol, tokens[index_tokens]]
				if not prod:
					return Fail("({0}, {1}): Syntax error at or near {2}".format(row_tracking, column_tracking, tokens[index_tokens]))

				index_node_tree += 1
				node_to_push = Tree(label = str (prod) + '_' + str(index_node_tree), 
                        children = [], parent = current_tree)
				current_tree.children.append(node_to_push)
				for i in range(len(prod) - 1, -1, -1):
					if prod[i] != Epsilon():
						stack_symbols.append((prod[i], node_to_push))

			
			if symbol.name == '\n':
				row_tracking += 1
				column_tracking = 1

		if not (not stack_symbols and index_tokens == len(tokens)):
			return Fail("({0}, {1}): Syntax error at or near {2}".format(row_tracking, column_tracking, tokens[index_tokens]))
		return derivation_tree

	def printTable(self):
		print(end ='\t')
		for x in self.inputSymbols:
			print(x, end= '\t')
		print('\n')
		for y in self.symbolsForStack:
			print(y,end ='\t')
			for x in self.inputSymbols:
				print(self.table[y,x],end ='\t')
			print('\n')

	def Asign(self,table, symbolForStack, inputSymbol, prod):
		if not table[(symbolForStack,inputSymbol)]:
			table[(symbolForStack, inputSymbol)] = prod
			return True
		else:
			return Fail("Grammar is not LL(1):\nConflict between {0} y {1} for terminal {2}".format(
				(symbolForStack,table[(symbolForStack, inputSymbol)]), (symbolForStack, prod), inputSymbol))
		
	
		
class LR_Parser(PredictiveParser):
	def __init__(self, grammar, parse_type = 0):
		super().__init__(grammar)
		
		initialSymbol = NoTerminal(name = grammar.initialSymbol.name + "'")                
		d = {initialSymbol : [tuple([grammar.initialSymbol])]}
		d.update(grammar.nonTerminals)
		self.augmentedGrammar = GrammarClass(initialSymbol = None, terminals = [], nonTerminals=[] )
		self.augmentedGrammar.initialSymbol = initialSymbol
		self.augmentedGrammar.terminals = grammar.terminals
		self.augmentedGrammar.nonTerminals = d
		self.Firsts = CalculateFirst(self.augmentedGrammar)
		self.Follows = CalculateFollow(self.augmentedGrammar, self.Firsts)
		self.LR_Automaton = LR_Parser.canonical_LR(self, need_lookahead= 1 if parse_type == 'LALR(1)' else 2 if parse_type == 'LR(1)' else  0)
		self.table, self.conflict_info, self.was_conflict = LR_Parser.buildTable(self, parser_type = parse_type, automaton = self.LR_Automaton)

	def canonical_LR(self, need_lookahead = False):
		initialState =canonical_State (label = "I{0}".format(0), 
                                 		setOfItems = [Item(label = {FinalSymbol()} if need_lookahead else None, 
                                                      grammar = self.augmentedGrammar, 
                                                      nonTerminal= self.augmentedGrammar.initialSymbol, 
                                                      point_Position = 0, 
                                                      production = self.augmentedGrammar.nonTerminals[self.augmentedGrammar.initialSymbol][0])],
                                   		grammar = self.augmentedGrammar)          
		canonical_states = [initialState]
		statesQueue = [canonical_states[0]]
		transition_table = {}
		
		while (statesQueue):            
			otherCurrent = None
			if not isinstance(statesQueue[0], tuple):
				currentState = statesQueue.pop(0)
			else:
				currentState, otherCurrent = statesQueue.pop(0)
			currentState.setOfItems = (LR_Parser.closure(self, currentState.kernel_items))
			symbols = []            
			{symbols.append (item.production[item.point_Position]) for item in currentState.setOfItems if item.point_Position < len(item.production) and not item.production[item.point_Position] in symbols}
			for x in symbols:                
				new_state = LR_Parser.goto(self, currentState, x, len(canonical_states))
				if otherCurrent:
					if transition_table[(otherCurrent,x)] != new_state:
						return Fail("No se puede hacer la mezcla LALR, ya que hay indeterminismo para los estados {0}:{3} y {1}:{4} con el símbolo {2}".format(currentState, otherCurrent, x, new_state, transition_table[(otherCurrent, x)]))
					
				founded = False
				state_for_mixed = None
				for state in canonical_states:
					if state == new_state:
						new_state= state
						if need_lookahead :
							if state.equal_looksahead(new_state):
								founded = True
							if founded:
								break
							state_for_mixed = state if need_lookahead == 2 else None
							if state_for_mixed: 
								break
						else:
							founded = True
							break                           

				if not founded:
					if not state_for_mixed:
						canonical_states.append(new_state)
						statesQueue.append(new_state)
					else:
						changed = False
						for i in range(len(state_for_mixed.kernel_items)):
							before = len(state_for_mixed.kernel_items[i].label)
							state_for_mixed.kernel_items[i].label.update(new_state.kernel_items[i].label)
							changed = not before == len(state_for_mixed.kernel_items[i].label)
						if changed:    
							state_for_mixed.label += "-" + new_state.label
							statesQueue.append((new_state,state_for_mixed))
				
				transition_table.update({(currentState, x): new_state})     

		grammar_symbols = {x for x in self.augmentedGrammar.nonTerminals}.union(self.augmentedGrammar.terminals)        
		return Automaton(states = canonical_states, 
						symbols = grammar_symbols, 
						initialState =canonical_states[0], 
						FinalStates = canonical_states, 
						transitions = transition_table )

	def goto(self, current_state, grammar_symbol, index):
		new_state = canonical_State(label = "I{0}".format(index), setOfItems = [], grammar = self.augmentedGrammar)
		
		for item in current_state.setOfItems:
			if item.point_Position < len(item.production):
				if item.production[item.point_Position] == grammar_symbol:
					to_extend = Item(label = item.label.copy() if item.label else None, grammar = self.augmentedGrammar, nonTerminal = item.nonTerminal, point_Position = item.point_Position + 1, production = item.production)                    
					new_state.extend([to_extend])        
		return new_state
		

	def closure(self, kernel_items):
		closure = list(kernel_items)
		itemsQueue = list(kernel_items)        
		while(itemsQueue):
			current = itemsQueue.pop(0)
			if current.point_Position < len(current.production):
				X = current.production[current.point_Position]

				if current.label:
					looks_ahead = set()
					for ahead_symbol in current.label:
						to_update = FirstsForBody(current.production[current.point_Position +1:] + tuple([ahead_symbol]), self.Firsts)
						looks_ahead.update(to_update)
				else:
					looks_ahead = None

				if looks_ahead and Epsilon() in looks_ahead: looks_ahead = {current.label}
				if (isinstance(X, NoTerminal)):
					itemsToQueue = []
					for prod in self.augmentedGrammar.nonTerminals[X]:
						itemToAppend = Item(label = looks_ahead.copy() if looks_ahead else None, grammar = self.augmentedGrammar, nonTerminal= X, point_Position = 0, production = prod if prod != tuple([Epsilon()]) else ())
						founded = False
						for item in closure:
							if item == itemToAppend:
								if item.label: item.label.update(itemToAppend.label)
								founded = True                                
						if not founded:
							itemsToQueue.append(itemToAppend)
																		   
					itemsQueue.extend(itemsToQueue)                    
					closure.extend(itemsToQueue)            
		return closure

	def buildTable(self, parser_type, automaton):                
		inputSymbols= self.augmentedGrammar.terminals + [FinalSymbol()] + [x for x in self.augmentedGrammar.nonTerminals if x != self.augmentedGrammar.initialSymbol]
		self.inputSymbols= inputSymbols
		table = {(state, symbol):[] for state in automaton.states for symbol in inputSymbols}
		conflict_info = {state:[] for state in automaton.states}
		was_conflict = False
		for state in automaton.states:
			for item in state.setOfItems:
				shift_reduce_conflict = []
				reduce_reduce_conflict = []
				if item.point_Position < len(item.production):
					symbol = item.production[item.point_Position]
					if table[(state, symbol)] and isinstance(table[(state, symbol)][-1], reduce):
						shift_reduce_conflict.append (table[(state, symbol)])

					response_state = automaton.transitions[(state, symbol)]
					table[(state,symbol)].append(shift(table_tuple = tuple([state,symbol]), response = response_state, label = "S" + response_state.label.partition('-')[0][1:] if isinstance(symbol, Terminal) else response_state.label.partition('-')[0][1:] )) 

				else:
					looks_ahead = self.Follows[item.nonTerminal] if parser_type == 'SLR(1)'\
						else item.label if parser_type == 'LR(1)' \
						else self.augmentedGrammar.terminals + [FinalSymbol()] if parser_type == 'LR(0)' \
						else []
						
					for symbol in looks_ahead:
						if table[state,symbol]:
							if isinstance(table[state,symbol][-1], shift):
								shift_reduce_conflict.append((table[state,symbol][-1], symbol))
							else:
								reduce_reduce_conflict.append((table[state,symbol][-1], symbol))
						if (parser_type == 'LR(0)' or symbol == FinalSymbol())  \
							and (NoTerminal (self.augmentedGrammar.initialSymbol.name.rstrip("'")),) == item.production:
							table[state, symbol].append (accept(table_tuple = (state, symbol), response = 'accept', label='ok'))
						else:
							table[state,symbol].append (reduce(table_tuple = (state, symbol),
														 response = len(item.production),
														 label = item))
				
				if shift_reduce_conflict:
					was_conflict = True
					conflict_info[state] += [shift_reduce_fail(shift_decision = shc,
                                                reduce_decision = table[state,symbol], 
                                                conflict_symbol = conflict_symbol,
                                                state= state.label) for shc, conflict_symbol in shift_reduce_conflict ]
				if reduce_reduce_conflict:
					was_conflict = True
					conflict_info[state] += [reduce_reduce_fail(reduce_decision1 = rdc,
																reduce_decision2 = table[state,symbol],
																conflict_symbol = conflict_symbol,
																state= state.label) for rdc, conflict_symbol in reduce_reduce_conflict ]

		return table, conflict_info, was_conflict

	def parse_tree(self, input_tokens):
		stack_states = [self.LR_Automaton.initialState]
		stack_trees = []
		i = 0
		tokens= input_tokens + [FinalSymbol()]
		index_node_tree= 0
		row_tracker = 1
		column_tracker= 1
		while i < len (tokens):
			if tokens[i].name == '\n':
				row_tracker += 1
				column_tracker = 1
			else:
				column_tracker += 1
			action = next( (act for act in self.table[(stack_states[-1], tokens[i])]), None) 
			if not action:
				return Fail("({0}, {1}): Syntax error at or near {2}".format(row_tracker, column_tracker, tokens[i]))
			if isinstance (action, accept):
    				break
			elif isinstance(action, shift):
				stack_states.append(action.response)
				index_node_tree += 1
				stack_trees.append(Tree(label = str (tokens[i]) + "_" + str(index_node_tree)))
				i += 1
			elif isinstance(action, reduce):
				children = []
				for _ in range(action.response):
					stack_states.pop()
					children.append(stack_trees.pop())
				stack_states.append(self.LR_Automaton.transitions[(stack_states[-1], action.label.nonTerminal)])
				index_node_tree += 1
				stack_trees.append(Tree(label = str (action.label.nonTerminal) + "_" + str(index_node_tree), 
                            children=children))

		return stack_trees.pop()

class Fail:
	def __init__(self, error_message):
		self.error_message = error_message

	def __repr__(self):
		return self.error_message
	
	__str__ = __repr__	
		
class automaton_fail(Fail):
	def __init__(self, fail_type, decision1, decision2, conflict_symbol, state):
		self.decision1 = decision1
		self.decision2 = decision2
		self.conflict_symbol = conflict_symbol
		self.error_message = "State {4} symbol {2} : {3} between {0} and {1} ".format(decision1, decision2 , conflict_symbol, fail_type, state)

class shift_reduce_fail(automaton_fail):
	def __init__(self, shift_decision, reduce_decision, conflict_symbol, state):
		super().__init__(fail_type = "shift-reduce", 
						decision1= shift_decision, 
						decision2 = reduce_decision, 
						conflict_symbol = conflict_symbol,
						state= state)

class reduce_reduce_fail(automaton_fail):
	def __init__(self, 
				reduce_decision1, 
				reduce_decision2, 
				conflict_symbol,
				state):
		super().__init__(fail_type = "reduce-reduce", 
						 decision1= reduce_decision1, 
						 decision2 = reduce_decision2,
						 conflict_symbol = conflict_symbol,
						 state= state)

class Action:
	def __init__(self, table_tuple, response, label):
		self.table_tuple = table_tuple
		self.response = response
		self.label = label

	def __repr__(self):
		return repr(self.label)

class reduce(Action):
	pass

class shift(Action):
	pass

class accept(Action):
	pass

class error(Action, Fail):
	pass

