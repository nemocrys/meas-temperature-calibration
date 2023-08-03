#!/usr/bin/env python3
import adafruit
#import pymodbus
import time
import matplotlib.pyplot as plt
import numpy as np



# Liest das Rezept ein
#Erg: Wertelisten aus dem Rezept
def readRezept(debugPrint=True):
    with open("rezept.txt", "r") as f:
        rezept = f.read().split("\n")
    tTarget = [] # in °C
    tTime = []   # in minuten
    tStationaer = [] # in minuten
    for x in rezept:
        tTarget.append(x.split(",")[0])
        tTime.append(x.split(",")[1])
        tStationaer.append(x.split(",")[2])
    if debugPrint == True:
        print(f"tTarget: {tTarget}")
        print(f"tTime:   {tTime}")
        print(f"tStatio: {tStationaer}")
    return tTarget, tTime, tStationaer

# Erg: Plotet mit den neusten Werten neu und legt ie Grezen neu fest.
def plotData(ax, fig, tSensorList, tInstrList, tSensorLine, tInstrLine):
    x1 = np.linspace(0,len(tSensorList),len(tSensorList))
    x2 = np.linspace(0,len(tInstrList),len(tInstrList))
    tSensorLine.set_xdata(x1)
    tInstrLine.set_xdata(x2)
    ax.set_xlim([0, len(tSensorList)+1])
    
    if tSensorList != None:
        tSensorLine.set_ydata(tSensorList) #plot new line
        tInstrLine.set_ydata(tInstrList) #plot new line
        limList = tSensorList
        #limList.sort()
        limList = limList[1:]
        ax.set_ylim([ float(limList[0])-1, float(limList[-1])+1 ])
    else:
        ax.set_ylim([0, 100])
        
    fig.canvas.draw()
    fig.canvas.flush_events()



### Prepare Sensor
sensor = adafruit.Adafruit(name="Pt100", GPIO="D24",res=100,refres=430,wire=4,Vergleichssensor=True)
tSensor = float(sensor.get_temperatur())
print(f"T_sensor = {round(tSensor,2)}°C")
### Prepare Instrument
#tInstr = 24
#print(f"T_calibration= {round(tInstr,2)}°C")


### Variables
tolerance = 1 #°C
### Listen
tSensorList = [0] # Stores all Temperatures from sensor internaly
tInstrList = [0] # Stores all Temperatures from Calibration instrument internaly
tTargetList, tTimeList, tStationaerList = readRezept() # tTargetList ist die Liste der Zieltempraturen,# tTimeList ist die Liste der "Verweilzeiten"



### Pepare Temperatures.txt
with open("temperatures.csv", "w") as f: 
    f.write("tSensor,tInstr,tTarget\n")



###Plot Prep.
x1 = 0
x2 = 0
fig, ax = plt.subplots(figsize=(10, 8))
plt.title("Temperatur über Zeit", fontsize=20)
plt.xlabel("Zeit [s]",fontsize=18)
plt.ylabel("Temperatur [°C]",fontsize=18)
plt.grid()
plt.ion()
plt.show()
tSensorLine, = plt.plot(x1, tSensorList)
tInstrLine, = plt.plot(x2, tInstrList)



### Start Loop
for i in range(len(tTargetList)):
    tTarget     = tTargetList[i]
    tTime       = tTimeList[i]
    tStationaer = tStationaerList[i]
    
    while True:
        ### Generate Data
        tSensor = round(sensor.get_temperatur(),4)
        print(tSensor)
        tInstr = 24 # Temporär, Kalibrator funktioniert noch nicht :(


        ###Save data internaly
        tSensorList.append(tSensor)
        tInstrList.append(tInstr)


        ###Save data externaly
        with open("temperatures.csv", "a") as f:
            f.write(f"{tSensor},{tInstr},{tTarget}\n")
        
        ###Check if tSensor is in Target Area and stationary
        if tSensor <= tTarget + tolerance and tSensor >= tTarget - tolerance and isStationaer == True:
            print("stationär!")
        
        
        plotData(ax, fig, tSensorList, tInstrList, tSensorLine, tInstrLine)
        
        
        time.sleep(1) # wait 1s until next read
    
