import serial, time

ser = serial.Serial('/dev/ttyUSB0', 9600)

# wait while the arduino resets

time.sleep(2)
while 1 :
    ret = ser.readline()
    print(ret)

