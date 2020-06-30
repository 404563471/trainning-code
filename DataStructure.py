class Node():
    def __init__(self, value):
        self.value = value
        self.next = None

    def __repr__(self):
        return str(self.value)

    def __str__(self):
        return str(self.value)


class UnorderedList():
    '''
    初始化的head为None, 不计入size中;
    位置从head开始0, 1, 2....进行计算
    '''

    def __init__(self):
        self.head=None

    def isEmpty(self):
        return self.head==None

    def add(self, node):
        if not isinstance(node, Node): node=Node(node)
        self.head, node.next = node, self.head

    def append(self, node):
        if not isinstance(node, Node): node=Node(node)

        if self.head == None :
            self.head = node
        else:
            current = self.head
            while current.next != None :
                current = current.next
            current.next = node


    def size(self):
        current=self.head
        count=0
        while current != None:
            count += 1
            current = current.next
        return count

    def search(self, item):
        current=self.head
        found=False
        position=-1
        while current != None and found == False :
            found = current.value == item
            current=current.next
            position += 1

        if found : return position
        else:  return None

    def getNode(self, position):

        position = self.positionRange(position)

        current = self.head
        index = 0
        while index < position :
            current = current.next
            index += 1
        return current

    def remove(self, position):

        position = self.positionRange(position)

        if position == 0 :
            removeNode = self.head
            self.head = removeNode.next
        else:
            index = 1
            previous = self.head
            current = previous.next
            while index < position :
                index += 1
                previous = current
                current = previous.next

            removeNode = current
            previous.next = removeNode.next

        return removeNode.value

    def clear(self):
        self.head = None
        print("clear all data")

    def transList(self):
        current=self.head
        valueList=[]
        while current != None :
            valueList.append(current.value)
            current = current.next
        return valueList

    def __str__(self):
        valueList = self.transList()
        return str(valueList)

    def __repr__(self):
        valueList = self.transList()
        return str(valueList)

    def positionRange(self, position):
        length = self.size()
        if position > length or position + length < 0:
            raise IndexError()

        if position < 0 :
            position += length

        return position
