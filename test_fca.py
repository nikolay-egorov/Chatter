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
with open("test.csv", 'r') as fp:
    reader = csv.reader(fp, delimiter=',', quotechar='"', lineterminator='\n')
    data = np.array([row for row in reader])
    exams = None
    for i in range(0, len(data)):
        if data[i][0] == "":
            exams = np.array(data[i + 1:, :])
            data = np.array(data[: i, :])
            break
    attributes = data[0, 3:]
    objects = data[1:, 0]
    objectsChance = data[1:, 1]
    data = data[1:, 3:]
    examsCost = exams[1:, 1]
    examsTime = exams[1:, 2]
    examsData = exams[1:, 3:]
    exams = exams[1:, 0]
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

    fca = FCA(attributes, objects, objectsChance, data, exams, examsCost, examsTime, examsData)
    fca.buildLattice()

    while True:
        info = fca.getInfo()
        info = sorted(fca.getInfo(),
                      key=lambda el: (-el[1][0] * el[1][1], -el[1][1], -el[1][0], el[1][3], -el[1][2], -el[1][4]))
        for i in range(0, len(info)):
            item = info[i]
            print(item[0] + " - match: " + '{0:.4f}'.format(item[1][1]) + "; completeness: " + '{0:.4f}'.format(
                item[1][0]) + "; loss: " + '{0:.4f}'.format(item[1][3]) + "; surplus: " + '{0:.4f}'.format(item[1][2]))
        print("activeAttributes: " + "[" + (", ".join(list(fca.activeAttributes.items()))) + "]")
        print("falseAttributes: " + "[" + (", ".join(list(fca.falseAttributes))) + "]")
        # print("activeNodes: \n" + "[" + (",\n ".join(map(str, list(fca.activeNodes)))) + "]")

        examsImportanceList, examsProbabilityList, examsValueList = fca.getExaminations()
        print("examsImportanceList: " + str(examsImportanceList))
        print("examsProbabilityList: " + str(examsProbabilityList))
        print("examsValueList: " + str(examsValueList))
        print("EXAMS NUMERATION: \n" + "\n".join((str(i) + ": " + fca.exams[i]) for i in range(0, len(fca.exams))))
        print("\nВведите номер исследования: ")
        qIn = input()
        if qIn == "Q" or qIn == "q":
            print("Не болей!")
            exit(0)
        elif qIn == "R" or qIn == "r":
            fca.refresh()
        else:
            for attribute in fca.examsDict[fca.exams[qIn]]:
                print("Введите результат тестирования симптома " + attribute + ": ")
                resIn = float(input())
                if resIn > 0:
                    fca.addAttribute(attribute, resIn)
                else:
                    fca.removeAttribute(attribute)

