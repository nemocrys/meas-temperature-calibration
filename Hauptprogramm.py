#!/usr/bin/env python3
from jupiter4852 import Jupiter
from daq6510 import Daq6510


import matplotlib.pyplot as plt
import numpy as np

import os
from datetime import datetime
import time
import yaml
# Erstellt den Ergebnisordner und erstellt die Datein, sowie die erste Zeile der .cvs Datein
# Erg: Gibt den path zum Ergebnisordner zurück
def createFiles():
    date = datetime.now().strftime('%Y-%m-%d')
    parent_dir = "./data/"
    
    # Automatische Erzeugung von eindeutigen Filenamen, ohne das eine alte Datei überschrieben wird:
    directoryIndex = '#'+str(1).zfill(2)
    directory = f"{date}_{directoryIndex}" # Andere Dateiendungen (z.B. dat) auch möglich
    j = 1
    while os.path.exists(parent_dir + '/' + directory): # Schaut ob es den Namen schon in dem Verzeichnis gibt ...
        j = j + 1 # ... wenn ja wird der FleOutIndex (j) solange erhöht bis es eine neue Datei erstellen kann
        directoryIndex = '#'+str(j).zfill(2)
        directory = f"{date}_{directoryIndex}"
    
    path = os.path.join(parent_dir, directory)
    os.mkdir(path)
    
    # Pepare Files
    with open(os.path.join(path, "data.csv"), "w", encoding="utf-8") as f: 
        line1 = "tTarget,tCal"
        line2 = ""
        for sensor in sensors:
            line2 = line2 + f",{sensor['ID']}"
        f.write(line1+line2+"\n")
        
    with open(os.path.join(path, "measurementData.csv"), "w", encoding="utf-8") as f: 
        line1 = "tTarget,tCal_avg,tCal_std"
        line2 = ""
        for sensor in sensors:
            line2 = line2 + f",{sensor['ID']}_avg,{sensor['ID']}_std,{sensor['ID']}_offset"
        f.write(line1+line2+"\n")
        
    return path


# Liest die Datei "settings.txt" ein.
# Erg: Wertelisten aus dem Rezept; für detalierte Beschreibung siehe debugPrint Fuktion
def readRezept(debugPrint=True):
    with open("rezept.txt", "r", encoding="utf-8") as f:
        rezept = f.read().split("\n")
    
    tTarget = [] # in °C
    tToleranz = [] # in °C
    tTime = []   # in min
    tStationaer = [] # in min
    tStationaerTolerace = []
    
    for temp in rezept:
        line = temp.replace(" ", "")
        if line.startswith("s:"):
            controlSensorList = line.split(",")
            controlSensorList[0] = controlSensorList[0][2:]
            
        elif line.startswith("r:"):
            tTarget.append(line.split(",")[0])
            tToleranz.append(line.split(",")[1])
            tTime.append(line.split(",")[2])
            tStationaer.append(line.split(",")[3])
            tStationaerTolerace.append(line.split(",")[4])

    # remove the "r:"
    for i in range(len(tTarget)):
        tTarget[i] = tTarget[i].replace("r:", "")
        
    if debugPrint == True:
        print(f"tTarget:        {tTarget}") # Liste der Zieltemeraturen
        print(f"tToleranz:      {tToleranz}") # Liste des Tolranzbereich für die Zieltemeraturen
        print(f"tTime:          {tTime}") # Liste der Zeiten die für die Messung verwedet werden soll
        print(f"tStatio:        {tStationaer}") # Liste der Zeiten, die die Temperatur stationär sein soll
        print(f"tStatioToleranz:{tStationaerTolerace}") # Liste der Toleranz der Stationärtemperatur
        print("-----------------------\n")
        
    return tTarget, tToleranz, tTime, tStationaer, tStationaerTolerace, controlSensorList


# Erg: Plotet mit den neusten Werten neu
def plotData(ax, List, Line):
    x = np.linspace(0,len(List)*timeRes,len(List))
    Line.set_xdata(x)
    ax.set_xlim([1, len(List)*timeRes+1])
    
    if List != None:
        Line.set_ydata(List) # plot new line


