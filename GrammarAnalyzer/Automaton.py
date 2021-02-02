from GrammarAnalyzer.Grammar import GrammarClass, Epsilon, NoTerminal

class Automaton:
	def __init__(self, states, symbols, initialState, FinalStates, transitions):
		self.states = states
		self.symbols = symbols
		self.initialState = initialState
		self.FinalStates = FinalStates
		self.transitions = transitions
		self.currentState = initialState

	def trans(self, inputSymbol):
		return self.transitions[(self.currentState, inputSymbol)]        

	def accept(self):
		return self.currentState in self.FinalStates

	
	def add_transition(self, state_out, symbol, state_in):
		if not (state_out, symbol) in self.transitions :
			self.transitions.update({(state_out, symbol) : state_in })
		else:
			self.transitions[state_out, symbol] =state(label = self.transitions [state_out, symbol].label  + state_in.label  )  
	


class state:
	def __init__(self, label):
		self.label = label        

	def __eq__(self,other):
		return self.label == other.label
	
	def __hash__(self):
		return hash(self.label)

	def __repr__(self):
		return "state: !" + repr(self.label) + "!"


class canonical_State(state):    

	def __init__(self, label, setOfItems, grammar:GrammarClass):
		self.label = label
		self.setOfItems = setOfItems
		self.kernel_items = [x for x in setOfItems if x.isKernel]
		self.grammar =grammar

	def extend(self, otherList):
		self.setOfItems.extend(otherList)
		self.kernel_items.extend(x for x in otherList if x.isKernel)

	def __eq__(self, other):
		return self.kernel_items == other.kernel_items

	def equal_looksahead(self, other):
		if not self.kernel_items and not other.kernel_items: return True
		if self.kernel_items != other.kernel_items: return False
		for x in self.kernel_items:
			for y in other.kernel_items:
				if x==y and x.label!=y.label: return False
		return True

	def __repr__(self):
		l = "".join( repr(x) + '\n' for x in self.kernel_items )
		l += '--------------\n'
		l += "".join(repr(x) + '\n' for x in self.setOfItems if not x in self.kernel_items)
		return repr(self.label) + "\n " + repr(l) 


	def __hash__(self):
		toReturn = 0
		for item in self.kernel_items:            
			toReturn += hash(item)
		return toReturn 

class Item(state):
	def __init__(self, label, grammar:GrammarClass, nonTerminal, point_Position, production):
		super().__init__(label)
		self.nonTerminal = nonTerminal
		self.production = production
		self.point_Position = point_Position * (self.production !=tuple([Epsilon()]))
		self.isKernel = not self.point_Position == 0 or grammar.initialSymbol == self.nonTerminal 

	def __repr__(self):
		toReturn = repr(self.nonTerminal) + "->" + repr(self.production[:self.point_Position]) + "." + repr (self.production[self.point_Position:])
		if self.label: toReturn += ", " + repr(self.label)
		return toReturn

	def __hash__(self):
		return hash(self.nonTerminal) + hash(self.point_Position) + hash(self.production)
	
	def __eq__(self, other):
		return self.production == other.production and self.point_Position == other.point_Position and self.nonTerminal == other.nonTerminal

	def equal_look_ahead(self,other):
		return self.label == other.label


class Tree:
	def __init__(self, label, children = [], parent = None):
		self.label = label
		self.children = children
		self.parent = parent

	def append(self, child):
		self.children.append(child)

	def __repr__(self):
		to_return = str (self.label)
		to_return += '\n'
		for t in self.children:
			to_return+= str(t)
			to_return += '\t'
		return to_return

class regularExpr:
	def __init__(self, left = None, right = None, isClosure = False, isUnion = False, isLeaf = False, symbol = None):
		self.isLeaf = isLeaf
		if self.isLeaf:
			self.left = self.right = None            
		else:
			self.left = left
			self.right = right 
			
		self.symbol = symbol
		self.isClosure = isClosure
		self.isUnion = isUnion
		if self.isClosure:
			if not isUnion:
				self.symbol = '(' + self.symbol + ')'
			if not self.symbol[-1] =='*':
				self.symbol += '*'
	
	def __repr__(self):
		return repr(self.symbol)

	def __add__(self, other):
		if self == other:
			return self
		if isinstance(other, emptyRegExp):
			return self
		return regularExpr(left = self, right = other, symbol = '(' + self.symbol + '|' + other.symbol +')', isUnion = True)

	def concat(self, other):
		if isinstance(other, epsilonRegExp):
			return self
		if isinstance(other, emptyRegExp):
			return other
		return regularExpr(left = self, right = other, symbol= self.symbol + other.symbol)
		
	def toClosure(self): 
		if not isinstance(self, specialRegExp):
			if self.isClosure:
				return self
			if isinstance(self.left, epsilonRegExp):
				return self.right.toClosure()
			if isinstance(self.right, epsilonRegExp):
				return self.left.toClosure()
			return regularExpr(left = self.left, right = self.right, isClosure = True, symbol = self.symbol, isLeaf = self.isLeaf, isUnion=self.isUnion)
		return epsilonRegExp()

	
	def __eq__(self,other):
		return self.symbol == other.symbol
	

class specialRegExp(regularExpr):
	def __init__(self, symbol):
		self.isClosure = self.isUnion = False
		self.isLeaf = True
		self.symbol = symbol
		self.left = None
		self.right = None

	
	def concat (self, other):
		return other

class emptyRegExp (specialRegExp):
	def __init__(self ):
		super().__init__(symbol = 'ø')

	def __add__(self, other):
		return other

	def concat(self, other):
		return self

class epsilonRegExp (specialRegExp):
	def __init__(self):
		super().__init__(symbol = 'œ')
	
	def concat(self, other):        
		return other