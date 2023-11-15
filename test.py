from jupiter4852 import Jupiter

J = Jupiter('/dev/ttyr03', bd = 9600, stopbits = 1, bytesize = 8, timeout= 0.1)

text = J.setTemperature(30)
print(text)

print(J.readTargetTemperature())

#J.setTemperature(30.00)