# Prüft ob die Temperatur Stationär ist, gibt True zurück wenn ja.
# Vor: tList:               Liste der Temperaturen die geprüft werden sollen
#      tStationär:          Wie lang die Stationärität daueren soll in Minuten
#      tStationaerTolerace: Welche Temperaturabweichung "geduldet" wird in °C
def stationaerPruefung(tList, tStationaer, tStationaerTolerace):
    isStationaer = False
    if len(tList) > tStationaer: # Nur prüfen wenn über StationarTime Einträge vohanden sind
        tempList = tList[int(-tStationaer * 30):] # Liste der letzten Temperaturen erstellen...
        tempList.sort() # ...und sortieren
        #print(f"Größte   Temp:{round(tempList[-1],2)}\nKleinste Temp:{round(tempList[0],2)}")
        if tempList[-1] - tempList[0] <= tStationaerTolerace: # Wenn die größte die Temperaur und die Kleinste Temp. kleiner sind als der vorggebene Bereich
            isStationaer = True
            #print("Stationaer")
        else:
            isStationaer = False
            #print("Nicht Stationaer")
    return isStationaer
            
            

# Schließt das Programm ordnugsgemäß
def on_close(event):
    print("Program wurde ordungsgemäß geschlossen!")
    exit()
    
    
###########################################################################################
                                    ### ### ### BEGIN PREP ### ### ###
timeRes = 3 # Alle drei Sekunden eine Berechnung

# Load config data
with open("config.yml", "r") as f:
    config = yaml.safe_load(f)


### Prepare Sensors
daq = Daq6510(config["DAQ-6510"])
sensors = []
tSensor = []

for channel in config["DAQ-6510"]["channels"]:
    print(daq.read())
    tSensor.append(round(float(daq.read().split(",")[1]),2))
    print(daq.config["channels"][channel]["sensor-id"])
print(f"T_sensor = {tSensor}")

### Prepare Instrument
J = Jupiter('/dev/ttyr03', bd = 9600, stopbits = 1, bytesize = 8, timeout= 0.1)

path = createFiles()
### Variables
tTargetList, tToleranceList, tTimeList, tStationaerList, tStationaerToleraceList, controlSensorList = readRezept() # tTargetList ist die Liste der Zieltempraturen,# tTimeList ist die Liste der "Verweilzeiten"


# Plot Prep.
x = 0

plt.ion()
fig = plt.figure(figsize=(10,10)) # Fenster Größe des Diagrammes festlegen
fig.suptitle("Programm wird beendet, wenn Plot geschlossen wird!",fontsize=14, c="red") # Erzeugt eine Gesamt Überschrifft des Graphen

# Graph: Temperaur
tCalList = [0] # Stores all Temperatures from Calibration instrument internaly
ax1 = plt.subplot(111)
ax1.set_ylim([25, 115])

tCalLine, = ax1.plot(x, tCalList, label='Jupiter 4852',c="black") # plottet T_kalibriergerät


sensors = []
for channel in config["DAQ-6510"]["channels"]:
    
    channelId = config["DAQ-6510"]["channels"][channel]["sensor-id"]
    
    tSensorList = [0]
    tSensorListTemp = []
    tSensorLine, = ax1.plot(x, tSensorList, label=channelId)
    
    tempdict = {"ID" :             channelId,
                "tSensorList":     tSensorList,
                "tSensorListTemp": tSensorListTemp,
                "tSensorLine":     tSensorLine,
                }
                
    sensors.append(tempdict)
    
    
plt.title("Temperatur über Zeit", fontsize=12)
plt.xlabel("Zeit [s]",fontsize=10)
plt.ylabel("Temperatur [°C]",fontsize=10)
plt.grid()
plt.legend()

plt.tight_layout()
plt.show()
fig.canvas.mpl_connect('close_event', on_close) # Programm wird beendet, wenn Plot geschlossen wird!



###########################################################################################
                                    ### ### ### BEGIN LOOP ### ### ###



