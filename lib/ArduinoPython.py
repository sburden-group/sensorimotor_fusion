#!/usr/bin/env python

from threading import Thread
import os.path
import serial
import time
from datetime import datetime
import struct
import pandas as pd
import numpy as np
# import collections
from collections import deque
import itertools
from threading import Thread
from queue import Queue, LifoQueue
import copy

#ArduinoPython sensor fusion code
#Need to change:
#(1) where to save EMG calibration data
cal_dir = os.path.join('C:/Users/amber/Documents/Github/sensorfusion/calibration','EMGcalibration.txt')
#(2) COM port
COM_PORT = 'COM4'
#(3) slider min and max value (raw data)
SLIDER_MIN = 0.
SLIDER_MAX = 675.8 #3.3V in Arduino (3.3*1024/5)

numPlots = 3 #number of inputs

class slider:
    def __init__(self, port=COM_PORT, serialBaud = 115200, dataNumBytes = 4):
        self.port = port
        self.baud = serialBaud
        self.dataNumBytes = dataNumBytes
        self.numPlots = numPlots
        self.rawData = bytearray(numPlots * dataNumBytes)
        self.dataType = None
        if dataNumBytes == 2:
            self.dataType = 'h'     # 2 byte integer
        elif dataNumBytes == 4:
            self.dataType = 'f'     # 4 byte float
        self.data = [0.,0.,0.] #raw data, float
        self.sliderData = 0.
        self.input1 = 0; self.input2 = 0
        self.datafused = np.array([]) #fused data
        self.isRun = True
        self.isReceiving = False
        self.thread = None
        self.thread2 = None
        self.q1 = LifoQueue()
        self.q_all = Queue()

        print('Trying to connect to: ' + str(port) + ' at ' + str(serialBaud) + ' BAUD.')
        try:
            self.serialConnection = serial.Serial(port, serialBaud, timeout=4)
            print('Connected to ' + str(port) + ' at ' + str(serialBaud) + ' BAUD.')
        except:
            print("Failed to connect with " + str(port) + ' at ' + str(serialBaud) + ' BAUD.')

    def startArduino(self): #read serial start
        if self.thread == None:
            self.serialConnection.reset_input_buffer()
            self.thread = Thread(target=self.backgroundThread)
            self.thread2 = Thread(target=self.receiveArduinoData)
            self.thread3 = Thread(target=self.EMG_MA)
            self.thread.start()
            self.thread2.start()
            self.thread3.start()
            # Block till we start receiving values
            while self.isReceiving != True:
                time.sleep(0.1)

    def backgroundThread(self):    # retrieve data
        time.sleep(1.0)  # give some buffer time for retrieving data
        self.serialConnection.reset_input_buffer()
        while (self.isRun):
            self.serialConnection.readinto(self.rawData)
            self.isReceiving = True

    def receiveArduinoData(self):
        time.sleep(1.0) # give some buffer time for retrieving data
        now_time = 0.; previous_time = 0.
        while self.thread.isAlive():
            raw = copy.deepcopy(self.rawData[:]) # in bytes
            self.data = [abs(struct.unpack(self.dataType, raw[:4])[0]-512), 
                         abs(struct.unpack(self.dataType, raw[4:8])[0]-512),
                         struct.unpack(self.dataType, raw[8:12])[0]]
            # self.q1.put(self.data)
            # self.q_all.put([datetime.now().strftime('%Y-%m-%d-%H:%M:%S.%f'),self.data[0],self.data[1],self.data[2]])
            
            # put data into queues
            now_time = datetime.now().strftime('%S.%f')
            if now_time != previous_time: #avoid repeating timestamps, control sampling rate
                self.q1.put(self.data)
                self.q_all.put([datetime.now().strftime('%Y-%m-%d-%H:%M:%S.%f'),self.data[0],self.data[1],self.data[2]])
            previous_time = now_time

    # EMG rectify and moving average
    def EMG_MA(self):
        window = 200 # 100 ms windows (python 1000Hz,Arduino 200Hz)
        data1 = []
        data2 = []
        while self.thread2.isAlive():
            # self.input1 = 0.
            # self.input2 = 0. 
            while not self.q1.empty():
                Threedata = self.q1.get()
                data1.append(Threedata[0]) # A0, demean, rectify
                data2.append(Threedata[1]) # A1, demean, rectify
                self.sliderData = Threedata[2] #updateing the slider value (A2)
                #taking moving average
                if len(data1) > 0:
                    if len(data1) < window:
                        self.input1 = np.mean(data1)
                        self.input2 = np.mean(data2)
                    else:
                        self.input1 = np.mean(deque(itertools.islice(data1,
                                        int(len(data1)-window),
                                        int(len(data1)))))
                        self.input2 = np.mean(deque(itertools.islice(data2,
                                        int(len(data1)-window),
                                        int(len(data1)))))
                        data1.pop(0) #delete first item in append to avoid long lists
                        data2.pop(0)
                else:
                    self.input1 = 0.
                    self.input2 = 0.   
    
    def rescale_inp(self,MIN=SLIDER_MIN,MAX=SLIDER_MAX): 
        inp = self.sliderData
        return ((inp - MIN) / (MAX - MIN)) - 0.5 #-0.5~+0.5 of slider

    def rescale_inp_EMG(self,inp1,inp2): 
        thresh = 0.025 # threshold is 2.5% of MVIC
        
        EMG_calibration = np.loadtxt(cal_dir)
        MIN_1 = EMG_calibration[0,0]
        MIN_2 = EMG_calibration[1,0]
        MAX_1 = EMG_calibration[0,1]
        MAX_2 = EMG_calibration[1,1]

        INP1 = (float(inp1) - MIN_1) / (MAX_1 - MIN_1) #0~1
        INP2 = (float(inp2) - MIN_2) / (MAX_2 - MIN_2) #0~1

        if (INP1 < thresh) & (INP2 < thresh):
            return 0
        elif INP1 > 1:
            return 0.5
        elif INP2 > 1:
            return -0.5
        else:
            if INP1 > INP2:
                scaled = INP1/2 #0~+0.5
            elif INP1 < INP2:
                scaled = -INP2/2 #-0.5~0
            else:  
                scaled = 0 
                print('error')
                print(self.input1,self.input2,self.sliderData)
            return scaled*2 #-1~1

    #experimentPython3 grabdata here every 60Hz:
    def grabData(self,EMGweight):
        #(1)moving average 2 EMG data, then scale EMG data
        EMG_scaled = self.rescale_inp_EMG(self.input1,self.input2)

        #(2) scale slider data
        slider_scaled = self.rescale_inp()

        #(3) fuse 2 scaled sensor inputs
        self.datafused = (1-EMGweight)*slider_scaled + EMGweight*EMG_scaled #senor fusion

        # print(self.datafused, EMG_scaled, slider_scaled) #Debug

        return self.datafused, EMG_scaled, slider_scaled

    def close(self):
        self.isRun = False
        self.thread.join()
        self.thread2.join()
        self.thread3.join()
        self.serialConnection.close()
        print('Disconnected...')

