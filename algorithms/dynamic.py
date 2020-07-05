## 找零问题

## 1. 贪心算法， 把最大的返回最多个数，以此递减
def recMC1(money, coinList=[100, 50, 20, 10, 5, 2, 1]):
    if money in coinList :
        return {money : 1}
    else : 
        coinList = sorted([coin for coin in coinList if coin < money], reverse=True)
        coinNum = []
        for coin in coinList :
            coinNum.append(money // coin)
            money %= coin
        return dict(zip(coinList, coinNum))
        
## 2. 动态规划方法

def dpMC(change, coinValueList=[100, 50, 20, 10, 5, 2, 1]):
    # 从一分开始到change逐个计算最少硬币数
    minCoins = [0] * (change+1)
    for cents in range(1, change+1):
        # 初始化一个最大值
        coinCount = cents
        # 减去每个硬币，向后查找最少硬币数，同时记录总的最少数
        for j in [c for c in coinValueList if c <= cents]:
            coinCount = min(minCoins[cents - j] + 1, coinCount)
        # 得到当前最少硬币数，并记录在表中
        minCoins[cents] = coinCount
    # 返回最后一个结果
    return minCoins[change]

## 盗宝问题


## 两序列比对
import numpy as np

class Match:
    def __init__(self,p0,p1,p2):
        self.p0, self.p1, self.p2 = p0, p1, p2
        self.isGlobal = True

    def credit(self, c1, c2):
        if c1 == '-' or c2 == '-':
            return self.p2
        if c1 == c2:
            return self.p0
        else:
            return self.p1

    def resetScores(self, p0, p1, p2):
        assert type(p0) == int and type(p0) == type(p1) and type(p1) == type(p2)
        self.p0, self.p1, self.p2 = p0, p1, p2

    def setGlobal(self, yes):
        assert type(yes) == bool
        self.isGlobal = yes


    def match(self, s, t):
        m = len(s)
        n = len(t)
        if self.isGlobal:
            p2 = self.p2
            A = np.empty((m+1,n+1))
            A[0][0] = 0 #初始化左上角
            
            for k in range(1, n+1): #初始化第0行第0列
                A[0][k] = A[0][k-1] + p2
            for k in range(1, m+1):
                A[k][0] = A[k-1][0] + p2
            maxFunc = max
        else:
            A = np.zeros((m+1,n+1))
            maxFunc = lambda x, y, z: max(0, max(x,y,z))

        maxLocal = 0
        for i in range(1, m+1): #行
            for j in range(1, n+1): #列
                replaceOrEqual = A[i-1][j-1] + self.credit(s[i-1],t[j-1])
                deletej = A[i][j-1] + self.credit('-',t[j-1])
                insertj = A[i-1][j] + self.credit(s[i-1],'-')
                A[i][j] = maxFunc(replaceOrEqual, deletej, insertj)
                maxLocal = max(A[i][j], maxLocal)
        if self.isGlobal:
            print(A[m,n])
        else:
            print(maxLocal)