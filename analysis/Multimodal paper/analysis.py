import numpy as np
import matplotlib.pyplot as plt
import warnings
import unittest
from scipy import signal, fft
from scipy.stats import wilcoxon
import sklearn
from sklearn import linear_model, metrics


def mean_and_interquartile(data, axis = 0):
    """
    calculate mean and interquartile range of data.
    how to use: 
    mean, quantile25, quantile50, quantile75 = mean_and_interquartile(data, axis)
    """
    mean = np.nanmean(data, axis = axis)
    q25, q50, q75 = np.nanpercentile(data, [25, 50, 75], axis=axis)
    return mean, q25, q50, q75


def WilcoxonTest(all_data):
    """Wilcoxon signed-rank test:  
    tests the null hypothesis that two related paired samples come from the same distribution
    """

    n = len(all_data)
    w = np.zeros(n**2)
    p = np.zeros(n**2)
    sig = np.zeros(n**2)
    flag = []
    k = 0
    for i in range(n):
        for j in range(n):
            if i != j:
                w[k], p[k] = wilcoxon(all_data[i],all_data[j])
                # determine significant (p<=0.05)
                if p[k] <= 0.05:
                    sig[k] = 1
            else: 
                w[k] = np.nan
                p[k] = np.nan
                sig[k] = np.nan #i=j
            
            if sig[k] == 1 and j > i:
                flag.append('there is significant difference between condition '+str(i)+' and condition '+str(j)+', w = '+str(w[k])+ ', pvalue = '+str(p[k]))
            
            k+=1    
    return w,p,sig,flag

def derivative(x, y, norm=True):
    '''
    Computes the derivative of y along x.

    Args:
        x (nt): independent variable, e.g. time
        y (nt, ...): dependent variable, e.g. position
        norm (bool, optional): also compute the norm of y if it is multidimensional (default True)

    Returns:
        nt: derivative of y
    '''
    dy = np.gradient(y, axis=0, edge_order=2)
    if norm and dy.ndim > 1:
        dy = np.linalg.norm(dy, axis=1)
    dx = np.gradient(x)
    dydx = dy/dx
    return dydx

def double_derivative(x, y, norm=True):
    '''
    Computes the double derivative of y along x.

    Args:
        x (nt): independent variable, e.g. time
        y (nt, ...): dependent variable, e.g. position
        norm (bool, optional): also compute the norm of y if it is multidimensional (default True)

    Returns:
        nt: double derivative of y
    '''
    ddy = np.gradient(np.gradient(y, axis=0, edge_order=2), axis=0, edge_order=2)
    if norm and ddy.ndim > 1:
        ddy = np.linalg.norm(ddy, axis=1)
    dx = np.gradient(x)
    ddydx = ddy/(dx**2)
    return ddydx
