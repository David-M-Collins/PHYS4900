# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 14:26:18 2020

@author: David Collins
"""
from netCDF4 import Dataset
import numpy as np
from matplotlib import pyplot as plt

path = "SABER_data/SABER_20140719.nc"

saber = Dataset(path)

print(saber)
print()

DN = saber['tpDN'][:]
nightval = 0

for zil in range(len(DN)):
    if DN[zil] == 1:
        nightval = nightval + 1

alt = saber['tpaltitude'][:nightval]
lat = saber['tplatitude'][:nightval]
lon = saber['tplongitude'][:nightval]
temp = saber['ktemp'][:nightval]
SZ = saber['tpSolarZen'][:nightval]

print(temp[-1])
    