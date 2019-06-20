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
with open("test3.csv", 'r') as fp:
    reader = csv.reader(fp, delimiter=',', quotechar='"', lineterminator='\n')
    preData = []
    preExams = []
    flag = False
    for row in reader:
        if row[0] == "":
            if flag:
                break
            else:
                flag = True
                continue
        else:
            if not flag:
                preData.append(row)
            else:
                preExams.append(row)


    data = np.array(preData)
    exams = np.array(preExams)

    attributes = data[0, 3:]
    objects = data[1:, 0]
    objectsChance = data[1:, 1]
    data = data[1:, 3:]
    examsCost = exams[1:, 1]
    examsTime = exams[1:, 2]
    examsData = exams[1:, 3:]
    exams = exams[1:, 0]


    fca = FCA(attributes, objects, objectsChance, data, exams, examsCost, examsTime, examsData)
    fca.buildLattice()
    file = open("test.txt", "r+")
    flag = True
    numLine = 1
    while True:
        if not flag:
            file.close()
            file = open("test.txt", "a")
        info = fca.getInfo()
        info = sorted(fca.getInfo(),
                      key=lambda el: (-el[1][0] * el[1][1], -el[1][1], -el[1][0], el[1][3], -el[1][2], -el[1][4]))
        for i in range(0, len(info)):
            item = info[i]
            print(item[0] + " - match: " + '{0:.4f}'.format(item[1][1]) + "; completeness: " + '{0:.4f}'.format(
                item[1][0]) + "; loss: " + '{0:.4f}'.format(item[1][3]) + "; surplus: " + '{0:.4f}'.format(item[1][2]))
        print("activeAttributes: " + "[" + (", ".join(list(fca.activeAttributes))) + "]")
        print("falseAttributes: " + "[" + (", ".join(list(fca.falseAttributes))) + "]")
        # print("activeNodes: \n" + "[" + (",\n ".join(map(str, list(fca.activeNodes)))) + "]")

        print()
        examsImportanceList, examsProbabilityList, examsValueList = fca.getExaminations()
        print("examsImportanceList: " + str(examsImportanceList) + "\n")
        print("examsProbabilityList: " + str(examsProbabilityList) + "\n")
        print("examsValueList: " + str(examsValueList) + "\n")
        print("EXAMS NUMERATION: \n" + "\n".join((str(i) + ": " + fca.exams[i]) for i in range(0, len(fca.exams)) if fca.exams[i] not in fca.passedExams ))
        print("\nВведите номер исследования: ")
        print(str(numLine), end = " - ")
        numLine += 1
        qIn = ""
        if flag:
            qIn = file.readline()
            if not qIn:
                flag = False
                file.close()
                file = open("test.txt", "a")
            else:
                print(qIn)
        if not flag:
            qIn = input()
            file.write(qIn + "\n")


        if qIn == "Q" or qIn == "q":
            print("Не болей!")
            exit(0)
        elif qIn == "R" or qIn == "r":
            fca.refresh()
        else:
            fca.passedExams.append(fca.exams[int(qIn)])
            for attribute in fca.examsDict[fca.exams[int(qIn)]]:
                print("Введите результат тестирования симптома " + attribute + ": ")
                print(str(numLine), end=" - ")
                numLine += 1
                resIn = ""
                if flag:
                    resIn = file.readline()
                    if not resIn:
                        flag = False
                        file.close()
                        file = open("test.txt", "a")
                    else:
                        print(resIn)
                if not flag:
                    resIn = input()
                    file.write(resIn + "\n")
                resIn = int(resIn)
                if resIn > 0:
                    fca.addAttribute(attribute, resIn)
                else:
                    fca.removeAttribute(attribute)

