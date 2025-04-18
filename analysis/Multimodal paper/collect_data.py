"""
Amber 12/11/2024: 
This code collects the raw npz files from experiment and make it into data arrays. 
Still need to: Tur, Tud and Wr, Md. 
"""
import sys
import os
import glob
import numpy as np
import math as m
from globalVars import *
from scipy import signal

# find npz files for each trial
def findFilename(PATH, subject):
    fis = glob.glob(PATH+'\\data\\'+subject+'\\*.npz')
    fis = [os.path.basename(fi) for fi in fis]

    ids = sorted(list(set([fi.strip('.npz') for fi in fis])))
    #ids = [id for id in ids if ('.csv') not in id[-4:]]
    ids = [id for id in ids if ('rst2') not in id]
    ids = [id for id in ids if ('rst1') not in id]
    ids = [id for id in ids if ('rst0') not in id]
    ids = [id for id in ids if ('react') not in id]
    return ids

# combine all functions to get variables of interest
def getrawdata(PATH,subject):
    listofIDs = findFilename(PATH,subject) # npz file names

    trials = dict()
    for id in listofIDs:
        fis = sorted(glob.glob(PATH+'\\data\\'+subject+'\\'+id+'.npz'))
        if len(fis) > 1:
        	dbg('WARNING -- repeated trials for id ='+id)
        assert len(fis) > 0, 'ERROR -- no data for id ='+id
        fi = fis[-1]
        #print('LOAD '+fi)
        trial = dict(np.load(fi,encoding="latin1",allow_pickle=True))
        trials[id] = trial
    
    timedomainvalues = {}
    timedomainvalues[listofIDs[0]] = {}
    times_ = [trials[listofIDs[0]]['time_']]
    refs_  = [trials[listofIDs[0]]['ref_']]
    outs_  = [trials[listofIDs[0]]['out_']]
    inps_  = [trials[listofIDs[0]]['inp_']]
    inps0_ = [trials[listofIDs[0]]['inp0_']]
    inps1_ = [trials[listofIDs[0]]['inp1_']]
    dists_ = [trials[listofIDs[0]]['dis_']]

    timedomainvalues[listofIDs[0]]['times'] = np.hstack(times_)[-N:] # take out first 5 sec
    timedomainvalues[listofIDs[0]]['refs'] = np.hstack(refs_)[-N:]
    timedomainvalues[listofIDs[0]]['outs'] = np.hstack(outs_)[-N:]
    timedomainvalues[listofIDs[0]]['inps'] = np.hstack(inps_)[-N:]
    timedomainvalues[listofIDs[0]]['inp0s'] = np.hstack(inps0_)[-N:]
    timedomainvalues[listofIDs[0]]['inp1s'] = np.hstack(inps1_)[-N:]
    timedomainvalues[listofIDs[0]]['dists'] = np.hstack(dists_)[-N:]

    for id in listofIDs[1:]:
        times_ = [trials[id]['time_']]
        refs_  = [trials[id]['ref_']]
        outs_  = [trials[id]['out_']]
        inps_  = [trials[id]['inp_']]
        inps0_ = [trials[id]['inp0_']]
        inps1_ = [trials[id]['inp1_']]
        dists_ = [trials[id]['dis_']]
        timedomainvalues[id] = {}
        timedomainvalues[id]['times'] = (np.hstack(times_)[-N:]) # take out first 5 sec
        timedomainvalues[id]['refs']=(np.hstack(refs_)[-N:])
        timedomainvalues[id]['outs']=(np.hstack(outs_)[-N:])
        timedomainvalues[id]['inps']=(np.hstack(inps_)[-N:])
        timedomainvalues[id]['inp0s']=(np.hstack(inps0_)[-N:])
        timedomainvalues[id]['inp1s']=(np.hstack(inps1_)[-N:])
        timedomainvalues[id]['dists']=(np.hstack(dists_)[-N:])
    return timedomainvalues


