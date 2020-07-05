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