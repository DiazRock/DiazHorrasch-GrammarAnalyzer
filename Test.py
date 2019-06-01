
from Parser import *

G = GrammarClass(initialSymbol= "S", terminals= ['a','h','c', 'b', 'g', 'f'], nonTerminals= ['S','B', 'C', 'D', 'E', 'F'])
G.addProduction('F', ['f'], ['œ'])
G.addProduction('S', ['a', 'B', 'D', 'h'])
G.addProduction('B', ['c', 'C'])
G.addProduction('C', ['b', 'C'], ['œ'])
G.addProduction('D', ['E', 'F'])
G.addProduction('E', ['g'], ['œ'])

G1 = GrammarClass(initialSymbol= "S", terminals= ['a','d','b','g'], nonTerminals= ['S','A', "A'", 'B', 'C'])
G1.addProduction('S', ['A'])
G1.addProduction('A', ['a', 'B', "A'"])
G1.addProduction("A'", ['d', "A'"], ['œ'])
G1.addProduction('B', ['b'])
G1.addProduction('C', ['g'])

G2 = GrammarClass(initialSymbol= "S", terminals= ['a', '(',')', ','], nonTerminals= ['S','L', "L'"])
G2.addProduction('S', ['(','L',')'], ['a'])
G2.addProduction('L', ['S', "L'"])
G2.addProduction("L'", [',', "S", "L'"], ['œ'])



G3 = GrammarClass(initialSymbol= "E", terminals= ['+', '(',')', 'int', '*'], nonTerminals= ['E','T', "X",'Y'])
G3.addProduction('E', ['T','X'])
G3.addProduction('X', ['+', "E"], ['œ'])
G3.addProduction("T", ['int', "Y"], ['(', 'E', ')'])
G3.addProduction("Y", ['*', "T"], ['œ'])

G4 = GrammarClass(initialSymbol= "S", terminals= ['a', 'b', 'c', 'd'], nonTerminals= ['S','X', "Y"])
G4.addProduction("S", ['d', 'S'], ['X'], ['c','Y'])
G4.addProduction("X", ['a','Y','b','Y','c','Y'], ['b', 'Y','c'], ['œ'])
G4.addProduction("Y", ['d','Y'], ['X','c'])


G5 = GrammarClass(initialSymbol= "S", terminals= ['a', 'b', 'c', 'd'], nonTerminals= ['S','X', "A", "B", "Y", "Z"])
G5.addProduction("S", ['b', 'a', 'X'])
G5.addProduction("X", ['c','A'], ['d', 'B'])
G5.addProduction("A", ['a','Y'], ['œ'])
G5.addProduction("B", ['a', 'Z'], ['œ'])
G5.addProduction("Y", ['c', 'a', "Y"], ["d"])
G5.addProduction("Z", ['d', 'a', "Z"], ["c"])

G6 = GrammarClass(initialSymbol= "S", terminals= ['a', 'b', 'd'], nonTerminals= ['S','B', 'D'])
G6.addProduction("S", ['B', 'b'],['D','d'])
G6.addProduction("B", ['B', 'a'], ['a'])
G6.addProduction("D", ['D', 'a'], ['a'])

G7 = GrammarClass(initialSymbol= "E", terminals= ['int', '*', '(', ')', '+'], nonTerminals= ['E','T'])
G7.addProduction("E", ['T'], ['T', '+','E'])
G7.addProduction("T", ['int'], ['int', '*','T'], ['(', 'E' ,')'])

G8 = GrammarClass(initialSymbol= "E", terminals= ['=', '+', 'i'], nonTerminals= ['E','A'])
G8.addProduction("E", ['A', '=', 'A'], ['i'])
G8.addProduction("A", ['i', '+', 'A'], ['i'])

G9 = GrammarClass(initialSymbol= "E", terminals= ['-', '+', 'i', "(", ')'], nonTerminals= ['E','A', 'T'])
G9.addProduction("E", ['E', 'A', 'T'], ['T'])
G9.addProduction("A", ['+'], ['-'])
G9.addProduction("T", ['(', 'E', ')'], ['i'])

G10 = GrammarClass(initialSymbol= "E", terminals= ['i', '+', '[', "]", ','], nonTerminals= ['E','V', 'L'])
G10.addProduction("E", ['E', '+', 'V'], ['V'])
G10.addProduction("V", ['i'], ['i', '[','L',']'])
G10.addProduction("L", ['L', ',', 'E'], ['E'])

G11 = GrammarClass(initialSymbol= "S", terminals= ['i', '+', 'r'], nonTerminals= ['S','E'])
G11.addProduction("S", ['E', 'r', 'E'], ['i'])
G11.addProduction("E", ['E', '+', 'i'], ['i'])


G12 = GrammarClass(initialSymbol= "S", terminals= ['a', 'b', 'c'], nonTerminals= ['S','A', 'X', 'B'])
G12.addProduction("S", ['A', 'X'])
G12.addProduction("A", ['a', 'A'], ['œ'])
G12.addProduction("X", ['b', 'B'], ['c', 'B'])
G12.addProduction("B", ['œ'], ['X'])

G13 = GrammarClass(initialSymbol= "S", terminals= ['i', '+', '[',']', '='], nonTerminals= ['S','V', 'A', 'E'])
G13.addProduction("S", ['V', '=','E'], ['i'])
G13.addProduction("V", ['i'], ['A','[','E',']'])
G13.addProduction("A", ['i'])
G13.addProduction("E", ['E','+','V'], ['V'])


print (CalculateFirst(G))
Firsts = CalculateFirst(G)
print(CalculateFollow(G, Firsts), '\n')

FirstsG1 = CalculateFirst(G1)
print(FirstsG1, CalculateFollow(G1, FirstsG1), '\n', sep = '\n')

FirstsG2 = CalculateFirst(G2)
print(FirstsG2, CalculateFollow(G2, FirstsG2), '\n', sep = '\n')
 

LL_Parser(G3).printTable()
LL_Parser(G4).printTable()
LL_Parser(G5).printTable()

deleteInmediateLeftRecusrive(G6)

a = LR_Parser(G7).canonical_LR(need_lookahead= True)
a = LR_Parser(G9).canonical_LR()
a = LR_Parser(G10).canonical_LR()

a = LR_Parser(G8).canonical_LR()
a = LR_Parser(G11).canonical_LR(need_lookahead = 2)

a = LR_Parser(G12).canonical_LR()
a = LR_Parser(G12).canonical_LR(need_lookahead = True)
a = LR_Parser(G12).canonical_LR(need_lookahead = 2)

a = LR_Parser(G13).canonical_LR(need_lookahead = True)
a = LR_Parser(G13).canonical_LR(need_lookahead = 2)