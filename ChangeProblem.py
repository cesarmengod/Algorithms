# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 14:36:48 2019

@author: armengod
"""

def ChangeProblem(money, d):
    change = list()
    for i in range(len(d)):
        aux = money // d[i]
        money -= aux * d[i] 
        change.append(aux)
    return change
