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
            ("\n       C:" + str(self.objects)) if self.isConcept else "")+ ")"

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
    def __init__(self, data, objects, attributes):
        for i in range(0, len(data)):
            for j in range(0, len(data[i])):
                if (data[i][j] == ""):
                    data[i][j] = "0"
        self.data = np.asfarray(np.array(data), float)
        self.objects = objects
        self.attributes = attributes
        self.startNode = Node(objects, None, 0)
        self.endNode = Node(None, attributes, 1)
        self.size = 2
        self.graph = [self.startNode, self.endNode]

        self.activeAttributes = set()
        self.falseAttributes = set()
        self.activeNodes = [self.startNode]
        self.statistics = dict(map(lambda object: (object, (0, 0, 0, 0)), objects))

    def calculateStatistics(self):
        for i in range(0, len(self.objects)):
            sumActiveRequired = 0
            sumActiveNotRequired = 0
            sumNotActiveRequired = 0
            sumRequired = 0
            for j in range(0, len(self.attributes)):
                if self.attributes[j] in self.activeAttributes and self.data[i][j] > 0:
                    sumActiveRequired += self.data[i][j]
                if self.attributes[j] in self.falseAttributes and self.data[i][j] > 0:
                    sumNotActiveRequired += self.data[i][j]
                if self.attributes[j] in self.activeAttributes and self.data[i][j] == 0:
                    sumActiveNotRequired += 1
                if self.data[i][j] > 0:
                    sumRequired += self.data[i][j]
            completeness = sumActiveRequired / sumRequired
            loss = sumNotActiveRequired / sumRequired
            match = 1 if sumNotActiveRequired == 0 else sumActiveRequired / (sumActiveRequired + sumNotActiveRequired)
            surplus = sumActiveNotRequired / sumRequired
            self.statistics[self.objects[i]] = (completeness, match, surplus, loss)


    def refresh(self):
        self.activeAttributes = set()
        self.falseAttributes = set()
        self.activeNodes = [self.startNode]
        self.statistics = dict(map(lambda object: (object, 0, 0, 0), self.objects))
        self.calculateStatistics()

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
                                    attributeProbability += self.statistics[object][1] * self.data[objectNum][attributeNum] * 1
                                    # importance of concept = completeness * match * frequency of illness
                                    attributeImportance += self.statistics[object][0] * self.statistics[object][1]  * self.data[objectNum][attributeNum] * 1
                            if attribute in attributesImportance:
                                attributesImportance[attribute] = max(attributeImportance, attributesImportance[attribute])
                            else:
                                attributesImportance[attribute] = attributeImportance
                            if attribute in attributesProbability:
                                attributesProbability[attribute] = max(attributeProbability, attributesImportance[attribute])
                            else:
                                attributesProbability[attribute] = attributeProbability

        items = sorted(attributesProbability.items(), key = lambda item:(-item[1], item[0]))

        maxProbable = items[0][1]
        mostImportanceAttribute = items[0][0]
        for attribute, probable in items:
            if probable < maxProbable:
                break
            if attributesImportance[mostImportanceAttribute] < attributesImportance[attribute]:
                mostImportanceAttribute = attribute
        return mostImportanceAttribute

    def addAttribute(self, attribute):
        self.activeAttributes.add(attribute)
        newActiveNodes = []
        for activeNode in self.activeNodes:
            for child in activeNode.children:
                if child is not self.endNode and attribute in child.attributes:
                    if child not in self.activeNodes:
                        newActiveNodes.append(child)
        self.activeNodes.extend(newActiveNodes)
        self.calculateStatistics()

    def removeAttribute(self, attribute):
        self.falseAttributes.add(attribute)
        newActiveNodes = []
        for activeNode in self.activeNodes:
            for child in activeNode.children:
                if child is not self.endNode and attribute in child.attributes:
                    if len(set(child.attributes) - self.activeAttributes - self.falseAttributes) == 0:
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
                           np.array_equal(self.data[k, :], self.data[i, :])]
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
                              np.array_equal(self.data[:, k], self.data[:, j])]
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

    # for x in range(0, len(self.bipartiteGroups)):
    #     object = "".join(str(m) for m in sorted(self.bipartiteGroups[x][0]))
    #     attribute = "".join(str(m) for m in sorted(self.bipartiteGroups[x][1]))
    #     self.conceptDict[object] = set(self.bipartiteGroups[x][1])
    #     self.conceptDict[attribute] = set(self.bipartiteGroups[x][0])
    #
    # self.bipartiteGroups.sort(key=lambda a: len(a[0]))
    # return self.conceptDict

    #
    # def removeUnclosed(self):
    #     flist = []
    #     for x in range(0, len(self.bipartiteGroups)):
    #         list_attr = []
    #         list_obj = []
    #         for y in range(0, len(self.bipartiteGroups[x][0])):
    #             if list_attr == []:
    #                 list_attr = self.dictionaryGM[self.bipartiteGroups[x][0][y]]
    #             else:
    #                 list_attr = list(set(list_attr).intersection(set(self.dictionaryGM[self.bipartiteGroups[x][0][y]])))
    #
    #         for z in range(0, len(self.bipartiteGroups[x][1])):
    #             if not list_obj:
    #                 list_obj = self.dictionaryGM[self.bipartiteGroups[x][1][z]]
    #             else:
    #                 list_obj = list(
    #                     set(list_obj).intersection(set(self.dictionaryGM[self.bipartiteGroups[x][1][z]])))
    #         # print ("printing both list for ",  x,  list_top,  list_bottom)
    #         if set(list_attr) == set(self.bipartiteGroups[x][1]) and set(list_obj) == set(self.bipartiteGroups[x][0]):
    #             flist.append(self.bipartiteGroups[x])
    #     self.bipartiteGroups = flist
    #     return self.bipartiteGroups
    #
    # # Need improvements
    # def buildLatticeGraph(self):
    #
    #     hasSuccessor = []
    #     hasPredecessor = []
    #     for x in range(0, len(self.bipartiteGroups)):
    #         nodeName = "".join(str(m) for m in self.bipartiteGroups[x][0]) + ", " + "".join(
    #             str(m) for m in self.bipartiteGroups[x][1])
    #         self.graphnx.add_node(nodeName)
    #
    #     for x in range(0, len(self.bipartiteGroups)):
    #         for y in range(x + 1, len(self.bipartiteGroups)):
    #             if set(self.bipartiteGroups[x][0]).issubset(set(self.bipartiteGroups[y][0])):
    #                 nodeName1 = "".join(str(m) for m in self.bipartiteGroups[x][0]) + ", " + "".join(
    #                     str(m) for m in self.bipartiteGroups[x][1])
    #                 nodeName2 = "".join(str(m) for m in self.bipartiteGroups[y][0]) + ", " + "".join(
    #                     str(m) for m in self.bipartiteGroups[y][1])
    #                 self.graphnx.add_edge(nodeName1, nodeName2)
    #                 hasSuccessor.append(x)
    #                 hasPredecessor.append(y)
    #
    #     # Creating the top most and the bottom most node
    #     list_top = []
    #     list_bottom = []
    #     for x in range(0, len(self.attributes)):
    #         if not list_top:
    #             list_top = self.dictionaryGM[self.attributes[x]]
    #         else:
    #             list_top = list(set(list_top).intersection(set(self.attributes[x])))
    #
    #     for x in range(0, len(self.objects)):
    #         if not list_bottom:
    #             list_bottom = self.dictionaryGM[self.objects[x]]
    #         else:
    #             list_bottom = list(set(list_bottom).intersection(set(self.objects[x])))
    #     if not list_bottom:
    #         list_bottom = ["null"]
    #     if not list_top:
    #         list_top = ["null"]
    #
    #     # adding them to the graph
    #     firstNode = "".join(str(m) for m in list_top) + ", " + "".join(str(m) for m in self.attributes)
    #     # print(firstNode)
    #     self.graphnx.add_node(firstNode)
    #     lastNode = "".join(str(m) for m in self.objects) + ", " + "".join(str(m) for m in list_bottom)
    #     self.graphnx.add_node(lastNode)
    #
    #     # adding edges to them self.M[x]
    #     for x in range(0, len(self.bipartiteGroups)):
    #         if x not in hasSuccessor:
    #             nodeName = "".join(str(m) for m in self.bipartiteGroups[x][0]) + ", " + "".join(
    #                 str(m) for m in self.bipartiteGroups[x][1])
    #             # print(nodeName)
    #             self.graphnx.add_edge(nodeName, lastNode)
    #
    #     for x in range(0, len(self.bipartiteGroups)):
    #         if x not in hasPredecessor:
    #             nodeName = "".join(str(m) for m in self.bipartiteGroups[x][0]) + ", " + "".join(
    #                 str(m) for m in self.bipartiteGroups[x][1])
    #             self.graphnx.add_edge(nodeName, firstNode)
    #     return self.graphnx
    #
    # def queryLattice(self, query):
    #     self.bipartiteGroups.sort(key=lambda x: len(x[0]))
    #     key = "".join(str(m) for m in sorted(query.split()))
    #     if key in self.conceptDict:
    #         print(', '.join(self.conceptDict[key]), "\n")
    #     else:
    #         print("Not present in Concept lattice\n")
    #     return 0
    #
    # def saveLatticeGraph(self, path):
    #     if not self.graphnx:
    #         self.buildLatticeGraph()
    #
    #     nx.draw(self.graphnx, nx.kamada_kawai_layout(self.graphnx), with_labels=True,
    #             node_color=range(self.graphnx.number_of_nodes()),
    #             cmap=plt.cm.Blues)
    #     plt.axis('off')
    #     plt.savefig(path)
    #
    # def saveLattice(self, path):
    #     np.savez(path, I=self.data, M=self.attributes, G=self.objects, dictionaryGM=self.dictionaryGM,
    #              conceptDict=self.conceptDict,
    #              bipartiteGroups=self.bipartiteGroups)
    #
    # def loadLattice(self, path):
    #     data = np.load(path + ".npz")
    #     self.data = data['I'].tolist()
    #     self.objects = data['G'].tolist()
    #     self.attributes = data['M'].tolist()
    #     self.dictionaryGM = data['dictionaryGM'].tolist()
    #     self.conceptDict = data['conceptDict'].tolist()
    #     self.bipartiteGroups = data['bipartiteGroups'].tolist()
    #     return self.conceptDict
