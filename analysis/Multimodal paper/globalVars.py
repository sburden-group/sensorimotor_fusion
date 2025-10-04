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
M = soM(s(omegas))           #M_hat = 1/ ((jw)^2 + (jw)) at stimulated frequencies

M_all = soM(s(2*np.pi*xf_all)) #M_hat = 1/ ((jw)^2 + (jw)) at all frequencies
M_all[0] = 0

#scaling factors for output screen and input slider
scaleOutputScreen = 1/4
scaleInput = 0.04616974606700115

