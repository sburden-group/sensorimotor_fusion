import numpy as np

def zero(t, trial, x=None, *args, **kwargs):
  return 0.*np.asarray(t)

def spline_interp(x, x0, x1, y0, y1, dy0, dy1, return_dy=False, return_ddy=False):
  """
  spline_interp(...) samples cubic spline with given boundary conditions

  "symmetrical form" from:
  https://en.wikipedia.org/wiki/Spline_interpolation#Algorithm_to_find_the_interpolating_cubic_spline

  inputs:
    x - n array - sample points
    x0,x1 - scalars - initial, final sample
    y0,y1 - scalars - initial, final spline value
    dy0,dy1 - scalars - initial, final derivative value

  outputs:
    y - n array - cubic spline evaluated on samples
  """
  if np.allclose(x1,x0) or np.isinf(x0) or np.isinf(x1):
    return y0
  t = (x - x0) / (x1 - x0)
  a = dy0*(x1 - x0) - (y1 - y0)
  b = -dy1*(x1 - x0) + (y1 - y0)
  y = (1-t)*y0 + t*y1 + t*(1-t)*(a*(1-t) + b*t)
  dy = (y1-y0)/(x1-x0) + (1-2*t)*(a*(1-t)+b*t)/(x1-x0)+t*(1-t)*(b-a)/(x1-x0)
  ddy = 2*(b-2*a+(a-b)*3*t)/(x1-x0)**2
  r = [y]
  if return_dy:
    r.append(dy)
  if return_ddy:
    r.append(ddy)
  return r

def spline(t, trial, x=None):
  # TODO this function fails when t is scalar
  t = np.asarray(t)
  conds = np.asarray([np.logical_and(t0 <= t, t <= t1) for t0,t1,y0,y1 in trial['pts']])
  if t.size == 1:
    conds = np.asarray([conds])
  keep = (np.sum(conds,axis=1) > 0)
  keep = keep.nonzero()[0]
  if len(keep) > 0:
    conds = conds[keep]
    funcs = [lambda t,t0=t0,t1=t1,y0=y0,y1=y1 : 
             spline_interp(t,t0,t1,y0,y1,0.,0.) 
             for t0,t1,y0,y1 in trial['pts'][keep]]
    return np.piecewise(t, conds, funcs)
  else:
    return np.nan*t

def sum_of_sines_ramp(t, trial, x=None, 
                      frequencies=None, amplitudes=None, phase_shifts=None, derivative = None):

  t = np.asarray(t).copy(); t.shape = (t.size,1)

  r = trial['ramp']

  _ = sum_of_sines(t, trial, x, frequencies, amplitudes, phase_shifts, derivative)

  if r > 0:
    _ *= ((t*(t <= r)/r + (t > r)).flatten())**2

  return _

def sum_of_sines(t, trial, x=None,
                 frequencies=None, amplitudes=None, phase_shifts=None, derivative = None):

  t = np.asarray(t).copy(); t.shape = (t.size,1)

  if frequencies is None:
    f = np.asarray(trial['frequencies'])
  else:
    f = frequencies
  f = f.copy(); f.shape = (1,f.size)

  if amplitudes is None:
    a = np.asarray(trial['amplitudes'])
  else:
    a = amplitudes
  a = a.copy(); a.shape = (1,a.size)

  if phase_shifts is None:
    p = np.asarray(trial['phase_shifts'])
  else:
    p = phase_shifts
  p = p.copy(); p.shape = (1,p.size)

  assert f.shape == a.shape == p.shape,"Shape of frequencies, amplitudes, and phase shifts must match"

  o = np.ones(t.shape)

  if derivative == None:
    _ = np.sum(np.dot(o,a) * np.sin(2*np.pi*(np.dot(t,f) + np.dot(o,p))),axis=1)
  elif derivative == 1:
    _ = np.sum(np.dot(o,a) * 2*np.pi*np.dot(o,f) * np.cos(2*np.pi*(np.dot(t,f) + np.dot(o,p))),axis=1)
  else:
    _ = np.sum(-np.dot(o,a) * 4*(np.pi*np.pi)*np.dot(o,f*f) * np.sin(2*np.pi*(np.dot(t,f) + np.dot(o,p))),axis=1)

  return _

