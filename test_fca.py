from FCA import FCA

"""
That's just a working example of FCA class usage
"""


obj = ['a','b','c','d','e','f','g']
print(len(obj))
attr = ['1','2','3','4','5']
aMat = [
    ['1','0','1','0','1'],
    ['1','0','1','0','1'],
    ['1','0','1','0','0'],
    ['0','1','1','0','1'],
    ['1','0','1','1','0'],
    ['0','1','1','0','1'],
    ['1','0','0','1','1']
]
fca = FCA(aMat,obj,attr)
fca.buildLattice()
fca.saveLattice('data/lattice')
# fca.loadLattice('data/lattice')
fca.saveLatticeGraph('data/latticeFig.png')
while True:
    qIn = input("Enter the query. Intent or Extent separated by space, e.g. 2 3 4 OR a b\nK - show concept\nQ - exit\n")
    input()
    if qIn == "Q":
        exit(0)
    if qIn == "K":
        print(fca.conceptDict)
    else:
        fca.queryLattice(qIn)
