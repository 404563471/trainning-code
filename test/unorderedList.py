from DataStructure import UnorderedList

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
