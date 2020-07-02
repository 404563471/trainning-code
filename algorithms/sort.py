## 经典洗牌算法（KD：Knuth_Durstenfeld)
import random

def swap(arr, i, j):
    '''
    交换两个值
    '''
    arr[i], arr[j] = arr[j], arr[i]

def kd(arr):
    '''
    算法时间复杂度 O（n）
    属于原地打乱顺序的一种，不需要额外开辟存储打乱后的数组的空间
    '''
    i = len(arr)
    for i in range(i - 1, -1, -1):
        swap(arr, i, random.randint(0, i))
    return arr


## 冒泡排序（Bubble Sort）
def bubble_sort(arr):
    for i in range(len(arr) - 1):
        # 记录最小数的索引
        minIndex = i
        for j in range(i + 1, len(arr)):
            if arr[j] < arr[minIndex]:
                minIndex = j
                # i 不是最小数时，将 i 和最小数进行交换
        if i != minIndex:
            arr[i], arr[minIndex] = arr[minIndex], arr[i]
    return arr


## 选择排序
def selection_sort(arr):
    for i in range(len(arr) - 1):
        # 记录最小数的索引
        minIndex = i
        for j in range(i + 1, len(arr)):
            if arr[j] < arr[minIndex]:
                minIndex = j
             # i 不是最小数时，将 i 和最小数进行交换
        if i != minIndex:
            arr[i], arr[minIndex] = arr[minIndex], arr[i]
    return arr
