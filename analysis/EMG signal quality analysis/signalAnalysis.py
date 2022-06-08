# Created 20210809 by Momona Yamagami
# Methods from C Sinderby, L Indstrom, AE Grassino "Automatic assessment of electromyogram quality", 1995. https://doi.org/10.1152/jappl.1995.79.5.1803

import numpy as np
import pandas as pd
from scipy import signal, fft

def get_SMR(f,Pxx_bic,Pxx_tri):
    
    # get freqs below 600 Hz
    f_600_indx = [ n for n,i in enumerate(f) if i<600 ] # get the indices of freqs below 600 Hz
    f_600 = f[f_600_indx]
    Pxx_bic_600 = Pxx_bic[f_600_indx]
    Pxx_tri_600 = Pxx_tri[f_600_indx]
    
    # compute mean PSD and find highest PSD above 35 Hz
    # average PSD over N points using N/2 points before and after
    N = 13
    b = np.squeeze(np.ones((N,1))/N)
    a = 1
    mean_psd_bic = signal.lfilter(b,a,np.hstack([Pxx_bic_600,(np.squeeze(np.zeros((int(np.floor(N/2)),1))))]))
    mean_psd_bic = mean_psd_bic[int(np.floor(N/2)):]

    mean_psd_tri = signal.lfilter(b,a,np.hstack([Pxx_tri_600,(np.squeeze(np.zeros((int(np.floor(N/2)),1))))]))
    mean_psd_tri = mean_psd_tri[int(np.floor(N/2)):]
    
    # find index that is above 35 Hz for bic
    f_indx_above_35 = [x[0] for x in enumerate(f_600) if x[1] > 35]
    highest_mean_psd = max(mean_psd_bic[f_indx_above_35])
    f_highest_mean_psd = f_600[int(np.argmax(mean_psd_bic[f_indx_above_35])+(len(f_600)-len(f_indx_above_35)))]
    f_highest_mean_psd_indx = int(np.argmax(mean_psd_bic[f_indx_above_35])+(len(f_600)-len(f_indx_above_35))) 

    # find index that is above 35 Hz for tri
    highest_mean_psd_tri = max(mean_psd_tri[f_indx_above_35])
    f_highest_mean_psd_tri = f_600[int(np.argmax(mean_psd_tri[f_indx_above_35])+(len(f_600)-len(f_indx_above_35)))]
    f_highest_mean_psd_indx_tri = int(np.argmax(mean_psd_tri[f_indx_above_35])+(len(f_600)-len(f_indx_above_35))) 
    
    # find all data that is below the slope between highest point and (0,0)) bic
    f_indx_below_20 = [x[0] for x in enumerate(f_600) if x[1] < 20]
    slope = highest_mean_psd/f_highest_mean_psd
    indx_exceed_line = [x[0] for x in enumerate(Pxx_bic_600[f_indx_below_20]) if x[1] > slope*f_600[x[0]]]

    # find all data that is below the slope between highest point and (0,0)) tri
    slope_tri = highest_mean_psd_tri/f_highest_mean_psd_tri
    indx_exceed_line_tri = [x[0] for x in enumerate(Pxx_tri_600[f_indx_below_20]) if x[1] > slope_tri*f_600[x[0]]]
    
    # compute power above line for BICEPS
    power_above_line = np.sum(Pxx_bic_600[indx_exceed_line])
    total_power = np.sum(Pxx_bic_600)
    SM_bic = total_power/power_above_line
    
    # compute power above line for TRICEPS
    power_above_line = np.sum(Pxx_tri_600[indx_exceed_line_tri])
    total_power = np.sum(Pxx_tri_600)
    SM_tri = total_power/power_above_line
    SMR = [10*np.log10(SM_bic),10*np.log10(SM_tri)]
    return SMR

def get_SNR(f,Pxx_bic,Pxx_tri):
    
    # obtain upper 20% of frequency data
    f_ind_upper = range(int(len(f)*4/5),len(f))
    
    # COMPUTE SNR FOR BICEPS
    # compute power of noise in upper 20% of freq data (adjusted for less data total)
    noise_power_bic = np.sum(Pxx_bic[f_ind_upper])/len(f_ind_upper)*len(f)
    
    # compute total power as sum of PSD
    total_power_bic = np.sum(Pxx_bic)
    SNR_bic = total_power_bic/noise_power_bic
    
    # COMPUTE SNR FOR TRICEPS
    # compute power of noise in upper 20% of freq data (adjusted for less data total)
    noise_power_tri = np.sum(Pxx_tri[f_ind_upper])/len(f_ind_upper)*len(f)
    
    # compute total power as sum of PSD
    total_power_tri = np.sum(Pxx_tri)
    SNR_tri = total_power_tri/noise_power_tri
    
    
    SNR = [10*np.log10(SNR_bic),10*np.log10(SNR_tri)]
    return SNR

def get_LE(data,fs):
    # demean EMG signal
    bic_demean = data["Biceps (V)"].values-np.mean(data["Biceps (V)"].values)
    tri_demean = data["Triceps (V)"].values-np.mean(data["Triceps (V)"].values)
    
    # find FFT
    tri_fft = tri_demean
    bic_fft = bic_demean
    
    # create high pass butterworth filter (40 Hz, 4th order)
    sos = signal.butter(N=4,Wn=40,btype='hp',fs=fs, output='sos')
    
    # highpass filter at 40 Hz
    bic_hp = signal.sosfiltfilt(sos=sos,x=bic_demean)
    tri_hp = signal.sosfiltfilt(sos=sos,x=tri_demean)
    
    # rectify signal
    bic_rect = abs(bic_hp)
    tri_rect = abs(tri_hp)
    
    # create lowpass butterworth filter (40Hz, 4th order)
    sos = signal.butter(N=4,Wn=40,btype='lowpass',fs=fs, output='sos')
    
    # lowpass filter at 40 Hz
    bic_lp = signal.sosfiltfilt(sos=sos,x=bic_rect)
    tri_lp = signal.sosfiltfilt(sos=sos,x=tri_rect)
    
#     # compute RMS
#     window = np.ceil(0.3*fs)
#     bic_rms = []
#     for idx in range(int(len(bic_lp)-window)):
#         bic_rms.append(np.sqrt(1/window*np.sum([abs(x)**2 for x in bic_lp[idx:int(idx+window)]])))
#     bic_rms = np.asarray(bic_rms)
#     tri_rms = []
#     for idx in range(int(len(tri_lp)-window)):
#         tri_rms.append(np.sqrt(1/window*np.sum([abs(x)**2 for x in tri_lp[idx:int(idx+window)]])))
#     tri_rms = np.asarray(tri_rms)
      
    # compute average linear envenlope
    avg_LE = [np.mean(bic_lp),np.mean(tri_lp)]
    return avg_LE

def get_psd(data,fs):
    # demean EMG signal
    data["bic_demean"]= data["Biceps (V)"].values-np.mean(data["Biceps (V)"].values)
    data["tri_demean"]= data["Triceps (V)"].values-np.mean(data["Triceps (V)"].values)
    
    f, Pxx_bic = signal.welch(data["bic_demean"].values, fs=fs,detrend=False)
    f, Pxx_tri = signal.welch(data["tri_demean"].values, fs=fs,detrend=False)
    return f,Pxx_bic,Pxx_tri