def main():
    cmd_initial = input('Press anykey+enter to start calibration process;Press enter to start data collection: ')
    if cmd_initial != "":
        sliderJoystick = slider(port = COM_PORT)   # initializes all required variables
        sliderJoystick.startArduino()              # starts background thread
        cmd = input('Press enter to get prepared for max_1 calibration (bicep)')
        if cmd != "":
            EMG_MAX_1 = float(cmd)
        else:
            calibration_num = 3
            save_calibration = np.zeros((calibration_num,))
            for num in range(calibration_num):
                cmd = input('Press enter to start max_1 calibration (2-sec): ')
                calibration = []
                t_end = time.time() + 2 # in 2 seconds
                while time.time() < t_end:
                    print(sliderJoystick.input1,sliderJoystick.input2)
                    calibration.append(sliderJoystick.input1) #A0, EMG1
                save_calibration[num] = np.percentile(calibration,95)# calculate 95th percentile 
                
            EMG_MAX_1 = np.mean(save_calibration)
            print(EMG_MAX_1)
            # np.savetxt('calibration_max_1.csv',calibration,delimiter=',')

        cmd = input('Press enter to get prepared for max_2 calibration (tricep) ')
        if cmd != '':
            EMG_MAX_2 = float(cmd)
        else:
            calibration_num = 3
            save_calibration = np.zeros((calibration_num,))
            for num in range(calibration_num):
                cmd = input('Press enter to start max_2 calibration (2-sec): ')
                calibration = []
                t_end = time.time() + 2 # in 2 seconds
                while time.time() < t_end:
                    print(sliderJoystick.input1,sliderJoystick.input2)
                    calibration.append(sliderJoystick.input2) #A0, EMG1
                save_calibration[num] = np.percentile(calibration,95) # calculate 95th percentile 

            EMG_MAX_2 = np.mean(save_calibration)
            print(EMG_MAX_2)
            # np.savetxt('calibration_max_2.csv',calibration,delimiter=',')

        cmd = input('Press enter to start relaxing (5-sec): ')
        if cmd != '':
            EMG_MIN_1 = float(cmd)
            EMG_MIN_2 = float(cmd)
        else:
            relax1 = []
            relax2 = []
            t_end = time.time() + 5 # in 5 seconds
            while time.time() < t_end:
                print(sliderJoystick.input1,sliderJoystick.input2)
                relax1.append(sliderJoystick.input1) #A0, EMG1
                relax2.append(sliderJoystick.input2)    
            EMG_MIN_1 = np.mean(relax1)
            EMG_MIN_2 = np.mean(relax2)
            print(EMG_MIN_1,EMG_MIN_2)
            # np.savetxt('calibration_max_2.csv',calibration,delimiter=',')

        EMG_calibration = (np.asarray([[EMG_MIN_1,EMG_MAX_1],[EMG_MIN_2,EMG_MAX_2]]))
        np.savetxt(cal_dir, EMG_calibration)
        sliderJoystick.close()
    
    else:
        sliderJoystick = slider(port = COM_PORT)   # initializes all required variables
        sliderJoystick.startArduino()              # starts background thread
        # AllData = []

        t_end = time.time() + 10 # in 10 seconds
        while time.time() < t_end:
            # print(sliderJoystick.data)
            print(sliderJoystick.input1,sliderJoystick.input2,sliderJoystick.sliderData)
            # ThreeData = sliderJoystick.grabData()
            # print(ThreeData)
            time.sleep(0.1)

        # while not sliderJoystick.q2.empty():
        #     AllData.append(sliderJoystick.q2.get()[0])
        # print(len(AllData))
        sliderJoystick.close()


if __name__ == '__main__':
    main()