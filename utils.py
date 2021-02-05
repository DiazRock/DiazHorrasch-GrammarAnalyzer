def preprocess_input(rg: str):
	rg1 = rg.rstrip()
	raw_input_grammar = [[x for x in line.split('->')] for line in rg1.split('\n')]
	unzipped_object = zip(*raw_input_grammar)
	raw_non_terminals, raw_productions = list(unzipped_object)
	
	
	#Non terminals from input
	non_terminals= [nt.replace(' ', '') for nt in raw_non_terminals]
	
	#Productions from input
	productions_by_non_term= [[p.split() for p in prod.split('|')] for prod in raw_productions]

	for productions in productions_by_non_term:
		for i, prod in enumerate(productions):
			if not prod:
				productions[i]= ['œ']


	terminals = []
	for productions in productions_by_non_term:
		for prod in productions:
			terminals += [t for t in prod if not t== 'œ' if not t in non_terminals if not t in terminals]

	# This is for an order that I can test without effort
	terminals
	return non_terminals, terminals, productions_by_non_term

def dfs(t):
	edges = { t.label : [ child.label for child in t.children]}
	for child in t.children:
		edges.update(dfs(child))
	return edges
	