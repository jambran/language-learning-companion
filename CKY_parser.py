
from math import *
from CKY_grammar import *

class Item:
    def __init__(self, i, j, label, logProb=0, backPtrLeft=None, backPtrRight=None):
        self.startPos = i
        self.endPos = j
        self.label = label
        self.logProb = logProb
        self.backPtrLeft = backPtrLeft
        self.backPtrRight = backPtrRight

    def get_tree(self):
        if self.backPtrLeft is None:    # this is a terminal rule
            return self.label
        elif self.backPtrRight is None: # this is a unary production
            return Tree(self.label, [self.backPtrLeft.get_tree()])
        else:                           # this is a binary production
            return Tree(self.label, [self.backPtrLeft.get_tree(), self.backPtrRight.get_tree()])

    def __str__(self):
        return self.label + "[" + str(self.startPos) + ':' + str(self.endPos) + "]"


class Chart:
    def __init__(self, pruningPercent=None):
        self.chart = {}
        self.greatestLogProb = {}
        self.pruningPercent = pruningPercent

    def iter_cell(self, i, j):
        if i not in self.chart: return
        if j not in self.chart[i]: return
        for item in self.chart[i][j].values():
            yield item

    def best_in_cell(self, i, j, desiredLabel=None):
        bestItem = None
        bestLogProb = float('-inf')
        for item in self.iter_cell(i, j):
            if desiredLabel is not None and desiredLabel != item.label: continue
            if item.logProb > bestLogProb:
                bestItem    = item
                bestLogProb = item.logProb
        return bestItem

    def prune_cell(self, i, j):
        # kill anything worse than pruningPercent times the probability of the best thing
        if self.pruningPercent is None: return
        
        bestItem = self.best_in_cell(i, j)
        if bestItem is None: return

        threshold = log(self.pruningPercent) + bestItem.logProb
        toRemove = []
        for item in self.iter_cell(i,j):
            if item.logProb < threshold:
                toRemove.append(item.label)

        for label in toRemove:
            self.remove(i, j, label)

    def remove(self, i, j, label):
        if i not in self.chart: return
        if j not in self.chart[i]: return
        if label not in self.chart[i][j]: return
        del self.chart[i][j][label]

    def add(self, item):
        i = item.startPos
        j = item.endPos
        if i not in self.chart:
            self.chart[i] = {}
            self.greatestLogProb[i] = {}
        if j not in self.chart[i]:
            self.chart[i][j] = {}
            self.greatestLogProb[i][j] = float('-inf')
            
        # only add if we don't already have a better version
        shouldAdd = True
        if item.label in self.chart[i][j]:
            # easy case: if we're not better, we shouldn't add
            if item.logProb <= self.chart[i][j][item.label].logProb:
                shouldAdd = False

            # pruning case: if we're not better than the best*pruningPercent, we shouldn't add
            if self.pruningPercent is not None and item.logProb < log(self.pruningPercent) + self.greatestLogProb[i][j]:
                shouldAdd = False

        if shouldAdd:
            self.chart[i][j][item.label] = item
            if item.logProb > self.greatestLogProb[i][j]:
                self.greatestLogProb[i][j] = item.logProb

        return shouldAdd

def cky(pcfg, sent, pruningPercent=None):
    N = len(sent)

    # chart[i][j] holds all ways to parse the string
    # sent[i]... sent[j] inclusive
    chart = Chart(pruningPercent)

    # base case: fill in chart for each position's word
    for i in range(N):
        item = Item(i, i+1, sent[i], logProb=0)   # logProb=0 means probability=1
        chart.add(item)

    # base case: unary rules -- need to be sure we don't loop!
    for i in range(N):
        while True:
            toAdd = []
            for item in chart.iter_cell(i, i+1):
                for lhs,ruleProb in pcfg.iter_unary_rules_on_rhs(item.label):
                    newItem = Item(i, i+1, lhs, item.logProb + log(ruleProb), item)
                    # print("UNARY ", item.get_tree())
                    toAdd.append(newItem)

            anyAdded = False
            for item in toAdd:
                if chart.add(item):
                    anyAdded = True
                
            if not anyAdded:
                break

        chart.prune_cell(i, i+1)

    # recursive case
    for spanSize in range(2,N+1):

        for i in range(N-spanSize+1):
            toAdd = []
            k = i + spanSize
            for j in range(i+1, k):
                # consider creating a cell spanning i -> k, with a split
                # point at k.  in other words, we want to merge [i,j] with
                # [j+1,k]
                for rhs1 in chart.iter_cell(i,j):
                    for rhs2 in chart.iter_cell(j, k):
                        for lhs,ruleProb in pcfg.iter_binary_rules_on_rhs(rhs1.label, rhs2.label):
                            # make a new item
                            item = Item(i, k, lhs, rhs1.logProb + rhs2.logProb + log(ruleProb), rhs1, rhs2)
                            # print("BINARY "+str(i)+" "+str(j)+" "+str(k),item.get_tree())
                            chart.add(item)
                            # toAdd.append(item)

            # try unary rules
            for rhs in chart.iter_cell(i,k):
                for lhs,ruleProb in pcfg.iter_unary_rules_on_rhs(rhs.label):
                    newItem = Item(i, k, lhs, rhs.logProb + log(ruleProb), rhs)
                    toAdd.append(newItem)
                    # print("UNARY " , newItem.label)#newItem.get_tree())
                    # chart.add(newItem)
            for item in toAdd:
                chart.add(item)

            # prune the cell
            chart.prune_cell(i, k)
    
    return chart

def parse(pcfg, sent, pruningPercent=None):
    N = len(sent)
    chart = cky(pcfg, sent, pruningPercent)
    top = chart.best_in_cell(0, N, 'TOP')
    if top is None:
        return None
    return top.get_tree()

def evaluateParser(pcfg, filename, pruningPercent=None, horizSize=None, verticSize=1, runFancyCode=False):
    averageAcc = 0.
    totalCount = 0.
    for tree in iterateTreebank(filename, horizSize=horizSize, verticSize=verticSize, runFancyCode=runFancyCode):
        sent = tree.preterminals()
        sys.__stderr__.write('.')
        res  = parse(pcfg, sent, pruningPercent)
        averageAcc += evaluate(debinarizeTree(tree), debinarizeTree(res))
        totalCount += 1.0
    sys.__stderr__.write('\n')
    return averageAcc/totalCount


def reinsertWords(tree, sent):
    def reinsertWords_rec(tree, i):
        for j in range(len(tree)):
            if isinstance(tree[j], Tree):
                i,tree[j] = reinsertWords_rec(tree[j], i)
            else:
                tree[j] = Tree(tree[j], [sent[i]])
                i = i + 1
        return i,tree
    j,tree = reinsertWords_rec(tree, 0)
    return tree

def runParserOnTest(pcfg, testFilename, outputFilename, pruningPercent=None, horizSize=None, verticSize=1, runFancyCode=False):
    h = open(outputFilename, 'w')
    for (sent,tags) in iterateTaggedSentences(testFilename):
        sys.__stderr__.write('.')
        res  = parse(pcfg, tags, pruningPercent)
        if res is None:
            h.write('None\n')
        else:
            h.write(repr(reinsertWords(debinarizeTree(res), sent)))
            h.write('\n')
    sys.__stderr__.write('\n')
        

if __name__ == "__main__":

    testSent = "crea una alarma para las seis menos cinco".split()

    print(testSent)
    print()
    print(parse(fluencyFriendPCFG, testSent))