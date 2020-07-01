from DataStructure import Stack, Queue, Deque

myStack=Stack()
for i in range(10):
    myStack.push(i)
print(myStack.size())
print(myStack)

for i in range(3):
    print(myStack.pop())

print(myStack)
print(myStack.top())


myQueue=Queue()
for i in range(10):
    myQueue.push(i)

print(myQueue)
for i in range(3):
    print(myQueue.pop())

print(myQueue)
print(myQueue.top())


myDeque=Deque()
for i in range(10):
    myDeque.addRear(i)

print(myDeque)
for i in range(4):
    print(myDeque.removeFront())
print(myDeque)

myDeque=Deque()
for i in range(10):
    myDeque.addFront(i)

print(myDeque)
for i in range(4):
    print(myDeque.removeFront())
print(myDeque)
