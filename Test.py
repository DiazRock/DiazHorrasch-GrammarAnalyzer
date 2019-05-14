from Grammar import *
from AuxiliarMethods import *

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

print (CalculateFirst(G))
Firsts = CalculateFirst(G)
print(CalculateFollow(G, Firsts), '\n')

FirstsG1 = CalculateFirst(G1)
print(FirstsG1, CalculateFollow(G1, FirstsG1), '\n', sep = '\n')

FirstsG2 = CalculateFirst(G2)
print(FirstsG2, CalculateFollow(G2, FirstsG2), '\n', sep = '\n')
