import os
import sys
sys.path.append(os.getcwd())

from DataStructure import UnorderedList, OrderedList

mylist=UnorderedList()

for i in range(5):
    mylist.add(i)

#print(mylist.size())
print(mylist)
position = mylist.search(3)
print("position is: ", position)

print(mylist.remove(-5))
#print(mylist.remove(mylist.search(3)))
#print(mylist.remove(3))
print(mylist)

#print(mylist.remove(mylist.search(3)))
print(mylist)

mylist.append(-1)
print(mylist)

print(mylist.getNode(-2))

mylist.getNode(-2).value = 10
print(mylist)

mylist.insert(0, 101)
mylist.insert(4, 104)

print(mylist)

print("this is orderedlist")

myorder = OrderedList()

for i in range(5, 0, -1):
    print(myorder)
    myorder.add(i)

print(myorder)