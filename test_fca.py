from FCA import FCA
import csv
import numpy as np
#-*- coding: utf-8 -*-

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

print("Укажите путь к файлу матрицы контекста:")

# with open('test.csv', 'r') as fp:
with open(input(), 'r') as fp:
    reader = csv.reader(fp, delimiter=',', quotechar='"', lineterminator='\n')
    data = np.array([row for row in reader])
    attr = data[0, 2:]
    obj = data[1:, 0]
    objChance = data[1:, 1]
    aMat = data[1:, 2:]
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

    fca = FCA(aMat, obj, attr, objChance)
    fca.buildLattice()

    while True:
        info = fca.getInfo()
        info = sorted(fca.getInfo(),
                      key=lambda el: (-el[1][0] * el[1][1], -el[1][1], -el[1][0], el[1][3], -el[1][2], -el[1][4]))
        for i in range(0, len(info)):
            item = info[i]
            if item[1][1] > 0.5 and item[1][0] > 0.5:
                print(item[0] + " - match: " + '{0:.4f}'.format(item[1][1]) + "; completeness: " + '{0:.4f}'.format(
                    item[1][0]) + "; loss: " + '{0:.4f}'.format(item[1][3]) + "; surplus: " + '{0:.4f}'.format(item[1][2]))
        print("activeAttributes: " + "[" + (", ".join(list(fca.activeAttributes))) + "]")
        print("falseAttributes: " + "[" + (", ".join(list(fca.falseAttributes))) + "]")
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
            fca.addAttribute(attribute)
