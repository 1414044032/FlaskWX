# -*- coding: utf-8 -*-
import collections

list1 = [1,2,3,4,5,6,7,7,8,8,9]
result = collections.Counter(list1)
keys = [i for i in result.keys()]
values = [i for i in result.values()]
print(result)
print(keys)
print(values)