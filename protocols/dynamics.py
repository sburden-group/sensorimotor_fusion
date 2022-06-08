import numpy as np

def fo(t,x,u,d=None):
  """
  first-order
  """
  q = x
  dq = u
  if d is not None:
    dq += d
  return np.asarray([dq])

def so(t,x,u,d=None):
  """
  second-order 
  """
  # TODO make this compatible with natural frequency
  b = 1.0
  q,dq = x
  ddq = u
  if d is not None: #take out
    ddq += d
  return np.asarray([dq,ddq - b*dq])

def zd11(t,x,u,d=None):
  """
  first-order system dynamics
  first-order zero dynamics

  dxi = u
  dzeta = -c * (xi - zeta)
  """
  c = -1.
  x1,x2 = x
  return np.asarray([ u - c*x2, u + c*x2 ])

def zd12(t,x,u,d=None): # USE THIS ONE!
  """
  first-order system dynamics
  second-order zero dynamics

  dxi = u
  ddzeta = c_1 (xi-zeta) + c_2 dzeta
  """
  c1, c2 = -1.,-1.
  xi,zeta,dzeta = x
  #return np.asarray([ u, dzeta, c1*zeta + c2*dzeta ])
  return np.asarray([ u, dzeta, -c1*(xi-zeta) + c2*dzeta ])

  #c1, c2 = -1.,-1.
  #x1,x2,x3 = x
  #return np.asarray([ u + x3, u - x3, c1*x2 + c2*x3 ])
