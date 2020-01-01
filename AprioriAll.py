import copy
import csv

def generateData():
    # seq1 = [[30], [30], [90]]
    # seq2 = [[10, 20], [30], [30, 60, 70],[90]]
    # seq3 = [[30, 50, 70], ]
    # seq4 = [[30], [40, 70], [90]]
    # seq5 = [[90], ]
    # dataSet = [seq1, seq2, seq3, seq4, seq5]

    with open('superstore_dataset.csv',encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        # print(headers)
        dataSet={}
        # count=0
        for row in reader:
            # count+=1
            if row[0] not in dataSet:
                event={}
                event[row[1]]=[row[2]]
                dataSet[row[0]]=event
            else:
                if row[1] not in dataSet[row[0]]:
                    dataSet[row[0]][row[1]]=[row[2]]
                else:
                    dataSet[row[0]][row[1]].append(row[2])
            # if count == 1000:
            #     break

        # for item in dataSet:
        #     print(item,dataSet[item])
        DataSet=[]
        for customer in dataSet:
            seq=[]
            for date in dataSet[customer]:
                seq.append(dataSet[customer][date])
            DataSet.append(seq)

        # for item in DataSet:
        #     print(item)
        # print()
        min_support_count = 10
        min_confidence=0.85
        return DataSet,min_support_count,min_confidence


# SCk是频繁项集的Ck, SLk是频繁项集的Lk
def createSC1(dataSet):
    SC1=[]
    for seq in dataSet:
        for event in seq:
            for item in event:
                if [item] not in SC1:
                    SC1.append([item])
    SC1.sort()
    # print("从数据集中生成的SC1",SC1)
    return SC1


def generateSLk(dataSet,SCk,min_support_count):
    SLK_count={}
    for item in SCk:
        SLK_count[tuple(item)]=0
    for item in SCk:
        for seq in dataSet:
            for event in seq:
                if set(item)<=set(event):
                    SLK_count[tuple(item)]+=1
    # print("项计数:",SLK_count)
    for item in list(SLK_count):
        if SLK_count[item]<min_support_count:
            del SLK_count[item]
    # SLK_count = sorted(SLK_count.items(),key=lambda x:x[1],reverse=True)
    SLK_support = {}
    for item in SLK_count:
        SLK_support[item] = SLK_count[item]
    # print("排序剪枝后, 频繁k-项集计数:", SLK_support)
    SLK = [list(x) for x in SLK_count]
    # print("频繁k-项集:",SLK)
    # print()
    return SLK, SLK_support


# 两个SLk生成一个nextSCk
# [[40],[70],[80],[90]] # 频繁1-项集
def generateNextSCk(SLk,k):
    SCk = []
    lenSLk = len(SLk)
    for i in range(lenSLk):
        for j in range(i + 1, lenSLk):
            # 前k-2项相同时，将两个集合合并
            L1 = SLk[i][:k - 2]  # 分片
            L2 = SLk[j][:k - 2]
            # L1.sort()
            # L2.sort()
            if L1 == L2:
                SCk.append(SLk[i]+SLk[j][k-2:])
                # SCk.append(list(set(SLk[i])| set(SLk[j])))  # 求集合的并集并添加到SCk中
    # print("频繁k-项连接后生成的SCk+1:",SCk)
    return SCk


def createSL(dataSet,min_support_count, SLK1,SLK_support):
    SL = [SLK1]  # [
                #   [[40],[70],[80],[90]], # 频繁1-项集
                # ]
    k = 2
    while len(SL[k - 2]) > 0:
        nextSCk = generateNextSCk(SL[k - 2], k)
        SLk, supK = generateSLk(dataSet, nextSCk, min_support_count)
        SLK_support.update(supK)
        if len(SLk) == 0:
            break
        SL.append(SLk)
        k += 1
    L = []
    for SLk in SL:
        for item in SLk:
            L.append(item)
    # print("频繁项集:", L)
    # print("频繁项集的支持度:", SLK_support)
    # print()
    return L

# 转换阶段
def transformDataSet(dataSet,L):
    for (idx,seq) in enumerate(dataSet[::-1]):
        for (index,event) in enumerate(seq[::-1]):
            fItems=[] # 包含于该事件中的所有频繁项集
            for fItem in L:
                if set(event) >= set(fItem):
                    fItems.append(fItem)
            if len(fItems)==0:
                del seq[index] # 如果一个事件不包含任何频繁项集，则将其删除
            elif len(fItems)>0:
                seq[index]=[x for x in fItems] # 每个事件替换成包含于该事件中的所有频繁项集
        seq.reverse()
        if len(seq)==0:
            del dataSet[idx] # 如果一个客户序列不包含任何频繁项集，则将该序列删除
    # print("把商品映射成整数")
    table={}
    rTable={}
    for (index,fItem) in enumerate(L):
        table[tuple(fItem)]=index+1
        rTable[index+1]=fItem
        # print(fItem,"->",index+1)
    # print(rTable)
    # print()
    for seq in dataSet:
        for event in seq:
            for(idx,item) in enumerate(event):
                event[idx]=table[tuple(item)]

    # print("转换后的新数据集")
    # for seq in dataSet:
    #     print("seq:",seq)
    # print()

    for (index,item) in enumerate(L):
        L[index]=[table[tuple(item)]]

    # print("转换后的频繁1-候选序列:",L)
    # print()
    return dataSet,L,rTable

#判断子序列
def isSub(subseq,seq):
    lenSub=len(subseq)
    lenS=len(seq)
    if lenSub>lenS:
        return False
    if lenSub==1:
        return any([subseq[0] in event for event in seq])
    if lenSub>1:
        head=[subseq[0] in event for event in seq]
        if any(head):
            split = head.index(True)
            return isSub(subseq[1:],seq[split+1:])
        else:
            return False


def generateLk(dataSet,Ck,min_support_count):
    LK_count = {}
    for subseq in Ck:
        LK_count[tuple(subseq)] = 0
    for subseq in Ck:
        for seq in dataSet:
            if isSub(subseq,seq):
                LK_count[tuple(subseq)] += 1
    # print("项计数:", LK_count)
    for item in list(LK_count):
        if LK_count[item] < min_support_count:
            del LK_count[item]
    # LK_count = sorted(LK_count.items(), key=lambda x: x[1], reverse=True)
    # print("项计数:", LK_count)
    LK_support = {}
    for item in LK_count:
        LK_support[item] = LK_count[item]
    # print("排序剪枝后, 频繁k-序列计数:", LK_support)
    LK = [list(x) for x in LK_count]
    # print("频繁k-序列:", LK)
    # print()
    return LK, LK_support

# 频繁序列连接
def generateNextCk(Lk,k):
    nextCk = []
    lenLk = len(Lk)
    for i in range(lenLk):
        for j in range(i + 1, lenLk):
            # 前k-2项相同时，将两个集合合并
            L1 = Lk[i][:k - 2]  # 分片
            L2 = Lk[j][:k - 2]
            if L1 == L2:
                nextCk.append(Lk[i]+Lk[j][k-2:])  # 连接
                nextCk.append(Lk[j]+Lk[i][k-2:])
    # print("频繁k-序列连接后生成的Ck+1:", nextCk)
    return nextCk


def createL(dataSet,min_support_count,L1,LK_support):
    L=[L1]
    k=2
    while len(L[k - 2]) > 0:
        nextSCk = generateNextCk(L[k - 2], k)
        Lk, supK = generateLk(dataSet, nextSCk, min_support_count)
        LK_support.update(supK)
        if len(Lk) == 0:
            break
        L.append(Lk)
        k += 1
    # LL=[]
    # for lk in L:
    #     for item in lk:
    #         LL.append(item)
    # print("频繁序列:",LL)
    # print("频繁序列",L)
    # print("频繁序列支持度:",LK_support)
    # print()
    return L,LK_support

def isSub2(sub,s):
    lenSub = len(sub)
    lenS = len(s)
    if lenSub > lenS:
        return False
    if lenSub == 1:
        return any([sub[0] == e for e in s])
    if lenSub > 1:
        head = [sub[0] == e for e in s]
        if any(head):
            split = head.index(True)
            return isSub2(sub[1:], s[split + 1:])
        else:
            return False

def maximize(L0,LK_support0):
    L=copy.deepcopy(L0)
    LK_support=copy.deepcopy(LK_support0)
    lenL=len(L)
    for i in range(lenL-1,-1,-1):
        for j in range(0,i):
            for p in L[i]:
                for q in L[j][::-1]:
                    if isSub2(q,p):
                        L[j].remove(q)
                        LK_support.pop(tuple(q))
    for i in range(lenL-1,-1,-1):
        for j in range(0, i):
            if len(L[j])==0:
                del L[j]
    LL=[]
    for k in L:
        for item in k:
            LL.append(item)
    # print("最大化序列:",LL)
    # print("最大化序列支持度",LK_support)
    # print()
    return LL,LK_support

def generateRule(L,LK_support,maxL,maxLK_support,min_confidence):
    lenMax=len(maxL[-1])
    R=[]
    if lenMax <= 1:
        return R
    else:
        for seq in maxL:
            for i in range(0,lenMax-1):
                for sub in L[i]:
                    if len(sub)<len(seq) and isSub2(sub,seq):
                        if maxLK_support[tuple(seq)]/LK_support[tuple(sub)] >= min_confidence:
                            R.append((copy.deepcopy(sub),copy.deepcopy(seq)))
    # print("生成的强关联规则:",R)
    # print()
    return R

def printR(R,table):
    for i in range(len(R)):
        for j in range(len(R[i][0])):
            R[i][0][j]=table[R[i][0][j]]
        for k in range(len(R[i][1])):
            R[i][1][k]=table[R[i][1][k]]
    # 输出规则
    print("输出规则")
    for r in R:
        print("{} --> {}".format(r[0],r[1]))
    # print(R)

def main():
    # 数据集和最小支持度计数和最小置信度
    dataSet,min_support_count,min_confidence=generateData()
    # 生成频繁1-项集的C1
    SC1=createSC1(dataSet)
    # 生成频繁1-项集和支持度计数
    SLK1,SLK_support=generateSLk(dataSet,SC1,min_support_count)
    # 生成频繁项集
    SL=createSL(dataSet,min_support_count,SLK1,SLK_support)
    # 转换阶段
    dataSet,C1,table=transformDataSet(dataSet,SL)
    # 生成频繁1-序列和支持度计数
    LK1,LK_support=generateLk(dataSet,C1,min_support_count)
    # 生成频繁序列
    L,LK_support=createL(dataSet,min_support_count,LK1,LK_support)
    # 最大化
    maxL,maxLK_support=maximize(L,LK_support)
    # 生成强关联规则
    R=generateRule(L,LK_support,maxL,maxLK_support,min_confidence)
    # 输出关联规则
    printR(R,table)

if __name__=="__main__":
    main()