# get all trial's data for each condition
def get_data(PATH,trial_name):
    time_so = {}
    keys = [trial_name]

    for key in keys:
        print('analyzing data for '+key)
        time_so[key] = getrawdata(PATH,key)
    
    # freq domain
    Rs = [] #reference
    Ds = [] #disturbance
    MDs = [] #Md in freq domain
    Us = [] #human input
    U0s = [] #human input emg
    U1s = [] #human input slider
    Ys = [] #output
    
    # time domain
    rs = [] #reference
    ds = [] #disturbance
    mds = [] #Md in time domain
    us = [] #human input
    u0s = [] #human input emg
    u1s = [] #human input slider
    ys = [] #output
    errors = [] #time domain errors (MSE per trial)

    for key in keys:
        for i,trial in time_so[key].items():
            refs = trial['refs'][-N:]
            outs = trial['outs'][-N:]
            inps = trial['inps'][-N:]
            inp0s = trial['inp0s'][-N:]
            inp1s = trial['inp1s'][-N:]
            dists = trial['dists'][-N:]
            REFS = np.fft.fft(refs)/N
            OUTS = np.fft.fft(outs)/N
            INPS = np.fft.fft(inps)/N
            INP0S = np.fft.fft(inp0s)/N
            INP1S = np.fft.fft(inp1s)/N
            DISTS = np.fft.fft(dists)/N
            M_D = M_all*DISTS # MD in freq domain
            M_D[0] = 0 #nan value
            M_d = IFFT(M_D,N) # Md in time domain

            # scale to screen/slider output to be 30% of the screen/slider size for visualization
            # i.e. scaled -15%~15%
            Rs.append(REFS*scaleOutputScreen) # freq domain
            Ds.append(DISTS*scaleInput) # freq domain
            MDs.append(M_D*scaleOutputScreen) # freq domain
            Us.append(INPS*scaleInput) # freq domain
            U0s.append(INP0S*scaleInput) # freq domain
            U1s.append(INP1S*scaleInput) # freq domain
            Ys.append(OUTS*scaleOutputScreen) # freq domain

            rs.append(refs*scaleOutputScreen) # time domain
            ds.append(dists*scaleInput) # time domain
            mds.append(M_d*scaleOutputScreen) # time domain
            us.append(inps*scaleInput) # time domain
            u0s.append(inp0s*scaleInput) # time domain
            u1s.append(inp1s*scaleInput) # time domain
            ys.append(outs*scaleOutputScreen) # time domain
            errors.append(np.sum(abs(refs*scaleOutputScreen - outs*scaleOutputScreen)**2)) #MSE np.sum((r-y)**2)
    Rs = np.asarray(Rs)
    Ds = np.asarray(Ds)
    MDs = np.asarray(MDs)
    Us = np.asarray(Us)
    U0s = np.asarray(U0s)
    U1s = np.asarray(U1s)
    Ys = np.asarray(Ys)
    rs = np.asarray(rs)
    ds = np.asarray(ds)
    mds = np.asarray(mds)
    us = np.asarray(us)
    u0s = np.asarray(u0s)
    u1s = np.asarray(u1s)
    ys = np.asarray(ys) # 11 gains 
    errors = np.asarray(errors)
    return Rs,Ds,MDs,Us,U0s,U1s,Ys,rs,ds,mds,us,u0s,u1s,ys,errors

# analyze data for each subject each condition
def analyze(PATH,keys,trialID): 
    #(freq domain)
    Rs = [] #reference
    Ds = [] #disturbances 
    MDs = [] #Md in freq domain
    Us = [] #U_H user inputs
    U0s = [] #U_H user inputs emg
    U1s = [] #U_H user inputs slider
    Ys = [] #output 
    
    #(time domain)
    rs = [] #reference (time domain)
    ds = [] #disturbances (time domain)
    mds = [] #Md in time domain
    us = [] #U_H user inputs (time domain)
    u0s = [] #U_H user inputs emg (time domain)
    u1s = [] #U_H user inputs slider (time domain)
    ys = [] #output (time domain)
    errors = [] #time domain errors (MSE per trial)

    for key in keys:
        Rs_,Ds_,MDs_,Us_,U0s_,U1s_,Ys_,rs_,ds_,mds_,us_,u0s_,u1s_,ys_,errors_ = get_data(PATH,key+'\\'+key+trialID)
        Rs.append(Rs_)
        Ds.append(Ds_)
        MDs.append(MDs_)
        Us.append(Us_)
        U0s.append(U0s_)
        U1s.append(U1s_)
        Ys.append(Ys_)
        rs.append(rs_)
        ds.append(ds_)
        mds.append(mds_)
        us.append(us_)
        u0s.append(u0s_)
        u1s.append(u1s_)
        ys.append(ys_)
        errors.append(errors_)
    Rs = np.asarray(Rs) # participants x number of trials x number of time points
    Ds = np.asarray(Ds) # participants x number of trials x number of time points
    MDs = np.asarray(MDs) # participants x number of trials x number of time points
    Us = np.asarray(Us) # participants x number of trials x number of time points
    U0s = np.asarray(U0s) # participants x number of trials x number of time points
    U1s = np.asarray(U1s) # participants x number of trials x number of time points
    Ys = np.asarray(Ys) # participants x number of trials x number of time points
    rs = np.asarray(rs) # participants x number of trials x number of time points
    ds = np.asarray(ds) # participants x number of trials x number of time points
    mds = np.asarray(mds) # participants x number of trials x number of time points
    us = np.asarray(us) # participants x number of trials x number of time points
    u0s = np.asarray(u0s) # participants x number of trials x number of time points
    u1s = np.asarray(u1s) # participants x number of trials x number of time points
    ys = np.asarray(ys) # participants x number of trials x number of time points
    errors = np.asarray(errors) # participants x number of trials
    return Rs,Ds,MDs,Us,U0s,U1s,Ys,rs,ds,mds,us,u0s,u1s,ys,errors