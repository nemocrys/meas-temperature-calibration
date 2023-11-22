import serial
from modbus_crc import add_crc



class Jupiter:
    def __init__(self, com, bd, stopbits, bytesize, timeout):
        self.com = com
        self.bd = bd
        self.stopbits = stopbits
        self.bytesize = bytesize
        self.timeout = timeout
        
        self.ser = serial.Serial(self.com,
                     bytesize = self.bytesize,
                     baudrate = self.bd,
                     stopbits = self.stopbits,
                     timeout= self.timeout)
        
        print(f"T_Jupiter = {self.readCurrentTemperature()}°C")
        
        
        
        
    # Gibt denn command mit Cycle Redunency Check (CRC) zurück. 
    def addCRC(self, command):
        signedCommand = add_crc(command)
        return signedCommand
    
    #sendet einen Befehl an das Gerät und gibt die Antwort zurück
    def sendAndReadCommand(self, command):
        signedCommand = self.addCRC(command)
        self.ser.write(signedCommand)
        response1 = self.ser.readline()
        response2 = self.ser.readline() # falls ein "/n" in der Antwort vorkommt wird trozdem alles gelesen
        return response1 + response2


    # Vor: temperature in °C übergeben
    # Erg: Jupiter hat jetzt die Zieltemperatur temperature
    def setTemperature(self, temperature):
        temperature = int(round(temperature*10,1)) #Zahl mit Komma zu Zahl ohne Komma, z.B. 32.1 (°C) zu 321 (°C)
        binaryTemperature = int(hex(temperature)[2:],16).to_bytes(2, 'big') # temperature wird zu hexstring umgewandelt; "x0" wird vom hexstring entfernt; hexstring wird als int interpretiert mit base 16; und wird zu binary umgewandelt
        command = b"\x02\x06\x00\x02" + binaryTemperature
        res = self.sendAndReadCommand(command) #comand wird gesendet und aufgefangen um 

    # Erg: gibt die aktuelle Ist-Temperatur zurück
    def readCurrentTemperature(self):
        command = b"\x02\x03\x00\x01\x00\x02\x95\xF8"
        res = self.sendAndReadCommand(command)
        tCurrent = int.from_bytes(res[res.find(b"\x04")+1:-4], "big")/10
        return tCurrent
    
    # Erg: gibt die aktuelle Soll-Temperatur zurück
    def readTargetTemperature(self):
        command = b"\x02\x03\x00\x01\x00\x02\x95\xF8"
        res = self.sendAndReadCommand(command)
        tTarget  = int.from_bytes(res[res.find(b"\x04")+3:-2], "big")/10
        return tTarget

###############################################################
"""
# Example:
# working settings for Jupiter4852
J = Jupiter('/dev/ttyr03', bd = 9600, stopbits = 1, bytesize = 8, timeout= 0.1)

J.setTemperature(34.56)
tCurrent = J.readCurrentTemperature()
tTarget  = J.readTargetTemperature()

print(tCurrent)
print(tTarget)
"""