# -*- coding: utf-8 -*-
"""
Created on Tue Oct 20 16:42:14 2020

@author: David Collins
"""

def index_finder(date, array = []):
    i = 0
    for x in range(0, len(array)):
        if array[i] == date:
            break
        else:
            i = i + 1
    return i
    
def index_printer(array = []):
    for i in range(0, len(array)):
        item = array[i]
        print("index " + str(i) + ": " + str(item))
        
def altMSIS_index_finder(check, array = []):
    indexMSIS = 0
    for i in range(0, len(array)):
        if int(array[i]) >= check:
            break
        else:
            indexMSIS = indexMSIS + 1
    return indexMSIS

# this is made mute for numpy.ndarray objects
def array_trim(index, array = []):
    while len(array) > index:
        array.remove(array[-1])
    return array

def m_to_km(array = []):
    for i in range(0, len(array)):
        array[i] = array[i] * 0.001
    return array

def average2(num1, num2):
    return ((num1 + num2) / 2.0)


