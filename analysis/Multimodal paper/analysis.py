import numpy as np
import matplotlib.pyplot as plt
import warnings
import unittest
from scipy import signal, fft
from scipy.stats import wilcoxon
import sklearn
from sklearn import linear_model, metrics
from matplotlib.patches import Ellipse
import matplotlib.transforms as transforms

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



def confidence_ellipse(x, y, ax, n_std=2.0, facecolor='none', **kwargs):
    """
    Create a plot of the covariance confidence ellipse of *x* and *y*.

    Parameters
    ----------
    x, y : array-like, shape (n, )
        Input data.

    ax : matplotlib.axes.Axes
        The axes object to draw the ellipse into.

    n_std : float
        The number of standard deviations to determine the ellipse's radiuses.

    **kwargs
        Forwarded to `~matplotlib.patches.Ellipse`

    Returns
    -------
    matplotlib.patches.Ellipse
    """
    if x.size != y.size:
        raise ValueError("x and y must be the same size")

    cov = np.cov(x, y)
    pearson = cov[0, 1]/np.sqrt(cov[0, 0] * cov[1, 1])
    # Using a special case to obtain the eigenvalues of this
    # two-dimensionl dataset.
    ell_radius_x = np.sqrt(1 + pearson)
    ell_radius_y = np.sqrt(1 - pearson)
    ellipse = Ellipse((0, 0), width=ell_radius_x * 2, height=ell_radius_y * 2,
                      facecolor=facecolor, **kwargs)

    # Calculating the stdandard deviation of x from
    # the squareroot of the variance and multiplying
    # with the given number of standard deviations.
    scale_x = np.sqrt(cov[0, 0]) * n_std
    mean_x = np.mean(x)

    # calculating the stdandard deviation of y ...
    scale_y = np.sqrt(cov[1, 1]) * n_std
    mean_y = np.mean(y)

    transf = transforms.Affine2D() \
        .rotate_deg(45) \
        .scale(scale_x, scale_y) \
        .translate(mean_x, mean_y)

    ellipse.set_transform(transf + ax.transData)
    return ax.add_patch(ellipse)


def calc_rms(signal, remove_offset=True):
    '''
    Root mean square of a signal
    
    Args:
        signal (nt, ...): voltage along time, other dimensions will be preserved
        remove_offset (bool): if true, subtract the mean before calculating RMS
    Returns:
        float array: rms of the signal along the first axis. output dimensions will be the same non-time dimensions as the input signal
    '''
    if remove_offset:
        m = np.mean(signal, axis=0)
    else:
        m = 0
    
    return np.sqrt(np.mean(np.square(signal - m), axis=0))

def calc_time_domain_error_2d(X, Y, axis = 1):
    """calc_time_domain_error for 2d cursor

    Args:
        X (n_time x n_dim): time-series data of position, e.g. reference position (time x dimensions)
        Y (n_time x n_dim): time-series data of another position, e.g. cursor position (time x dimensions)
        axis (int): axis to calculate the Euclidean distance along

    Returns:
        td_error (n_time x 1): time-series data of the Euclidean distance between X position and Y position
    """
    # make sure that the shapes are the same
    assert(X.shape == Y.shape)
    td_error = np.linalg.norm(X - Y, axis=axis)
    return td_error

def frequency_domain(t,fs):
    """ 
    t = time array
    fs = sampling rate (Hz) 
    return:
      xf = positve freq array, length = half of the time array
      xf_all = full freq array, length = same as time array

    """
    N = len(t)                          #data length (time (s) * sampling rate)
    xf_all = fft.fftfreq(N, 1./ fs)     #freq (x-axis) both + and - terms
    xf = fft.fftfreq(N, 1./ fs)[:N//2]  #freq (x-axis) positive-frequency terms
    return xf, xf_all