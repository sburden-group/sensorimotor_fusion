# serial read using the Python REPL

import serial
import time
import numpy as np
ser = serial.Serial('COM3',9600)
time.sleep(2)
# Read and record the data
SS_data =[]                       # empty list to store the SpikerShields EMG data
# for i in range(100000):
while True:
    b = ser.readline()         # read a byte string
    string_n = b.decode()  # decode byte string into Unicode  
    string = string_n.rstrip() # remove \n and \r
    flt = float(string)        # convert string to float
    print(flt)
    SS_data.append(flt)           # add to the end of data list
    time.sleep(0.02)            # wait (sleep) 0.02 seconds

ser.close()

# show the data

# for line in data:
#     print(line)

# import matplotlib.pyplot as plt
# # # if using a Jupyter notebook include
# # %matplotlib inline

# plt.plot(data)
# plt.xlabel('Time (seconds)')
# plt.ylabel('Potentiometer Reading')
# plt.title('Potentiometer Reading vs. Time')
# plt.show()

# size = np.size(data)
# print(size)