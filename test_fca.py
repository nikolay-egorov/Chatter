from FCA import FCA
import csv
import numpy as np

# obj = ['a','b','c','d','e','f','g']
# print(len(obj))
# attr = ['1','2','3','4','5', '6']
# aMat = [
#     ['1','0','1','0','1', '0'],
#     ['1','0','1','0','1', '0'],
#     ['1','0','1','0','0', '0'],
#     ['0','1','1','0','1', '0'],
#     ['1','0','1','1','0', '1'],
#     ['0','1','1','0','1', '0'],
#     ['1','0','0','1','1', '1']
# ]


with open('test.csv', 'r') as fp:
    reader = csv.reader(fp, delimiter=',', quotechar='"', lineterminator='\n')
    data = np.array([row for row in reader])
    attr = data[0, 1:]
    obj = data[1:, 0]
    aMat = data[1:, 1:]
    # obj = ['больница', 'югу', 'гостинка', 'ул мира', 'мира 100', 'светофор', 'калинина 26']
    # print(len(obj))
    # attr = ['здание', 'дорога', 'социальный', 'жилой', 'мгн', 'пандус', "больн"]
    # aMat = [
    #     ['1', '0', '1', '0', '1', '0', '1'],
    #     ['1', '0', '1', '0', '1', '0', '1'],
    #     ['1', '0', '1', '0', '0', '0', '0'],
    #     ['0', '1', '1', '0', '1', '0', '0'],
    #     ['1', '0', '1', '1', '0', '1', '1'],
    #     ['0', '1', '1', '0', '1', '0', '0'],
    #     ['1', '0', '0', '1', '1', '1', '0']
    # ]

    fca = FCA(aMat, obj, attr)
    fca.buildLattice()


    # fca.saveLattice('data/lattice')
    # fca.loadLattice('data/lattice')
    # fca.saveLatticeGraph('data/latticeFig.png')
    print("Напишите одно число, которое соответствует Вашим симптомам\nQ - exit\n")
    print("Что беспокоит?")
    while True:
        info = fca.getInfo()
        v = fca.getAttributes()
        info = sorted(fca.getInfo(), key = lambda el: (el[1][1], el[1][0]))
        for item in info:
            print(item[0] + " - match: " + str(item[1][1]) + "; completeness: " + str(item[1][0]) + "; surplus: " + str(item[1][2]))
        print("activeAttributes: " + fca.activeAttributes)
        print("falseAttributes: " + fca.falseAttributes + "\n")

        attribute = fca.getAttribute()
        print("Волнует ли: " + attribute)
        qIn = input()
        if qIn == "Q" or qIn == "q":
            print("Не болей!")
            exit(0)
        elif qIn == "R" or qIn == "r":
            fca.refresh()
        elif qIn == "N" or qIn == "n":
            fca.removeAttribute(attribute)
        else:
            fca.addAttributes(attribute)