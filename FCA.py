import numpy as np
import networkx as nx
from matplotlib import pyplot as plt


class Node:
    def __init__(self, objects, attributes, num, **kwargs):
        self.num = num
        self.active = True
        self.attributes = []
        self.uniqueAttributes = []
        if (attributes is not None):
            self.attributes.extend(attributes)
        self.objects = []
        if (objects is not None):
            self.objects.extend(objects)
        self.children = []
        self.parents = []
        if ("isConcept" in kwargs.keys() and kwargs["isConcept"] == True):
            self.isConcept = True
        else:
            self.isConcept = False

        if ("isAttributeEntry" in kwargs.keys() and kwargs["isAttributeEntry"] == True):
            self.isAttributeEntry = True
            self.uniqueAttributes = attributes.copy()
        else:
            self.isAttributeEntry = False

        self.importance = 0

    def __str__(self):
        return "(#" + str(self.num) + " parents:[" + ", ".join(
            str(parent.num) for parent in self.parents) + "]" + " children:[" + ", ".join(
            str(child.num) for child in self.children) + "]" + (
                   ("\n       A:" + str(self.uniqueAttributes)) if self.isAttributeEntry else "") + (
                   ("\n       C:" + str(self.objects)) if self.isConcept else "") + ")"

    def deactivate(self):
        self.active = False

    def isNotEndStart(self):
        return self.active and self.children and self.parents

    def __eq__(self, other):
        if (isinstance(other, Node)):
            return self.num == other.num

    def clearFastLinks(self):
        for parent in self.parents:
            for child in self.children:
                if child.active and parent.active:
                    if child in parent.children:
                        parent.children.remove(child)
                    if parent in child.parents:
                        child.parents.remove(parent)

    def dfs(self, final, collection):
        if self is final:
            return True
        collection.add(self.num)
        for node in self.parents:
            if node.num in collection:
                raise Exception("cicle in " + str(node))
            if node.dfs(final, collection):
                return True
        collection.remove(self.num)
        return False

    def connectWithChild(self, child):
        child.parents.append(self)
        self.children.append(child)

    def connectWithParent(self, parent):
        self.parents.append(parent)
        parent.children.append(self)


