import glob
import operator
from pathlib import Path
from nltk.stem import PorterStemmer
import itertools
import math
import os


##  Name - Abhishek Ranjan
##  UIN - 657657618
##  NetId - aranja8

"""
def calculateWt(word1, word2, document)
"""
with open('stopwords.txt', 'r') as stopFile:
    stops = stopFile.read().split('\n')

ps = PorterStemmer()

print("\nPut path in format -> dir1/dirn/* \n")
paths = input("Enter the path for Document Dataset(Ending with (*))::\n")

newpath = input("Enter the path for Gold standard Dataset(Ending with (*))::\n")

#paths = 'www (1)/www/abstracts/*'
files = glob.glob(paths)
filteredWords = {}
allWords = {}
FIleInp = []
scoreNgramGraph = {}
MRR_Value = {}
Vocabulary = {}
num = 0
i = 0
"""
Reading Input file
"""
for inputNm in files:
    fileName = inputNm.split(os.sep) 
    filetoOpen = Path(inputNm)
    with open(str(filetoOpen), encoding = "utf8") as file:
        FIleInp = file.read()
        filteredWords[fileName[-1]] = FIleInp
        i += 1
wordGraph = {}
scoreGraph = {}
ngramGraph = {}


"""
Creating Word Graph
"""
for key, val in filteredWords.items():
    wordList = val.split(" ")
    filteredList_temp = []
    allList_temp = []
    wordGraphNode = {}
    prevWord = ""
    dictTemp = {}
    unigram = []
    bigram = []
    trigram = []
    ngram = []
    i = 0
    k = 0
    prevword = ""
    prevprevword = ""
    for word in wordList:
        wordNew = word.split("_")
        if wordNew[0].lower() not in stops and wordNew[1] in ['NN', 'NNS', 'NNP', 'NNPS', 'JJ']:
            
            word = ps.stem(wordNew[0]).lower()
            """
            Creating Vocabulary and Count
            """
            if word not in Vocabulary:
                Vocabulary[word] = 1
            else:
                Vocabulary[word] += 1
            if k == 0:
                unigram.append((word,))
                prevword = word
            elif k == 1:
                unigram.append((word,))
                bigram.append((prevword, word))
                prevprevword = prevword
                prevword = word               
                
            elif k == 2:
                unigram.append((word,))
                bigram.append((prevword, word))
                trigram.append((prevprevword, prevword, word))
                prevprevword = prevword
                prevword = word            
            else:
                unigram.append((word,))
                bigram.append((prevword, word))
                trigram.append((prevprevword, prevword, word))
                prevprevword = prevword
                prevword = word
            k += 1
                
        else:
            k = 0
            prevprevword = ""
            prevword = ""
             
        
        try:
            if wordNew[0].lower() not in stops and wordNew[1] in ['NN', 'NNS', 'NNP', 'NNPS', 'JJ']:
                word = ps.stem(wordNew[0])
                if word not in filteredList_temp:
                    filteredList_temp.append(word.lower())
                    allList_temp.append(word.lower())
                else:
                    allList_temp.append(word.lower())
                dictTemp[i] = 1
                if (i-1) in dictTemp.keys():
                    if(dictTemp[i-1] == 1):
                        if prevWord in wordGraphNode.keys():
                            makeList = []
                            makeList = wordGraphNode[prevWord]
                            makeList.append(word.lower())
                            wordGraphNode[prevWord] = makeList
                        else:
                            makeList = []
                            makeList.append(word.lower())
                            wordGraphNode[prevWord] = makeList
                        if word.lower() in wordGraphNode.keys():
                            makeList = []
                            makeList = wordGraphNode[word.lower()]
                            makeList.append(prevWord)
                            wordGraphNode[word.lower()] = makeList
                        else:
                            makeList = []
                            makeList.append(prevWord)
                            wordGraphNode[word.lower()] = makeList
                prevWord = word.lower()
            else:
                #if word not in allList_temp:
                    #allList_temp.append(word.lower())
                pass
                dictTemp[i] = 2
        except IndexError:
            pass
        i += 1
    ngram = list(itertools.chain(unigram, bigram, trigram))
    ngramGraph[key] = ngram
    newList = []    
    wordGraph[key] = wordGraphNode    
    filteredWords[key] = filteredList_temp
    allWords[key] = allList_temp
    
"""
Creating ScoreGraph with default value
"""

for key, val in  filteredWords.items():
    scoreNode = {}
    for i in range(len(filteredWords[key])):
        scoreNode[i] = 1/len(filteredWords[key])
    scoreGraph[key] = scoreNode


"""
Applying the formula
"""

