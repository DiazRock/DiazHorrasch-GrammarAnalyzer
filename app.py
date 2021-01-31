import networkx as nx
import streamlit as st
import numpy as np
import pandas as pd
import plotly
from GrammarAnalyzer.Grammar import GrammarClass,Terminal
import GrammarAnalyzer.AuxiliarMethods as am
import GrammarAnalyzer.Parser as parser
import GrammarAnalyzer.Automaton as automaton
import utils

def main():
	st.sidebar.markdown (
		'''
			## This a context free grammar (CFG) analyzer

			It takes a CFG, and build a parse for it. A tool that generates
			a derivation tree for a string conform by tokens in the alphabet grammar.

			You can input your context free grammar and choose one of
			the options above for analyze it.

		'''
	)

	
	selection = st.sidebar.radio("Select the parser option", ['LL1', 'LR(0)/SLR(1)', 'LALR(1)', 'LR(1)'])

	st.sidebar.markdown(
		'''
			You can follow me!

			[![Twitter Badge](https://img.shields.io/badge/Twitter-Profile-informational?style=flat&logo=twitter&logoColor=white&color=1CA2F1)](https://twitter.com/DiazRock2)
	
			[![LinkedIn Badge](https://img.shields.io/badge/LinkedIn-Profile-informational?style=flat&logo=linkedin&logoColor=white&color=0D76A8)](https://www.linkedin.com/in/diazrock/)

			[![GitHub Badge](https://img.shields.io/badge/GitHub-Profile-informational?style=flat&logo=github&logoColor=white&color=0D76A8)](https://www.github.com/diazrock/)
		'''
	)
	user_input = st.text_area("Enter the context free grammar", height = 40)
	if user_input:
		non_terminals, terminals, productions_by_non_term = utils.preprocess_input(user_input)
		g = GrammarClass(initialSymbol= non_terminals[0],
						terminals= terminals,
						nonTerminals= non_terminals)
		for i, non_terminal in enumerate(non_terminals):
			g.addProduction(non_terminal, *productions_by_non_term[i])

		not_generable_prod_set, not_reachable_prod_set, new_g= am.cleanGrammar(g)
		if not (not_generable_prod_set and not_reachable_prod_set):
			'All non terminals are reachables and generables'
		else:
			if not_generable_prod_set:
				'The following non terminals are not generables %s' %not_generable_prod_set
			if not_reachable_prod_set:
				'The following non terminals are not reachables %s' %not_reachable_prod_set

		if g.LeftRecSet:
			'The following non terminals have left recursive productions %s' %new_g.LeftRecSet
			am.deleteInmediateLeftRecusrive(new_g)
			'This is the grammar without left recursive productions'

			print_grammar(new_g)

		if selection == 'LL1':
			ll = parser.LL_Parser(grammar= new_g)
			result_parse = ll.buildTable()
			if isinstance(result_parse, dict):
				'The grammar is LL1'
				'Here is the table'
				table_index= list(new_g.nonTerminals)
				d = {
						x: [result_parse[nt, x] for nt in table_index ] for x in ll.inputSymbols
					}
				df = pd.DataFrame(
					index= table_index,
					data = d)
				# df= pd.DataFrame(result_parse)
				st.table(df)
				input_chain= st.text_input('Enter a chain for see its derivation tree')
				if input_chain:
					t = ll.parse_tree(tokens= [Terminal(name= x) for x in input_chain.split()])
					if isinstance(t, automaton.Tree):
						draw_graph(t)
					else:
						st.write(t) 
					
			else:
				st.write(result_parse)
		if selection == 'LR(0)/SLR(1)':
			'Gramática LR(0)/SLR(1)'

		if selection == 'LALR(1)':
			'Gramática LALR(1)'

		if selection == 'LR(1)':
			'Gramática LR(1)'


	'''
	Here's a small, quick, example grammar to give you an idea of the format of the grammars:

	S -> id | 
			V assign E.

	V -> id.

	E -> V | 
			num.

	'''

def print_grammar(g):
	for nt in g.nonTerminals:
		str_to_print = '%s -> ' %nt
		for i, prod in enumerate(g.nonTerminals[nt]):
			str_to_print += ''.join(token.name for token in prod)
			if i != len(g.nonTerminals[nt]) - 1:
				str_to_print += ' | '
		str_to_print
		'\n'

def draw_graph(t):
	G= nx.Graph()				
	edges= utils.dfs(t)
	G.add_edges_from( [(x, i) for (x,y ) in edges.items() for i in y ] )
	dot = nx.nx_pydot.to_pydot(G)
	st.graphviz_chart(dot.to_string())


if __name__ == '__main__':
	main()
