import time
import serial

ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.050)
count = 0

while 1:
    cmd = input("Enter command: ")
    print("Sent: " + cmd)
    ser.write(cmd.encode())
    