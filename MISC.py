from csv import DictReader
from netCDF4 import Dataset
import numpy as np
from matplotlib import pyplot as plt
import index_finder as i_f
import os

alldates = []
with open('CSV_Dates.csv', 'r') as read_obj:
    csv_reader = DictReader(read_obj)
    for row in  csv_reader:
        alldates.append(int(row['Dates']))

# constant LIDAR data file which has all the available days in it
file = "oem_2-9-21.npy"

not_made = 0
not_made_SABER = 0
not_made_LIDAR = 0

while(alldates != []):  
    # the date examined in YYYYMMDD
    graph_date = int(alldates.pop(0))
        
    # open day to examine for SABER data
    path = "SABER_data/SABER_" + str(graph_date) + ".nc"
    saber = Dataset(path)
    
    # pull and set appropriate data in SABER file, the 1 pulls the night data only
    DN = saber['tpDN'][:]
    nightval = 0
    for zil in range(len(DN)):
        if DN[zil] == 1:
            nightval = nightval + 1
    if nightval == 0:
        print(str(graph_date) + " not created due to lack of SABER data")
        not_made = not_made + 1
        not_made_SABER = not_made_SABER + 1
        continue
    alt = saber['tpaltitude'][:nightval]
    lat = saber['tplatitude'][:nightval]
    lon = saber['tplongitude'][:nightval]
    temp = saber['ktemp'][:nightval]
    
    # create SABERerr list
    SABERerr = [[] for i in range(nightval)] 
    for l in range(nightval):
        for x in range(len(alt[l])):
            if alt[l][x] > 69 and alt[l][x] < 90:
                SABERerr[l].append(3)
            if alt[l][x] > 90 and alt[l][x] < 100:
                SABERerr[l].append(5.6)
            if alt[l][x] > 100 and alt[l][x] < 110:
                SABERerr[l].append(10.5)
            if alt[l][x] > 110:
                SABERerr[l].append(29.4)  
    
    # correct list size difference for empty alt values
    for zen in range(nightval):
        diff = len(alt[zen]) - len(SABERerr[zen])
        if diff != 0:
            for correct in range(diff):
                SABERerr[zen].append(0)
    
    # load up and use data file
    data = np.load(file, allow_pickle=True)
    info = data[()].keys()
    newtemp = data[()].get("newtemp")
    newtemperr = data[()].get("newtemperr")
    newalt = data[()].get("newalt")
    dates = data[()].get("newdate")
    temptopalt = data[()].get("temptopalt")
    msisTemp = data[()].get("msisTemp")
    oldtemp = data[()].get("oldtemp")
    oldtemperr = data[()].get("oldtemperr")
    oldalt = data[()].get("oldalt")
    
    # get proper index for examined date
    date = i_f.index_finder(graph_date, dates)
    
    # set LIDAR data into proper arrays
    OEM = newtemp[date]
    OEMerr = newtemperr[date]
    Altitude = newalt[date][0]
    TopAlt = int(temptopalt[date]) + 1
    AltitudeMSIS = newalt[date][1]
    MSISe00 = msisTemp[date - 6] # the -6 is to offset the difference in date array lengths, but still get the right date
    OEM.resize(TopAlt, refcheck=False)
    OEMerr.resize(TopAlt, refcheck=False)
    Altitude.resize(TopAlt, refcheck=False)
    AltitudeMSIS = np.resize(AltitudeMSIS, MSISe00.size)
    HCnan = oldtemp[date - 6]
    HCerrnan = oldtemperr[date - 6]
    AltHC = oldalt[date - 6]
    HC = HCnan[np.logical_not(np.isnan(HCnan))]
    HCerr = HCerrnan[np.logical_not(np.isnan(HCerrnan))]

    
    # set Altitudes to km values instead of m values
    Alt = i_f.m_to_km(Altitude)
    AltitudeM = i_f.m_to_km(AltitudeMSIS)

    # create the list of SABER temp data to compare LIDAR temp data to
    topLimit = None
    bottomLimit = None
    for a in range(len(Altitude)):
        if Altitude[a] > 110:
            topLimit = a
            break
        else:
            topLimit = a + 1
    for b in range(TopAlt):
        if Altitude[b] > 70:
            bottomLimit = b
            break
    trim = [Altitude[c] for c in range(bottomLimit, topLimit)]
    comparetemp = [[] for i in range(nightval)]
    comparealt = [[] for i in range(nightval)]
    check = len(trim)  
    for d in range(nightval):
        index = 1
        for e in range(len(alt[d])):
            if (index - 1) != check and (e - 1) < len(alt[d]):
                if alt[d][e] > trim[-index] and alt[d][e + 1] < trim[-index]:
                    comparetemp[d].append(i_f.average2(temp[d][e], temp[d][e + 1]))
                    comparealt[d].append(i_f.average2(alt[d][e], alt[d][e + 1]))
                    index = index + 1
            else:
                comparetemp[d].reverse()
                comparealt[d].reverse()
                break

    # find accuracy values for regions of 80- km, 80 to 95 km, 95+ km
    bottom = [[] for i in range(nightval)]
    middle = [[] for i in range(nightval)]
    top = [[] for i in range(nightval)]
    botval = []
    midval = []
    topval = []
    # currently comparing total distance between LIDAR data with error and SABER
    for f in range(nightval):
        for g in range(len(comparealt[f])):
            if comparealt[f][g] < 80: # bottom region
                if OEM[g] > comparetemp[f][g]:
                    bottom[f].append(OEM[g] - OEMerr[g] - comparetemp[f][g])
                else:
                    bottom[f].append(OEM[g] + OEMerr[g] - comparetemp[f][g])
            elif comparealt[f][g] > 95: # top region
                if OEM[g] > comparetemp[f][g]:
                    top[f].append(OEM[g] - OEMerr[g] - comparetemp[f][g])
                elif OEM[g] < comparetemp[f][g]:
                    top[f].append(OEM[g] + OEMerr[g] - comparetemp[f][g])
            else: # middle region
                if OEM[g] > comparetemp[f][g]:
                    middle[f].append(OEM[g] - OEMerr[g] - comparetemp[f][g])
                elif OEM[g] < comparetemp[f][g]:
                    middle[f].append(OEM[g] + OEMerr[g] - comparetemp[f][g])
        botval.append(round(sum(bottom[f]) / len(bottom[f]), 2))
        if len(middle[f]) > 0:
            midval.append(round(sum(middle[f]) / len(middle[f]), 2))
        if len(top[f]) > 0:
            topval.append(round(sum(top[f]) / len(top[f]), 2))
        
    if len(midval) == 0:
        print(str(graph_date) + " not created due to lack of LIDAR data")
        not_made = not_made + 1
        not_made_LIDAR = not_made_LIDAR + 1
        continue
    # destination for graph images
    outpath = "Graphs3/"

    # ensure destination exists
    if not os.path.exists(outpath):
        os.makedirs(outpath)

    # plot the final graph
    for i in range(nightval):
        if abs(midval[i]) == abs(min(midval)):
            x = max(max(temp[i]), max(OEM))
            averageLat = np.average(lat)
            averageLon = np.average(lon)
            title = (str(graph_date) + " at Lat " + str(round(averageLat, 2)) + 
                     " and Lon " + str(round(averageLon, 2)))
            plt.plot(temp[i], alt[i], color='g', label='SABER')
            plt.fill_betweenx(y=alt[i], x1=(temp[i]-SABERerr[i]), 
                    x2=(temp[i]+SABERerr[i]), color='#90ee90')
            plt.plot(OEM, Alt, color='b', label='OEM')
            plt.fill_betweenx(y=Alt, x1=(OEM-OEMerr), x2=(OEM+OEMerr),
                    color='#add8e6')
            plt.plot(MSISe00, AltitudeM, color='#ffa500', label='MSIS2')
            plt.plot(HC, AltHC, color='#ff0000', label='HC')
            plt.fill_betweenx(y=AltHC, x1=(HC-HCerr), x2=(HC+HCerr),
                    color='#ffb2b2')
            plt.axhline(y=80, color='r', linestyle='-')     
            plt.axhline(y=95, color='r', linestyle='-')       
            plt.xlabel('Temperature (K)')
            plt.ylabel('Altitude (km)')
            plt.suptitle(title)
            plt.legend(loc='upper left')
            plt.xlim([130, 320])
            plt.ylim([70, 110])
            botdist = "average temp distance " + str(botval[i]) + " K"
            middist = "average temp distance " + str(midval[i]) + " K"
            #plt.title(middist)
            #plt.text(x, 75, str(botdist), horizontalalignment='right')
            #plt.text(x, 85, str(middist), horizontalalignment='right')
            #if topval:
                #topdist = "average temp distance " + str(topval[i]) + " K"
                #plt.text(x, 105, str(topdist), horizontalalignment='right')
            name = outpath + title + ".png"
            plt.savefig(name.format(i))
            plt.close()
    print(str(graph_date) + " created successfully")
    saber.close()

print()
print("---REPORT---")
print("Total Graphs not created: " + str(not_made))
print("Total not made due to lack of SABER data: " + str(not_made_SABER))
print("Total not made due to lack of LIDAR data: " + str(not_made_LIDAR))
