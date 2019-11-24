# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 16:21:01 2019

@author: armengod
"""

import time

def MaximumPairwiseProduct(vector):
    result = 0
    for i in range(len(vector)-1):
        for j in range(i+1,len(vector)):
            aux = vector[i] * vector[j]
            if aux > result:
                result = aux
    return result

def MaximumPairwiseProductFAST(vector):
    vector.sort()
    return vector[len(vector)-1] * vector[len(vector)-2]

vector = [x for x in range(10000)]
a = time.time()
print(MaximumPairwiseProduct(vector))
b = time.time()
b-a

a = time.time()
print(MaximumPairwiseProductFAST(vector))
b = time.time()
b-a