for i in range(len(tTargetList)):
    
    # Erstellt die aktuellen Variablen zur Temperatur aus den settings.txt Listen
    tTarget     = float(tTargetList[i])
    tTolerance  = float(tToleranceList[i])
    tTime       = float(tTimeList[i])
    tStationaer = float(tStationaerList[i])
    tStationaerTolerace = float(tStationaerToleraceList[i])
    
    #Temperaur auf tTarget setzten
    J.setTemperature(tTarget)
    print(f"nächste Temperatur!\n  tTarget = {tTarget}°C")
    
    # Temporäre Listen/Variablen zurücksetzten
    dataPoints = 0
    for sensor in sensors:
        sensor["tSensorListTemp"] = []
    tCalListTemp = []
    
    isStationaer1   = False
    isStationaer1   = False
    isInTargetArea1 = False
    isInTargetArea2 = False
    
    # Begin Main Loop
    while True:
        calcStart = time.time()
        
        for sensor in sensors:
            sensor["tSensorList"].append(round(float(daq.read().split(",")[1]),2))
            
        tCal = J.readCurrentTemperature()
        tCalList.append(tCal)

        ### Save data externaly
        with open("data.csv", "a") as f:
            line1 = f"{tTarget},tCal"
            line2 = ""
            for sensor in sensors:
                line2 = line2 + f",{sensor['tSensorList'][-1]}"
                f.write(line1 + line2 + "\n")
        
        isStationaer1 = stationaerPruefung(tCalList, tStationaer, tStationaerTolerace)
        if tCal <= (tTarget + tTolerance) and tCal >= (tTarget - tTolerance): isInTargetArea1 = True
        
        for sensorID in controlSensorList:
            for sensor in sensors:
                if sensorID == sensor["ID"]:
                    isStationaer2 = stationaerPruefung(sensor["tSensorList"], tStationaer, tStationaerTolerace)
                    if isStationaer2 == False:
                        break
                    #print(sensor["tSensorList"][-1])
                    if sensor["tSensorList"][-1] <= (tTarget + tTolerance) and sensor["tSensorList"][-1] >= (tTarget - tTolerance):
                        isInTargetArea2 = True

        ### Check if Temperatures are in Target Area and stationary
        if isStationaer1 == True and isStationaer2 == True and isInTargetArea1 == True and isInTargetArea2 == True:
            if dataPoints == 0: print("Messung beginnt!")
            for sensor in sensors:
                sensor["tSensorListTemp"].append(sensor["tSensorList"][-1]) # Speichert alle Temperaturen der aktuellen Messung
            tCalListTemp.append(tCal) # Speichert alle Temperaturen der aktuellen Messung
            dataPoints = dataPoints + 1
            
            # Skip to next Step in Sequence
            if dataPoints >= tTime * (60/timeRes):
                # Speichert gerundete Werte der aktuellen Messung in measurement_data.csv datei
                # Achtung: passiert erst am Schluss der akteullen Messung!
                with open(os.path.join(path,"measurementData.csv"), "a", encoding="utf-8") as f:
                    line1 = f"{tTarget},{round(np.mean(tCalListTemp),2)},{round(np.std(tCalListTemp),2)}"
                    line2 = ""
                    for sensor in sensors:
                        avg = round(np.mean(sensor['tSensorListTemp']),2)
                        std = round(np.std(sensor['tSensorListTemp']),2)
                        offset = round(np.mean(tCalListTemp),2) - avg
                        line2 = line2 + f",{avg},{std},{offset}"
                    f.write(line1 + line2 + "\n")
                break # Beendet die aktuelle Messung und springt zur nächsten
        
        # Zeichnet die Linien
        plotData(ax1, tCalList, tCalLine)
        for sensor in sensors:
            plotData(ax1, sensor["tSensorList"], sensor["tSensorLine"])
        
        
        # aktualiesiert den Graphen
        fig.canvas.draw()
        fig.canvas.flush_events()
        
        calcEnd = time.time() # speichert Zeit am Ende der Berechnung
            
        # adjust for calculation time so every step is exactly 1s appart
        calcTime = calcEnd - calcStart
        if calcTime < timeRes:
            time.sleep(timeRes - calcTime)
        else:
            print(f"Achtung: Berechnungszeit ist größer als der Messabstand!\n  calcTime={round(calcTime,2)}s")
    plt.savefig(os.path.join(path,"plot.png")) # save plot after every Temerature
