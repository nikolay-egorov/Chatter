import numpy as np
import networkx as nx
from matplotlib import pyplot as plt


class Node:
    def __init__(self, attributes, objects = None):
        self.attributes = attributes
        self.objects = objects
    def __eq__(self, other):
        if (isinstance(other, Node)):
            return self.attributes == other.attributes


class FCA:
    def __init__(self, data, objects, attributes):
        self.data = data
        self.objects = objects
        self.attributes = attributes
        self.lattice = []
        self.adj = {}
        self.dictionaryGM = {}
        self.bipartiteGroups = []
        self.graphnx = nx.Graph()
        self.conceptDict = {}
        self.startNode = Node(None, None)
        self.graph = [self.startNode]

    def addConceptNodes(self):
        objectsLen = len(self.objects)
        attributesLen = len(self.attributes)

        for i in range(0, objectsLen):
            tempObjects = [self.objects[j] for j in range(0, objectsLen) if self.data[j] == self.data[i]]
            tempAttributes = [self.attributes[j] for j in range(0, attributesLen) if self.data[i][j] == '1']
            node = Node(tempObjects, tempAttributes)
            if (node not in self.graph):
               self.graph.append(node)

        for j in range(0, attributesLen):
            tmpAttr = [self.attributes[j]]
            tempAttributes = [self.objects[i] for i in range(0, objectsLen) if self.data[i][j] == '1']
            temp = tempAttributes, tmpAttr
            self.bipartiteGroups.append(temp)

    def addAttributeNodes(self):
        lastSize = len(self.bipartiteGroups)
        while True:
            newBipartiteGroups = []
            objectsLen = len(self.objects)
            attributesLen = len(self.attributes)

            for i in range(0, len(self.bipartiteGroups)):
                g1 = self.bipartiteGroups[i]
                tempObjects = set(g1[0])
                tempAttributes = set(g1[1])
                for j in range(0, attributesLen):
                    g2 = self.bipartiteGroups[j]
                    if tempAttributes == set(g2[1]):
                        tempObjects = tempObjects.union(set(g2[0]))
                tempGroup = list(tempObjects), list(tempAttributes)
                if (not (tempGroup in newBipartiteGroups)):
                    newBipartiteGroups.append(tempGroup)

            self.bipartiteGroups = newBipartiteGroups
            if lastSize == len(self.bipartiteGroups):
                break
            else:
                lastSize = len(self.bipartiteGroups)

    # def buildGraph(self):



    def buildLattice(self):
        self.addConceptNodes()
        self.addAttributeNodes()
        self.buildGraph()


        for x in range(0, len(self.bipartiteGroups)):
            object = "".join(str(m) for m in sorted(self.bipartiteGroups[x][0]))
            attribute = "".join(str(m) for m in sorted(self.bipartiteGroups[x][1]))
            self.conceptDict[object] = set(self.bipartiteGroups[x][1])
            self.conceptDict[attribute] = set(self.bipartiteGroups[x][0])

        self.bipartiteGroups.sort(key=lambda a: len(a[0]))
        return self.conceptDict


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
        np.savez(path, I=self.data, M=self.attributes, G=self.objects, dictionaryGM=self.dictionaryGM, conceptDict=self.conceptDict,
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