class FCA:
    def __init__(self, attributes, objects, objectsChance, data, exams, examsCost, examsTime, examsData):
        for i in range(0, len(data)):
            for j in range(0, len(data[i])):
                if (data[i][j] == ""):
                    data[i][j] = "0"
        self.data = data.astype(np.float)
        self.boolData = np.ones((len(data), len(data[0])))
        for i in range(0, len(data)):
            for j in range(0, len(data[i])):
                if (self.data[i][j] == 0 or self.data[i][j] < sum(self.data[i, :]) / len(attributes) and self.data[i][
                    j] < sum(self.data[:, j]) / len(objects)):
                    self.boolData[i][j] = False
                else:
                    self.boolData[i][j] = True

        self.objects = objects
        self.objectsChance = np.asfarray(np.array(objectsChance), float)
        for chance in self.objectsChance:
            chance /= sum(self.objectsChance)
        self.attributes = attributes

        self.exams = exams
        self.examsCost = np.asfarray(np.array(examsCost), float)
        self.examsTime = np.asfarray(np.array(examsTime), float)

        for i in range(0, len(examsData)):
            for j in range(0, len(examsData[i])):
                if (examsData[i][j] == ""):
                    examsData[i][j] = "0"
        self.examsData = np.asfarray(np.array(examsData), float)

        self.examsDict = dict()
        for i in range(0, len(self.exams)):
            for j in range(0, len(self.attributes)):
                if self.examsData[i][j] > 0:
                    if self.exams[i] not in self.examsDict:
                        self.examsDict[self.exams[i]] = dict()
                    self.examsDict[self.exams[i]][self.attributes[j]] = self.examsData[i][j]

        self.passedExams = []

        self.startNode = Node(objects, None, 0)
        self.endNode = Node(None, attributes, 1)
        self.size = 2
        self.graph = [self.startNode, self.endNode]

        self.attributesDegree = dict()
        self.activeAttributes = set()
        self.falseAttributes = set()
        self.activeNodes = [self.startNode]
        self.statistics = dict(map(lambda object: (object, (0, 0, 0, 0, 0)), self.objects))

    def calculateStatistics(self):
        for i in range(0, len(self.objects)):
            sumActiveRequired = 0
            sumActiveNotRequired = 0
            sumNotActiveRequired = 0
            sumRequired = 0
            for j in range(0, len(self.attributes)):
                if self.attributes[j] in self.activeAttributes and self.data[i][j] > 0:
                    sumActiveRequired += self.attributesDegree[self.attributes[j]] / self.data[i][j]
                if self.attributes[j] in self.falseAttributes and self.data[i][j] > 0:
                    sumNotActiveRequired += self.data[i][j]
                if self.attributes[j] in self.activeAttributes and self.data[i][j] == 0:
                    sumActiveNotRequired += self.attributesDegree[self.attributes[j]]
                if self.data[i][j] > 0:
                    sumRequired += self.data[i][j]
            completeness = sumActiveRequired / sumRequired
            loss = sumNotActiveRequired / sumRequired
            match = 1 if sumNotActiveRequired == 0 else sumActiveRequired / (sumActiveRequired + sumNotActiveRequired)
            surplus = sumActiveNotRequired / sumRequired
            self.statistics[self.objects[i]] = (completeness, match, surplus, loss, self.objectsChance[i])

    def refresh(self):
        self.attributesDegree = dict()
        self.activeAttributes = set()
        self.falseAttributes = set()
        self.activeNodes = [self.startNode]
        self.statistics = dict(map(lambda object: (object, (0, 0, 0, 0, 0)), self.objects))
        self.calculateStatistics()

    def getExaminations(self):
        if len(self.activeNodes) == 0:
            self.refresh()
            return None

        examsImportance = dict()
        examsProbability = dict()
        examsValue = dict(zip(self.exams, self.examsCost))

        attributesProbability = dict()
        attributesImportance = dict()
        for activeNode in self.activeNodes:
            for node in activeNode.children:
                if node is not self.endNode:
                    for attribute in node.attributes:
                        attributeProbability = 0
                        attributeImportance = 0
                        if attribute not in self.falseAttributes and attribute not in self.activeAttributes:
                            for child in self.graph:
                                if child.isConcept and child.dfs(node, set()):
                                    object = child.objects[0]
                                    objectNum = list(self.objects).index(object)
                                    attributeNum = list(self.attributes).index(attribute)
                                    # probability of attribute = sum of (match * frequency of attribute * frequency of illness)
                                    attributeProbability += self.statistics[object][1] * \
                                                            self.data[objectNum][attributeNum] * \
                                                            self.objectsChance[objectNum]
                                    # importance of concept = (completeness * frequency of attribute)
                                    attributeImportance += self.statistics[object][0] * \
                                                           self.data[objectNum][attributeNum]
                            if attribute in attributesImportance:
                                attributesImportance[attribute] = max(attributeImportance,
                                                                      attributesImportance[attribute])
                            else:
                                attributesImportance[attribute] = attributeImportance
                            if attribute in attributesProbability:
                                attributesProbability[attribute] = max(attributeProbability,
                                                                       attributesImportance[attribute])
                            else:
                                attributesProbability[attribute] = attributeProbability

        for examName, examAttributes in self.examsDict.items():
            for attribute in attributesProbability.keys():
                attributeProbability = 0
                attributeImportance = 0
                if attribute in examAttributes and attribute not in self.activeAttributes and attribute not in self.falseAttributes:
                    for node in self.graph:
                        if attribute in node.uniqueAttributes:
                            for child in self.graph:
                                if child.isConcept and child.dfs(node, set()):
                                    object = child.objects[0]
                                    objectNum = list(self.objects).index(object)
                                    attributeNum = list(self.attributes).index(attribute)
                                    # probability of attribute = sum of (match * frequency of attribute * frequency of illness)
                                    attributeProbability += self.statistics[object][1] * \
                                                            self.data[objectNum][attributeNum] * \
                                                            self.objectsChance[objectNum]
                                    # importance of concept = (completeness * frequency of attribute)
                                    attributeImportance += self.statistics[object][0] * \
                                                           self.data[objectNum][attributeNum]
                            if attribute in attributesImportance:
                                attributesImportance[attribute] = max(attributeImportance,
                                                                      attributesImportance[attribute])
                            else:
                                attributesImportance[attribute] = attributeImportance
                            if attribute in attributesProbability:
                                attributesProbability[attribute] = max(attributeProbability,
                                                                       attributesImportance[attribute])
                            else:
                                attributesProbability[attribute] = attributeProbability
                            break
            for attribute in examAttributes:
                if attribute in attributesImportance:
                    if examName not in examsImportance:
                        examsImportance[examName] = 0
                    examsImportance[examName] += attributesImportance[attribute]

                    if examName not in examsProbability:
                        examsProbability[examName] = 0
                    examsProbability[examName] += attributesProbability[attribute]

        for examName in self.passedExams:
            examsImportance.pop(examName, None)
            examsProbability.pop(examName, None)
            examsValue.pop(examName, None)
        examsImportanceList = sorted(examsImportance.items(), key=lambda item: (-item[1], item[0]))
        examsProbabilityList = sorted(examsProbability.items(), key=lambda item: (-item[1], item[0]))
        examsValueList = sorted(examsValue.items(), key=lambda item: (item[1], item[0]))
        # print("examsProbability ", str(examsProbabilityList))
        # print("examsImportance ", str(examsImportanceList))
        # print("examsValue ", str(examsValueList))

        return examsImportanceList, examsProbabilityList, examsValueList

    def getAttribute(self):
        if len(self.activeNodes) == 0:
            self.refresh()
            return None

        attributesImportance = dict()
        attributesProbability = dict()
        for activeNode in self.activeNodes:
            for node in activeNode.children:
                if node is not self.endNode:
                    for attribute in node.attributes:
                        attributeImportance = 0
                        attributeProbability = 0
                        if attribute not in self.falseAttributes and attribute not in self.activeAttributes:
                            for child in self.graph:
                                if child.isConcept and child.dfs(node, set()):
                                    object = child.objects[0]
                                    objectNum = list(self.objects).index(object)
                                    attributeNum = list(self.attributes).index(attribute)
                                    # probability of concept = match * frequency of illness
                                    attributeProbability += self.statistics[object][1] * self.data[objectNum][
                                        attributeNum] * self.objectsChance[objectNum]
                                    # importance of concept = completeness * match * frequency of illness
                                    attributeImportance += self.statistics[object][0] * self.statistics[object][1] * \
                                                           self.data[objectNum][attributeNum] * self.objectsChance[
                                                               objectNum]
                            if attribute in attributesImportance:
                                attributesImportance[attribute] = max(attributeImportance,
                                                                      attributesImportance[attribute])
                            else:
                                attributesImportance[attribute] = attributeImportance
                            if attribute in attributesProbability:
                                attributesProbability[attribute] = max(attributeProbability,
                                                                       attributesImportance[attribute])
                            else:
                                attributesProbability[attribute] = attributeProbability

        items = sorted(attributesProbability.items(), key=lambda item: (-item[1], item[0]))

        attributesImportanceList = sorted(attributesImportance.items(), key=lambda item: (-item[1], item[0]))
        attributesProbabilityList = sorted(attributesProbability.items(), key=lambda item: (-item[1], item[0]))
        print("attributeProbability ", str(attributesProbabilityList))
        print("attributeImportance ", str(attributesImportanceList))

        maxProbable = items[0][1]
        mostImportanceAttribute = items[0][0]
        for attribute, probable in items:
            if probable < maxProbable:
                break
            if attributesImportance[mostImportanceAttribute] < attributesImportance[attribute]:
                mostImportanceAttribute = attribute
        return mostImportanceAttribute

    def addAttribute(self, attribute, degree):
        self.activeAttributes.add(attribute)
        self.attributesDegree[attribute] = degree
        newActiveNodes = []
        for activeNode in self.activeNodes:
            for child in activeNode.children:
                if child is not self.endNode and attribute in child.uniqueAttributes:
                    if child not in self.activeNodes:
                        newActiveNodes.append(child)
        self.activeNodes.extend(newActiveNodes)
        self.calculateStatistics()

    def removeAttribute(self, attribute):
        self.falseAttributes.add(attribute)
        self.attributesDegree[attribute] = 0
        newActiveNodes = []
        for activeNode in self.activeNodes:
            for child in activeNode.children:
                if child is not self.endNode and attribute in child.uniqueAttributes:
                    if len(set(child.uniqueAttributes) - self.activeAttributes - self.falseAttributes) == 0:
                        newActiveNodes.append(child)
        self.activeNodes.extend(newActiveNodes)
        self.calculateStatistics()

    def getInfo(self):
        return self.statistics.items()

    def __str__(self):
        return "\n".join(self.graph)

    def validate(self, line=""):
        print("-----------")
        print(line)
        print("validate started")
        print("-----------")

        for node in self.graph:
            if node.active:
                print(node)

        print("-----------")
        for node in self.graph:
            if node.active:
                for parent in node.parents:
                    if parent is self.startNode:
                        if len(node.parents) != 1:
                            print("startNode + overparents")
                            print("         " + str(node))
                    if parent is node:
                        print("loop at " + str(node))
                    if parent in node.children:
                        print("loop between " + str(node))
                        print("         and " + str(parent))
                    elif node not in parent.children:
                        print("aren't connected " + str(node) + " " + str(parent))
                for child in node.children:
                    if child is self.endNode:
                        if len(node.children) != 1:
                            print("endNode + overchildren")
                            print("         " + str(node))
                    if child is node:
                        print("loop at " + str(node))
                    elif node not in child.parents:
                        print(str(node) + " " + str(child) + " aren't connected")

        for node in self.graph:
            if node.active:
                try:
                    if not node.dfs(self.startNode, set()):
                        print(str(node))
                        print("         isn't connected with startNode")
                except Exception as e:
                    print(str(node))
                    print("      can't go to startNode")
                    print("      " + repr(e))

                try:
                    if not self.endNode.dfs(node, set()):
                        print(str(node))
                        print("         isn't connected with endNode")
                except Exception as e:
                    print(str(node))
                    print("      can't go to startNode")
                    print("      " + repr(e))
        print("-----------")
        print(line)
        print("validate is ended")
        print("-----------\n\n\n\n\n")

    def addConceptNodes(self):
        objectsLen = len(self.objects)
        attributesLen = len(self.attributes)
        for i in range(0, objectsLen):
            tempObjects = [self.objects[k] for k in range(0, objectsLen) if
                           np.array_equal(self.boolData[k, :], self.boolData[i, :])]
            tempAttributes = [self.attributes[j] for j in range(0, attributesLen) if self.data[i][j] > 0]
            node = Node(tempObjects, tempAttributes, self.size, isConcept=True)
            for other in self.graph:
                if sorted(node.attributes) == sorted(other.attributes) and sorted(node.objects) == sorted(
                        other.objects):
                    break
            else:
                self.size += 1
                self.graph.append(node)

    def addAttributeNodes(self):
        objectsLen = len(self.objects)
        attributesLen = len(self.attributes)
        for j in range(0, attributesLen):
            tempObjects = [self.objects[i] for i in range(0, objectsLen) if self.data[i][j] > 0]
            tempAttributes = [self.attributes[k] for k in range(0, attributesLen) if
                              np.array_equal(self.boolData[:, k], self.boolData[:, j])]
            node = Node(tempObjects, tempAttributes, self.size, isAttributeEntry=True)
            for other in self.graph:
                if sorted(node.attributes) == sorted(other.attributes) and sorted(node.objects) == sorted(
                        other.objects):
                    break
            else:
                self.size += 1
                self.graph.append(node)

    def connectNodes(self):
        for child in self.graph:
            for parent in self.graph:
                if child is not parent and set(child.objects).issubset(set(parent.objects)) and \
                        set(parent.attributes).issubset(set(child.attributes)):
                    parent.connectWithChild(child)

    def clearTransitivePaths(self):
        for node in self.graph:
            if node.isNotEndStart():
                node.clearFastLinks()
                if self.endNode in node.children and len(node.children) > 1:
                    node.children.remove(self.endNode)
                    self.endNode.parents.remove(node)
                if self.startNode in node.parents and len(node.parents) > 1:
                    node.parents.remove(self.startNode)
                    self.startNode.children.remove(node)

    def getChildrenAttributeIntersection(self, node):
        attributesIntersection = set()
        if node == self.startNode or node == self.endNode:
            return attributesIntersection
        flag = False
        for child in node.children:
            if (child != self.endNode):
                if not flag and child != self.endNode:
                    attributesIntersection = set(child.attributes)
                    flag = True
                elif child != self.endNode:
                    attributesIntersection &= set(child.attributes)
        attributesIntersection -= set(node.attributes)
        return attributesIntersection

    def optimizeAttributeNodes(self):
        for child in self.graph:
            attributeIntersection = self.getChildrenAttributeIntersection(child)
            if attributeIntersection:
                for parent in self.graph:
                    if parent is not child and not parent.dfs(child, set()):
                        if parent.isNotEndStart() and child.isNotEndStart():
                            if set(parent.attributes).issubset(attributeIntersection):
                                child.attributes.extend(list(parent.attributes))
                                parent.connectWithChild(child)

    def optimizeConceptNodes(self):
        for parent in self.graph:
            for child in self.graph:
                if parent is not child and not parent.dfs(child, set()):
                    if parent.isNotEndStart() and child.isNotEndStart():
                        if set(parent.attributes).issubset(set(child.attributes)):
                            if child not in parent.children:
                                parent.connectWithChild(child)
                                parent.clearFastLinks()

    def clearSingleChildLinks(self):
        for node in self.graph:
            if node.isNotEndStart() and not node.isConcept and len(node.children) == 1 and node.children[
                0] != self.endNode:
                child = node.children[0]
                if node.isAttributeEntry:
                    child.uniqueAttributes = node.uniqueAttributes
                    child.isAttributeEntry = True
                for parent in node.parents:
                    parent.children.remove(node)
                child.parents.remove(node)
                for parent in node.parents:
                    parent.connectWithChild(child)
                node.deactivate()

    def buildLattice(self):
        self.addConceptNodes()
        self.addAttributeNodes()
        self.connectNodes()
        self.clearTransitivePaths()
        self.validate("after clearTransitivePaths 11111111111")

        self.optimizeAttributeNodes()
        self.validate("after optimizeAttributes 222222222")

        self.clearTransitivePaths()
        self.validate("after clearTransitivePaths 33333333333")

        self.clearSingleChildLinks()
        self.validate("after clearSingleChildLinks 444444444444")

        self.clearTransitivePaths()
        self.validate("after clearTransitivePaths 555555555555")

        self.optimizeConceptNodes()
        self.validate("after optimizeConceptNodes 666666666666")

        self.clearTransitivePaths()
        self.validate("after clearTransitivePaths 77777777777")

        self.clearSingleChildLinks()
        self.validate("after clearSingleChildLinks 8888888888")

        self.clearTransitivePaths()
        self.validate("after clearTransitivePaths 999999999")

        self.calculateStatistics()

        print("Мы вас слушаем!\n")
