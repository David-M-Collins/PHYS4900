"""
Created on Tue Oct 5 11:53:42 2020

@author: David Collins
"""
import numpy as np
from matplotlib import pyplot as plt
import sys
import index_finder as i_f

file = "oem_2-9-21.npy"

data = np.load(file, allow_pickle=True)

info = data[()].keys()

print(info)

newtemp = data[()].get("newtemp")
newtemperr = data[()].get("newtemperr")
newalt = data[()].get("newalt")
msisTemp = data[()].get("msisTemp")
temptopalt = data[()].get("temptopalt")
dates = data[()].get("newdate")
oldtemp = data[()].get("oldtemp")
oldtemperr = data[()].get("oldtemperr")
oldalt = data[()].get("oldalt")
tempdate = data[()].get("tempdate")
olddate = data[()].get("olddate")

np.set_printoptions(threshold=sys.maxsize)

date = i_f.index_finder(20150307, dates)

print(len(dates) - len(olddate))

Altitude = newalt[date][0]
AltitudeMSIS = newalt[date][1]
MSISe00 = msisTemp[date - 6]
TopAlt = int(temptopalt[date]) + 1
HCnan = oldtemp[date - 6]
HCerrnan = oldtemperr[date - 6]
Alt = oldalt[date - 6]


HC = HCnan[np.logical_not(np.isnan(HCnan))]
HCerr = HCerrnan[np.logical_not(np.isnan(HCerrnan))]

check = int(Altitude[TopAlt])

index = i_f.altMSIS_index_finder(check, AltitudeMSIS)

OEM = newtemp[date].resize(TopAlt, refcheck=False)
OEMerr = newtemperr[date].resize(TopAlt, refcheck=False)
HC.resize(TopAlt, refcheck=False)
HCerr.resize(TopAlt, refcheck=False)
Altitude.resize(TopAlt, refcheck=False)
AltitudeMSIS = np.resize(AltitudeMSIS, index)
MSIS = np.resize(MSISe00, index)


