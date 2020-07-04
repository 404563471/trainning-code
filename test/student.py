from DesignPattern import *

Bob=normalStudent("Bob", 59)
BobGrade=Bob.get_grade()
print(BobGrade)

Wang=someStudent("Wang", 57)
WangGrade=Wang.get_grade()
print(WangGrade)

Bill=niceTeacher("A")
print(Bill.getComment())

Wang=mathGrade("Wang", 57)
Wang.get_grade()
WangComment=Wang.getComment()
print(WangComment)