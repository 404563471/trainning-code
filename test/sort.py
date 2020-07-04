from algorithms.sort import *

sorted_arr=list(range(10))
#sorted_arr=list(range(10000))
un_sorted=kd(sorted_arr)
print(un_sorted)

un_sorted=tuple(un_sorted)
print(bubble_sort(list(un_sorted)))

print(un_sorted)
print(selection_sort(list(un_sorted)))


