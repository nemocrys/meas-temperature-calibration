import serial



def sprint():
    text = ser.readline()
    print(text)



ser = serial.Serial('/dev/ttyr03')  # open serial port
ser.baudrate = 9600
ser.bytesize = 8
ser.stopbits = 1
ser.timeout=0.05
print(ser, end="\n\n")


#Diagnostic code
res = ser.write(b'\02\08\00\00\12\34\ED\4F')
print(res)
#sprint()
#ser.write(b'\02\07\41\12')
#sprint()
#sprint()
#at device address 2, read 2 words from parameter address 1
#(Process Variable and Target Setpoint)
res = ser.write(b"\02\03\00\01\00\02\95\F8")
print(res)
#temp = ser.readline()
#print(temp)
#temp = temp[5:]
#print(temp)
#for x in temp:
#    print(x)

ser.close()             # close port