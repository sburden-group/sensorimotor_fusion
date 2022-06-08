#!usr/bin/MYenv python3

# this code is updated by Amber 070121

import socket
import sys
import numpy as np
from struct import *
import select
from matplotlib import pyplot as plt
import time
import matplotlib.animation as animation
#from protocols.globalsPython3 import *
from multiprocessing import Process
import threading
from threading import Thread
from queue import Queue, LifoQueue, Empty
from scipy.signal import detrend
import csv
from datetime import datetime
import gc; gc.disable()
from collections import deque
import itertools

import serial
ser = serial.Serial('COM3',9600)
time.sleep(2)

data = []
# HOST = '140.142.113.148'
# PORT_EMG = 50043
# BUFSIZE = 1024
# window = 250 # ms so samples = 2000 samples/1000 ms = 2 samples/ms


# this function is for experimentEMG.py
def run_EMG6(s_EMG,q1,q3,t):

	data = []
	print('running run_EMG')

    while True:
    b = ser.readline()         # read a byte string
    string_n = b.decode()  # decode byte string into Unicode  
    string = string_n.rstrip() # remove \n and \r
    flt = float(string)        # convert string to float
    # print(flt)
    SS_data.append(flt)           # add to the end of data list
    time.sleep(0.02)            # wait (sleep) 0.02 seconds

	# while t.isAlive():
	# 	temp = s_EMG.recv(64)
	# 	datapoint = [(unpack('<f',temp[0:4]))[0],(unpack('<f',temp[4:8]))[0]]
	# 	q1.put(datapoint)

	# 	q3.put([datetime.now().strftime('%Y-%m-%d-%H:%M:%S'),(unpack('<f',temp[0:4]))[0],(unpack('<f',temp[4:8]))[0]])

def EMG_grabData(q,data):
	# window = 100 # process in 100 ms windows
	while not q.empty():
		data.append(q.get())

	# # data = np.asarray(q.get())[-int(window*2):,:]
	# # data = detrend(data,axis=0,type='linear')
	# if len(data) > 0:
	# 	if len(data) < window*2:
	# 		# window = int(len(data[:,0])/2)
	# 		datanew = detrend(data,axis=0,type='linear')
	# 	else:
	# 		# data = [len(data)-int(window*2):,:]
	# 		# DETREND FIRST 50 MS OF DATA BEFORE TAKING AVERAGE
	# 		data1 = detrend(deque(itertools.islice(data,
	# 			int(len(data)-window*2),
	# 			int(len(data)-window))),
	# 			axis=0,type='linear')
	# 		data2 = detrend(deque(itertools.islice(data,
	# 			int(len(data)-(window)),
	# 			int(len(data)))),
	# 			axis=0,type='linear')
	# 		# data1 = detrend(data[-int(window*2):-int(window)],axis=0,type='linear')
	# 		# data2 = detrend(data[-int(window)-1:],axis=0,type='linear')
	# 		datanew = np.concatenate((data1,data2),axis=0)
	# 	input1 = np.mean(abs(datanew[-window*2:,0]))
	# 	input2 = np.mean(abs(datanew[-window*2:,1]))
	# 	# with q.mutex:
	# 	# 	q.queue.clear()
	# 	return input1,input2
	# else:
	# 	return 0,0

# def EMG_rms(q1,q2,t):
# 	input = []
# 	sampling_time = 16.6666666666666666 # sampling time in ms

# 	print('trying to thread')
# 	while  t.isAlive():#not q1.empty():
# 		data = abs(np.asarray(q1.get()))
# 		avg = np.mean(data[-200*2:]) # try processing 200 ms at a time
# 		print(avg)
# 		input.append(avg)
# 		# with q1.mutex:
# 		# 	q1.queue.clear()
# 		with q1.mutex:
# 			q1.queue.clear()
# 		time.sleep(sampling_time/1000)

# 	q2.put(input)
# 	return input
