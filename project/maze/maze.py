import sys
import matplotlib.pyplot as plt
from random import randint
import numpy as np


sys.setrecursionlimit(WIDTH * HEIGHT)


class Maze:
    def __init__(self, WIDTH=12, HEIGHT=8):
'''探索迷宫
把迷宫分成行列整齐的方格，区分出墙壁和通道。
即每个方格都有行列位置：矩阵，
采用不同字符来分别代表：墙壁，通道，海龟投放点
'''
        self.edgeList = initEdgeList()
        self.visited  = initVisitedList()

        DFS(0, 0, self.edgeList, self.visited)
        self.edgeList.remove((0, 0, 0, 1))
        self.edgeList.remove((self.WIDTH, self.HEIGHT-1, self.WIDTH, self.HEIGHT))

        self.mazeList = np.full((self.WIDTH, self.HEIGHT), [' '], dtype=str)
        for edge in edgeList:
            self.mazeList[ edge[0]:edge[1], edge[2]:edge[3] ] = "+"
        
        self.startRow = 10
        self.startCol = 4

    def initVisitedList():
        visited = []
        for y in range(HEIGHT):
            line = []
            for x in range(WIDTH):
                line.append(False)
            visited.append(line)
        return visited

    def drawLine(x1, y1, x2, y2):
        plt.plot([x1, x2], [y1, y2], color="black")

    def removeLine(x1, y1, x2, y2):
        plt.plot([x1, x2], [y1, y2], color="white")

    def get_edges(x, y):
        result = []
        result.append((x, y, x, y+1))
        result.append((x+1, y, x+1, y+1))
        result.append((x, y, x+1, y))
        result.append((x, y+1, x+1, y+1))

        return result

    def drawCell(x, y):
        edges = get_edges(x, y)
        for item in edges:
            drawLine(item[0], item[1], item[2], item[3])

    def getCommonEdge(cell1_x, cell1_y, cell2_x, cell2_y):
        edges1 = get_edges(cell1_x, cell1_y)
        edges2 = set(get_edges(cell2_x, cell2_y))
        for edge in edges1:
            if edge in edges2:
                return edge
        return None

    def initEdgeList():
        edges = set()
        for x in range(WIDTH):
            for y in range(HEIGHT):
                cellEdges = get_edges(x, y)
                for edge in cellEdges:
                    edges.add(edge)
        return edges

    def isValidPosition(x, y):
        if x < 0 or x >= WIDTH:
            return False
        elif y < 0 or y >= HEIGHT:
            return False
        else:
            return True

    def shuffle(dX, dY):
        for t in range(4):
            i = randint(0, 3)
            j = randint(0, 3)
            dX[i], dX[j] = dX[j], dX[i]
            dY[i], dY[j] = dY[j], dY[i]

    def DFS(X, Y, edgeList, visited):
        dX = [0,  0, -1, 1]
        dY = [-1, 1, 0,  0]
        shuffle(dX, dY)
        for i in range(len(dX)):
            nextX = X + dX[i]
            nextY = Y + dY[i]
            if isValidPosition(nextX, nextY):
                if visited[nextY][nextX] == False :
                    visited[nextY][nextX] = True
                    commonEdge = getCommonEdge(X, Y, nextX, nextY)
                    if commonEdge in edgeList:
                        edgeList.remove(commonEdge)
                    DFS(nextX, nextY, edgeList, visited)


def searchFrom(maze, startRow, startColumn):
    # 1.1 碰到墙壁，返回失败
    maze.updatePosition(startRow, startColumn)
    if maze[startRow][startColumn] == OBSTACLE:
        return False
    # 1.2 碰到面包屑（已尝试走过的可以走的点），或者死胡同，返回失败
    if (maze[startRow][startColumn] == TRIED) or (maze[startRow][startColumn] == DEAD_END):
        return False
    # 1.3 碰到了出口， 返回成功
    if maze.isExit(startRow, startColumn):
        maze.updatePosition(startRow, startColumn, PART_OF_PATH)
        return True
    # 1.4 撒一下面包屑，继续探索
    maze.updatePosition(startRow, startColumn, TRIED)
    # 2.1 向北南西东四个方向依次探索，OR操作有短路效应（即一个为TRUE,则后续的不管是啥，结果都为TRUE）
    found = searchFrom(maze, startRow-1, startColumn) or searchFrom(maze, startRow+1, startColumn) or \
            searchFrom(maze, startRow, startColumn-1) or searchFrom(maze, startRow, startColumn+1)
    # 2.2 如果探索成功则标记为当前点，否则标记为死胡同
    if found:
        maze.updatePosition(startRow, startColumn, PART_OF_PATH)
    else:
        maze.updatePosition(startRow, startColumn, DEAD_END)
    return found

#plt.axis('equal')
#plt.title('Maze')
edgeList = initEdgeList()
print(edgeList)

visited  = initVisitedList()
print(visited)

DFS(0, 0, edgeList, visited)
edgeList.remove((0, 0, 0, 1))
edgeList.remove((WIDTH, HEIGHT-1, WIDTH, HEIGHT))

#for edge in edgeList:
#	drawLine(edge[0], edge[1], edge[2], edge[3])
#plt.show()

