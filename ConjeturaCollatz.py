# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 20:46:18 2019

@author: armengod
"""

def ConjeturaDeCollatz(n):
    result = list()
    while n != 1:
        if n % 2 == 0: 
            n /= 2
        else: 
            n = 3 * n + 1
        result.append(int(n))    
    return result