for key, val in  filteredWords.items():    
    for k in range(10):
        #scoreNode = {}
        nodesum = 0
        for i in range(len(filteredWords[key])):
            #listNeighbours = []
            wij = 0
            wjk = 0
            nodesum = 0
            if filteredWords[key][i] in  wordGraph[key].keys():
                listNeighbours = wordGraph[key][filteredWords[key][i]]
                for item in listNeighbours:
                    wij = listNeighbours.count(item)
                    indexofj = listNeighbours.index(item)
                    nbrsNeighbours = wordGraph[key][item]
                    for subsequentitems in nbrsNeighbours:
                        wjk += nbrsNeighbours.count(subsequentitems)
                    nodesum += ((wij*scoreGraph[key][indexofj])/(wjk)) + ((0.15)*(1/len(filteredWords[key])))
            else:
                wij = 0
                wjk = 1
                nodesum += ((wij*scoreGraph[key][indexofj])/(wjk)) + ((0.15)*(1/len(filteredWords[key])))
            scoreGraph[key][i] = (0.85)*nodesum




    
           
"""
Finding score of n-gram
"""
def findscoreNgram(ngramGraph, scoreGraph):
    for key, val in ngramGraph.items():
        scoreNgramNode = {}
        for item in ngramGraph[key]:
            score = 0
            for word in item:
                indexofword = filteredWords[key].index(word)
                score += scoreGraph[key][indexofword]
            scoreNgramNode[item] = score
        scoreNgramGraph[key] = scoreNgramNode
    return scoreNgramGraph


"""
Sorting the score Graph based on ranking
"""
def sortScoreGraph(scoreNgramGraph):
    sortedscoreNGram = {}
    for key, val in scoreNgramGraph.items():
        sortedlist = sorted(scoreNgramGraph[key].items(), key=operator.itemgetter(1), reverse = True)
        sortedscoreNGram[key] = sortedlist
    return sortedscoreNGram

    
    

"""
Gold path
"""
##newpath = 'www (1)\www\gold\*'
newfiles = glob.glob(newpath)

"""
Finding Gold file Words
"""
def FindGoldattribute():
    goldDict = {}
    for inputdir in newfiles:
        fileName = inputdir.split(os.sep) 
        pathDir = Path(inputdir)
        with open(str(pathDir), encoding = "utf-8") as file:
            FileIn = file.read().strip().split("\n")
            #n = len(FileIn)
            FileOut = []
            for inpWord in FileIn:
                effword = []
                wordNew = inpWord.split(" ")
                for wordtoTest in wordNew:
                    word = ps.stem(wordtoTest).lower()
                    nlist = []
                    nlist.append(word)
                    effword.extend(nlist)
                FileOut.append(effword)
            goldDict[fileName[-1]] = FileOut
    return goldDict
        
##print(sortedscoreNGram[str(10023569)][0][0])        

"""
Calculating MRR
""" 

def findMRR_PRR(goldDict, sortedscoreNGram,op):
    MRR_PRRValue = {}
    for k in range(1,11):
        #num = 0
        mrr_prrDoc = 0
        for key, val in goldDict.items():
            #num += 1
            scoredList = []
            rank = 0
            for n in range(k):
                if ((len(sortedscoreNGram[key]) - 1) >= n):
                    word = sortedscoreNGram[key][n][0]
                    scoredList.append(word)
            for item in scoredList:
                if list(item) in goldDict[key]:
                    rank = scoredList.index(item) + 1
                    break
            if rank == 0:
                mrr_prrDoc += 0
            else:
                mrr_prrDoc += (1/rank)
        MRR_PRRValue[k] = (mrr_prrDoc/num)
        
    if(op == 1):
        
        print("Printing MRR value for Page Rank Algorithm \n")
        for key, value in MRR_PRRValue.items():
            print ("MRR Value for for Page Ranking ranking scheme k="+ str(key) + " is ->"+ str(value) )
        print("\n\n")
        
    else:
        print("Printing MRR value for tf-idf ranking scheme \n")
        for key, value in MRR_PRRValue.items():
            print ("MRR Value for for tf-idf ranking scheme for k="+ str(key) + " is ->"+ str(value))
        print("\n\n")



"""
Finding size of Collection
"""
goldDict = FindGoldattribute()
num = len(goldDict)

"""
Calling functions for Calculating MRR - Page Ranking scheme
"""

scoreNgramGraph = findscoreNgram(ngramGraph, scoreGraph)    
sortedscoreNGram = sortScoreGraph(scoreNgramGraph)
findMRR_PRR(goldDict, sortedscoreNGram,1)

"""
Calculating TF-IDF for Document Set
"""
scoretfidf = {}
for key, value in filteredWords.items():
    #wordList = allWords[key]
    wordList = allWords[key]
    docDict = {}
    scorenode = {}
    for word in wordList:
        if word in docDict:
            docDict[word] += 1
        else:
            docDict[word] = 1    
    for i in range(len(filteredWords[key])):
        tf = docDict[filteredWords[key][i]]/len(allWords[key])
        idf = math.log2(num/Vocabulary[filteredWords[key][i]])
        scorenode[i] = (tf*idf)    
    scoretfidf[key] = scorenode 
        
    
"""
Calling functions for Calculating MRR - Tf-idf weight scheme
"""      
        
scoreNgramGraph = findscoreNgram(ngramGraph, scoretfidf)    
sortedscoreNGram = sortScoreGraph(scoreNgramGraph)
findMRR_PRR(goldDict, sortedscoreNGram,2)  
    
        

        
            
                
    


                    
        
        