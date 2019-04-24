import numpy as np
import networkx as nx
from matplotlib import pyplot as plt


class Node:
    def __init__(self, objects, attributes, **kwargs):
        self.active = True
        self.attributes = []
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
        else:
            self.isAttributeEntry = False

    def deactivate(self):
        self.active = False

    def __eq__(self, other):
        if (isinstance(other, Node)):
            return sorted(self.attributes) == sorted(other.attributes) and sorted(self.objects) == sorted(other.objects)

    # def __hash__(self):
    #     return hash(tuple(sorted(self.attributes)))

    def clearFastLinks(self):
        for parent in self.parents:
            for child in self.children:
                if child in parent.children:
                    parent.children.remove(child)
                if parent in child.parents:
                    child.parents.remove(parent)

    def dfs(self, final):
        if self is final:
            return True
        for node in self.parents:
            if node.dfs(final):
                return True
        return False

    def connectWithChild(self, child):
        child.parents.append(self)
        self.children.append(child)

    def connectWithParent(self, parent):
        self.parents.append(parent)
        parent.children.append(self)

    def disconnectWithChild(self, child):
        child.parents.remove(self)
        self.children.remove(child)


class FCA:
    def __init__(self, data, objects, attributes):
        self.data = np.array(data)
        self.objects = objects
        self.attributes = attributes
        self.startNode = Node(objects, None)
        self.endNode = Node(None, attributes)
        self.graph = [self.startNode, self.endNode]
        # self.lattice = []
        # self.adj = {}
        # self.dictionaryGM = {}
        # self.bipartiteGroups = []
        # self.graphnx = nx.Graph()
        # self.conceptDict = {}

    def removeNode(self, node):
        for parent in node.parents:
            parent.children.remove(node)
        for child in node.children:
            child.parents.remove(node)
        self.graph.remove(node)

    def addConceptNodes(self):
        objectsLen = len(self.objects)
        attributesLen = len(self.attributes)
        for i in range(0, objectsLen):
            tempObjects = [self.objects[k] for k in range(0, objectsLen) if
                           np.array_equal(self.data[k, :], self.data[i, :])]
            tempAttributes = [self.attributes[j] for j in range(0, attributesLen) if self.data[i][j] == '1']
            node = Node(tempObjects, tempAttributes, isConcept=True)
            if (node not in self.graph):
                self.graph.append(node)

    def addAttributeNodes(self):
        objectsLen = len(self.objects)
        attributesLen = len(self.attributes)
        for j in range(0, attributesLen):
            tempObjects = [self.objects[i] for i in range(0, objectsLen) if self.data[i][j] == '1']
            tempAttributes = [self.attributes[k] for k in range(0, attributesLen) if
                              np.array_equal(self.data[:, k], self.data[:, j])]
            node = Node(tempObjects, tempAttributes, isAttributeEntry=True)
            if (node not in self.graph):
                self.graph.append(node)

    def connectNodes(self):
        for child in self.graph:
            for parent in self.graph:
                if child is not parent and set(child.objects).issubset(set(parent.objects)) and \
                        set(parent.attributes).issubset(set(child.attributes)):
                    parent.connectWithChild(child)

    def clearTransitivePaths(self):
        for node in self.graph:
            node.clearFastLinks()

    def getChildrenAttributeIntersection(self, node):
        attributesUnion = set()
        if node == self.startNode or node == self.endNode:
            return attributesUnion
        flag = False
        for child in node.children:
            if (child != self.endNode):
                if not flag and child != self.endNode:
                    attributesUnion = set(child.attributes)
                    flag = True
                elif child != self.endNode:
                    attributesUnion &= set(child.attributes)
        attributesUnion -= set(node.attributes)
        return attributesUnion

    def optimizeMultipleToHierarchial(self):
        for node in self.graph:
            attributeIntersection = self.getChildrenAttributeIntersection(node)
            if attributeIntersection:
                for parent in self.graph:
                    if parent is not node:
                        if parent is not self.startNode and parent is not self.endNode and \
                                set(parent.attributes).issubset(attributeIntersection):
                            node.attributes.extend(list(parent.attributes))
                            parent.connectWithChild(node)

    def optimizeIncoherentToHierarchial(self):
        for parent in self.graph:
            for child in self.graph:
                if parent is not child and set(parent.attributes).issubset(child.attributes):
                    if child not in parent.children:
                        child.connectWithParent(parent)
                        # parent.clearFastLinks()
                        # child.clearFastLinks()

    def clearSingleChildLinks(self):
        for node in self.graph:
            if not node.isConcept and len(node.children) == 1 and node.children[0] != self.endNode:
                child = node.children[0]
                if node.isAttributeEntry:
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
        self.optimizeMultipleToHierarchial()
        self.clearTransitivePaths()
        self.optimizeIncoherentToHierarchial()
        self.clearTransitivePaths()
        print("hello")
        self.clearSingleChildLinks()
        # self.optimizeIncoherentToHierarchial()
        print("hello")

        # for x in range(0, len(self.bipartiteGroups)):
        #     object = "".join(str(m) for m in sorted(self.bipartiteGroups[x][0]))
        #     attribute = "".join(str(m) for m in sorted(self.bipartiteGroups[x][1]))
        #     self.conceptDict[object] = set(self.bipartiteGroups[x][1])
        #     self.conceptDict[attribute] = set(self.bipartiteGroups[x][0])
        #
        # self.bipartiteGroups.sort(key=lambda a: len(a[0]))
        # return self.conceptDict

    def removeUnclosed(self):
        flist = []
        for x in range(0, len(self.bipartiteGroups)):
            list_attr = []
            list_obj = []
            for y in range(0, len(self.bipartiteGroups[x][0])):
                if list_attr == []:
                    list_attr = self.dictionaryGM[self.bipartiteGroups[x][0][y]]
                else:
                    list_attr = list(set(list_attr).intersection(set(self.dictionaryGM[self.bipartiteGroups[x][0][y]])))

            for z in range(0, len(self.bipartiteGroups[x][1])):
                if not list_obj:
                    list_obj = self.dictionaryGM[self.bipartiteGroups[x][1][z]]
                else:
                    list_obj = list(
                        set(list_obj).intersection(set(self.dictionaryGM[self.bipartiteGroups[x][1][z]])))
            # print ("printing both list for ",  x,  list_top,  list_bottom)
            if set(list_attr) == set(self.bipartiteGroups[x][1]) and set(list_obj) == set(self.bipartiteGroups[x][0]):
                flist.append(self.bipartiteGroups[x])
        self.bipartiteGroups = flist
        return self.bipartiteGroups

    # Need improvements
    def buildLatticeGraph(self):

        hasSuccessor = []
        hasPredecessor = []
        for x in range(0, len(self.bipartiteGroups)):
            nodeName = "".join(str(m) for m in self.bipartiteGroups[x][0]) + ", " + "".join(
                str(m) for m in self.bipartiteGroups[x][1])
            self.graphnx.add_node(nodeName)

        for x in range(0, len(self.bipartiteGroups)):
            for y in range(x + 1, len(self.bipartiteGroups)):
                if set(self.bipartiteGroups[x][0]).issubset(set(self.bipartiteGroups[y][0])):
                    nodeName1 = "".join(str(m) for m in self.bipartiteGroups[x][0]) + ", " + "".join(
                        str(m) for m in self.bipartiteGroups[x][1])
                    nodeName2 = "".join(str(m) for m in self.bipartiteGroups[y][0]) + ", " + "".join(
                        str(m) for m in self.bipartiteGroups[y][1])
                    self.graphnx.add_edge(nodeName1, nodeName2)
                    hasSuccessor.append(x)
                    hasPredecessor.append(y)

        # Creating the top most and the bottom most node
        list_top = []
        list_bottom = []
        for x in range(0, len(self.attributes)):
            if not list_top:
                list_top = self.dictionaryGM[self.attributes[x]]
            else:
                list_top = list(set(list_top).intersection(set(self.attributes[x])))

        for x in range(0, len(self.objects)):
            if not list_bottom:
                list_bottom = self.dictionaryGM[self.objects[x]]
            else:
                list_bottom = list(set(list_bottom).intersection(set(self.objects[x])))
        if not list_bottom:
            list_bottom = ["null"]
        if not list_top:
            list_top = ["null"]

        # adding them to the graph
        firstNode = "".join(str(m) for m in list_top) + ", " + "".join(str(m) for m in self.attributes)
        # print(firstNode)
        self.graphnx.add_node(firstNode)
        lastNode = "".join(str(m) for m in self.objects) + ", " + "".join(str(m) for m in list_bottom)
        self.graphnx.add_node(lastNode)

        # adding edges to them self.M[x]
        for x in range(0, len(self.bipartiteGroups)):
            if x not in hasSuccessor:
                nodeName = "".join(str(m) for m in self.bipartiteGroups[x][0]) + ", " + "".join(
                    str(m) for m in self.bipartiteGroups[x][1])
                # print(nodeName)
                self.graphnx.add_edge(nodeName, lastNode)

        for x in range(0, len(self.bipartiteGroups)):
            if x not in hasPredecessor:
                nodeName = "".join(str(m) for m in self.bipartiteGroups[x][0]) + ", " + "".join(
                    str(m) for m in self.bipartiteGroups[x][1])
                self.graphnx.add_edge(nodeName, firstNode)
        return self.graphnx

    def queryLattice(self, query):
        self.bipartiteGroups.sort(key=lambda x: len(x[0]))
        key = "".join(str(m) for m in sorted(query.split()))
        if key in self.conceptDict:
            print(', '.join(self.conceptDict[key]), "\n")
        else:
            print("Not present in Concept lattice\n")
        return 0

    def saveLatticeGraph(self, path):
        if not self.graphnx:
            self.buildLatticeGraph()

        nx.draw(self.graphnx, nx.kamada_kawai_layout(self.graphnx), with_labels=True,
                node_color=range(self.graphnx.number_of_nodes()),
                cmap=plt.cm.Blues)
        plt.axis('off')
        plt.savefig(path)

    def saveLattice(self, path):
        np.savez(path, I=self.data, M=self.attributes, G=self.objects, dictionaryGM=self.dictionaryGM,
                 conceptDict=self.conceptDict,
                 bipartiteGroups=self.bipartiteGroups)

    def loadLattice(self, path):
        data = np.load(path + ".npz")
        self.data = data['I'].tolist()
        self.objects = data['G'].tolist()
        self.attributes = data['M'].tolist()
        self.dictionaryGM = data['dictionaryGM'].tolist()
        self.conceptDict = data['conceptDict'].tolist()
        self.bipartiteGroups = data['bipartiteGroups'].tolist()
        return self.conceptDict
