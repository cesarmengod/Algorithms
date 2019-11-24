# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 16:21:01 2019

@author: armengod
"""

def MaximumPairwiseProduct(vector):
    result = 0
    for i in range(len(vector)-1):
        for j in range(i+1,len(vector)):
            aux = vector[i] * vector[j]
            if aux > result:
                result = aux
    return result