import numpy as np
import networkx as nx
from matplotlib import pyplot as plt


class FCA:
    """
    I - context
    G - objects
    M - attributes
    """

    def __init__(self,data,obj,attr):
        # self.I = np.array(data)
        # self.G = np.array(obj)
        # self.M = np.array(attr)
        self.I = data
        self.G = obj
        self.M = attr
        self.lattice = []
        self.adj = {}
        self.dictionaryGM = {}
        self.bipartiteGroups = []
        self.graph = nx.Graph()
        self.conceptDict = {}

    def getBipartiteGroups(self):
        cList = []
        aLen = len(self.I)
        bLen = len(self.I[0])
        # printMat(aMat)
        # print(aLen,bLen," are aLen and bLen\n\n")
        for x in range(0,aLen):
            tmpList = []
            tmpObj = [self.G[x]]

            for y in range(0,bLen):
                if self.I[x][y] == '1':
                    tmpList.append(self.M[y])

            tmp = tmpObj,tmpList
            self.dictionaryGM[self.G[x]] = tmpList
            cList.append(tmp)

        for x in range(0,bLen):
            tmpList = []
            tmpattr = [self.M[x]]

            for y in range(0,aLen):
                if self.I[y][x] == '1':
                    tmpList.append(self.G[y])

            tmp = tmpList,tmpattr
            self.dictionaryGM[self.M[x]] = tmpList
            cList.append(tmp)
        self.bipartiteGroups = cList
        return self.bipartiteGroups

    def removeUnclosed(self):
        flist = []
        for x in range(0,len(self.bipartiteGroups)):
            list_top = []
            list_bottom = []
            for y in range(0,len(self.bipartiteGroups[x][0])):
                if list_top == []:
                    list_top = self.dictionaryGM[self.bipartiteGroups[x][0][y]]
                else:
                    list_top = list(set(list_top).intersection(set(self.dictionaryGM[self.bipartiteGroups[x][0][y]])))

            for z in range(0,len(self.bipartiteGroups[x][1])):
                if not list_bottom:
                    list_bottom = self.dictionaryGM[self.bipartiteGroups[x][1][z]]
                else:
                    list_bottom = list(
                        set(list_bottom).intersection(set(self.dictionaryGM[self.bipartiteGroups[x][1][z]])))
            #       print ("printing both list for ",  x,  list_top,  list_bottom)
            if set(list_top) == set(self.bipartiteGroups[x][1]) and set(list_bottom) == set(self.bipartiteGroups[x][0]):
                flist.append(self.bipartiteGroups[x])
        self.bipartiteGroups = flist
        return flist

    def condenseList(self):
        clist = []
        toSkip = []
        for x in range(0,len(self.bipartiteGroups)):
            if x in toSkip:
                continue
            matched = 0
            for y in range(x + 1,len(self.bipartiteGroups)):
                if y in toSkip:
                    continue
                if set(self.bipartiteGroups[x][0]) == set(self.bipartiteGroups[y][0]):
                    tmpTuple = self.bipartiteGroups[x][0],list(
                        set(self.bipartiteGroups[x][1]).union(set(self.bipartiteGroups[y][1])))
                    clist.append(tmpTuple)
                    toSkip.append(y)
                    matched = 1
                    break
                elif set(self.bipartiteGroups[x][1]) == set(self.bipartiteGroups[y][1]):
                    tmpTuple = list(set(self.bipartiteGroups[x][0]).union(set(self.bipartiteGroups[y][0]))), \
                               self.bipartiteGroups[x][1]
                    clist.append(tmpTuple)
                    toSkip.append(y)
                    matched = 1
                    break
            if matched == 0:
                clist.append(self.bipartiteGroups[x])

        return clist

    def removeUnclosed(self):
        flist = []
        for x in range(0,len(self.bipartiteGroups)):
            list_top = []
            list_bottom = []
            for y in range(0,len(self.bipartiteGroups[x][0])):
                if list_top == []:
                    list_top = self.dictionaryGM[self.bipartiteGroups[x][0][y]]
                else:
                    list_top = list(set(list_top).intersection(set(self.dictionaryGM[self.bipartiteGroups[x][0][y]])))

            for z in range(0,len(self.bipartiteGroups[x][1])):
                if not list_bottom:
                    list_bottom = self.dictionaryGM[self.bipartiteGroups[x][1][z]]
                else:
                    list_bottom = list(
                        set(list_bottom).intersection(set(self.dictionaryGM[self.bipartiteGroups[x][1][z]])))
            #       print ("printing both list for ",  x,  list_top,  list_bottom)
            if set(list_top) == set(self.bipartiteGroups[x][1]) and set(list_bottom) == set(self.bipartiteGroups[x][0]):
                flist.append(self.bipartiteGroups[x])
        self.bipartiteGroups = flist
        return self.bipartiteGroups

    def buildLatticeGraph(self):

        hasSuccessor = []
        hasPredecessor = []
        for x in range(0,len(self.bipartiteGroups)):
            nodeName = "".join(str(m) for m in self.bipartiteGroups[x][0]) + ", " + "".join(
                str(m) for m in self.bipartiteGroups[x][1])
            self.graph.add_node(nodeName)

        for x in range(0,len(self.bipartiteGroups)):
            for y in range(x + 1,len(self.bipartiteGroups)):
                if set(self.bipartiteGroups[x][0]).issubset(set(self.bipartiteGroups[y][0])):
                    nodeName1 = "".join(str(m) for m in self.bipartiteGroups[x][0]) + ", " + "".join(
                        str(m) for m in self.bipartiteGroups[x][1])
                    nodeName2 = "".join(str(m) for m in self.bipartiteGroups[y][0]) + ", " + "".join(
                        str(m) for m in self.bipartiteGroups[y][1])
                    self.graph.add_edge(nodeName1,nodeName2)
                    hasSuccessor.append(x)
                    hasPredecessor.append(y)

        # Creating the top most and the bottom most node
        list_top = []
        list_bottom = []
        for x in range(0,len(self.M)):
            if not list_top:
                list_top = self.dictionaryGM[self.M[x]]
            else:
                list_top = list(set(list_top).intersection(set(self.M[x])))

        for x in range(0,len(self.G)):
            if not list_bottom:
                list_bottom = self.dictionaryGM[self.G[x]]
            else:
                list_bottom = list(set(list_bottom).intersection(set(self.G[x])))
        if not list_bottom:
            list_bottom = ["null"]
        if not list_top:
            list_top = ["null"]

        # adding them to the graph
        firstNode = "".join(str(m) for m in list_top) + ", " + "".join(str(m) for m in self.M)
        # print(firstNode)
        self.graph.add_node(firstNode)
        lastNode = "".join(str(m) for m in self.G) + ", " + "".join(str(m) for m in list_bottom)
        self.graph.add_node(lastNode)

        # adding edges to themself.M[x]
        for x in range(0,len(self.bipartiteGroups)):
            if x not in hasSuccessor:
                nodeName = "".join(str(m) for m in self.bipartiteGroups[x][0]) + ", " + "".join(
                    str(m) for m in self.bipartiteGroups[x][1])
                # print(nodeName)
                self.graph.add_edge(nodeName,lastNode)

        for x in range(0,len(self.bipartiteGroups)):
            if x not in hasPredecessor:
                nodeName = "".join(str(m) for m in self.bipartiteGroups[x][0]) + ", " + "".join(
                    str(m) for m in self.bipartiteGroups[x][1])
                self.graph.add_edge(nodeName,firstNode)
        return self.graph

    def queryLattice(self,query):
        self.bipartiteGroups.sort(key=lambda x: len(x[0]))
        key = "".join(str(m) for m in sorted(query.split()))
        if key in self.conceptDict:
            print(', '.join(self.conceptDict[key]),"\n")
        else:
            print("Not present in Concept lattice\n")
        return 0

    def buildLattice(self):
        self.getBipartiteGroups()
        bCListSize = len(self.bipartiteGroups)
        bCListSizeCondensed = -1
        # Condense bipartite cliques until no change
        while bCListSize != bCListSizeCondensed:
            bCListSize = len(self.bipartiteGroups)
            self.bipartiteGroups = self.condenseList()
            bCListSizeCondensed = len(self.bipartiteGroups)

        # filter concepts
        self.removeUnclosed()

        for x in range(0,len(self.bipartiteGroups)):
            object = "".join(str(m) for m in sorted(self.bipartiteGroups[x][0]))
            attribute = "".join(str(m) for m in sorted(self.bipartiteGroups[x][1]))
            self.conceptDict[object] = set(self.bipartiteGroups[x][1])
            self.conceptDict[attribute] = set(self.bipartiteGroups[x][0])

        self.bipartiteGroups.sort(key=lambda a: len(a[0]))
        return self.conceptDict

    def saveLatticeGraph(self,path):
        if not self.graph:
            self.buildLatticeGraph()

        nx.draw(self.graph,nx.kamada_kawai_layout(self.graph),with_labels=True,
                node_color=range(self.graph.number_of_nodes()),
                cmap=plt.cm.Blues)
        plt.axis('off')
        plt.savefig(path)

    def saveLattice(self,path):
        np.savez(path,I=self.I,M=self.M,G=self.G,dictionaryGM=self.dictionaryGM,conceptDict=self.conceptDict,
                 bipartiteGroups=self.bipartiteGroups)

    def loadLattice(self,path):
        data = np.load(path + ".npz")
        self.I = data['I'].tolist()
        self.G = data['G'].tolist()
        self.M = data['M'].tolist()
        self.dictionaryGM = data['dictionaryGM'].tolist()
        self.conceptDict = data['conceptDict'].tolist()
        self.bipartiteGroups = data['bipartiteGroups'].tolist()
        return self.conceptDict
