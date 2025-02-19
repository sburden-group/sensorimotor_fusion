import numpy as np
import math as m
from scipy import signal, fft

# N, primes, IX, base_freq, freqs, omegas, fs, sample_period, s, z, soM, zero, first, second

N = 2400 #length of time points
primes = np.asarray([2, 3, 5, 7, 11, 13, 17, 19])# max =37
IX = primes*2 #stimulated frequencies index = np.round(freqs * N / sample_rate).astype(int)
Even_IX = IX[1::2] #np.array([ 6, 14, 26, 38])
Odd_IX = IX[::2] #np.array([ 4, 10, 22, 34])
base_freq = 0.05
freqs = primes*base_freq # stimulated frequencies
omegas = 2*np.pi*freqs
T = 40 # 40 seconds trial
t = np.linspace(0, T, N) #time vector
fs = 60 #game sampling rate, update rate 60 Hz
dt = 1./fs #sample period
xf_all = np.fft.fftfreq(N, 1./ fs)       #freq (x-axis) both + and - terms, shape (N,)
xf = np.fft.fftfreq(N, 1./ fs)[:N//2]    #freq (x-axis) positive-frequency terms, shape (N//2,)
s = lambda omega: 1j*omega # in continuous time, s = jw

def FFT(data,N):
  return fft.fft(data)/N

def IFFT(data,N):
  return (fft.ifft(data)*N).real

soM = lambda s : 1/(s**2 + s) #2nd order machine
M = soM(s(omegas))           #M_hat = 1/ ((jw)^2 + (jw))

#scaling factors for output screen and input slider
scaleOutputScreen = 1/4
scaleInput = 0.04616974606700115

# plotting parameters
colors = dict(M='#6600CC',
              F='#000000',
              B='#FFFFFF',
              H='#009900',
              r='#FDB119',
              u='#009900',
              u25='#BBF90F',
              u75='#006400',
              d='#FD6E19',
              #y='#0033FF',  #or 6600CC which is darker and I prefer 
              y='#6600CC',  #or 6600CC which is darker and I prefer 
              N='#0000CC',
              D='#CC0000',
              g='#B1B1B1', #grey
              first5='#B1B1B1',
              last5='#999999',
              BLUE = '#1f77b4',
              ORANGE = '#ff7f0e',
              GREEN = '#2ca02c',
              RED = '#d62728',
              PURPLE = '#9467bd',
              GOLD = '#FDB119') #default colors
              # D = dominant = right; N = nondominant = left
