from FCA import FCA
import csv
import numpy as np
"""
That's just a working example of FCA class usage
"""

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
    print("На что жалуетесь?")
    while True:
        info = fca.getInfo()
        if info:
            print("\nПоздравляем! У тебя " + ", ".join(info) + "! Можешь прогуливать универ! Вот тебе справка!")
        v = fca.getAttributes()
        if not v:
            print("Больше мы тебе ничего не скажем!\n\nИли у тебя еще что-то болит?\n")
            continue
        for i in range(0, len(v)):
            print(str(i + 1) + " " + ", ".join(v[i]))
        print(str(len(v) + 1) + " Ни на что! Просто дайте мне справку в универ!")
        qIn = input()
        if qIn == "Q":
            print("Не болей!")
            exit(0)
        else:
            if int(qIn) == len(v) + 1:
                fca.refresh()
                print("Или говори, чем болеешь, или иди учись!\n")
                continue
            fca.addAttributes(v[int(qIn) - 1])