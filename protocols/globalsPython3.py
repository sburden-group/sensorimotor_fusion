import numpy as np

ORIENTATION = 'portrait'
#ORIENTATION = 'landscape'

# transform from absolute pixel (col,row) to frame-relative (x,y)
def px2xy(px,size,SC):
  return [[(_[0]-size[0]/2.)/SC,(_[1]-size[1]/2.)/SC] for _ in px]
  #if ORIENTATION == 'portrait':
  #  return [[(_[0]-size[0]/2.)/SC,(_[1]-size[1]/2.)/SC] for _ in px]
  #else:
  #  return [[(_[1]-size[0]/2.)/SC,(_[0]-size[1]/2.)/SC] for _ in px]

# transform from frame-relative (x,y) to absolute pixel (col,row)
def xy2px(xy,size,SC):
  SC = SC/4 #for new look ahead
  if ORIENTATION == 'portrait':
    return [[int(SC*_[1]+size[0]/2.),int(size[1]/2.-SC*_[0])] for _ in xy]
  else:
    return [[int(SC*_[0]+size[0]/2.),int(size[1]/2.-SC*_[1])] for _ in xy]

def datestring(t=None,sec=False):
  """
  Datestring

  Inputs:
    (optional)
    t - time.localtime()
    sec - bool - whether to include sec [SS] in output

  Outputs:
    ds - str - date in YYYYMMDD-HHMM[SS] format

  by Sam Burden 2012
  """
  if t is None:
    import time
    t = time.localtime()

  ye = '%04d'%t.tm_year
  mo = '%02d'%t.tm_mon
  da = '%02d'%t.tm_mday
  ho = '%02d'%t.tm_hour
  mi = '%02d'%t.tm_min
  se = '%02d'%t.tm_sec
  if not sec:
    se = ''

  return ye+mo+da+'-'+ho+mi+se

#size = (1200,800)
size = (1000,250)
RATIO = 4
if ORIENTATION == 'portrait':
  WIDTH = 200
  size = (WIDTH,RATIO*WIDTH)
  SC = float(WIDTH) # modify SC to change lookahead
  SCi= WIDTH
else:
  HEIGHT = 400
  HEIGHT = 200
  size = (RATIO*HEIGHT,HEIGHT)
  SC = float(HEIGHT) # modify SC to change lookahead
  SCi= HEIGHT


# global constants
FPS_ = 30
FPS = FPS_

SLIDER_MIN = 0.
SLIDER_MAX = 4096.
SLIDER_SPT = 2 # number of slider samples per pygame tick
SLIDER_SCALE = 5.

MSE_SCALE = 1.

CONGRATULATIONS_TIME = 3.

REACT_TIME = 10.
REACT_THRESH = 0 # change this to 5 


STEP = 1./(FPS*SLIDER_SPT)

PAUSE = False
#PAUSE = True

TRIAL_DONE = False

TRIAL_STATE = None

FADE = -1

ALLOW_DUPLICATES = False
#ALLOW_DUPLICATES = True

PLOT = False
#PLOT = True

SHOW_GRID = True
SHOW_GRID = False

SHOW_REF = True
#SHOW_REF = False

SHOW_INP = True
SHOW_INP = False

SHOW_DIS = True
SHOW_DIS = False

RNG = np.asarray(px2xy([[0.,0.],size],size,SC))
XRNG = RNG[:,0]
YRNG = RNG[:,1]
if ORIENTATION == 'portrait':
  SC_REF = (RNG[1,0]-RNG[0,0])
else:
  SC_REF = (RNG[1,1]-RNG[0,1])
ACCEL = 1.
RAD_SYS,THK_SYS = 5e-2,0.
THK_REF = 2*RAD_SYS
THK_INP = RAD_SYS
THK_DIS = RAD_SYS
#GRID_SPACE = 4*RAD_SYS
GRID_SPACE = 1.
SHIP_SHIFT = -.0
INP_SHIFT = -.5#SHIP_SHIFT-4*RAD_SYS
DIS_SHIFT = -.25#SHIP_SHIFT-4*RAD_SYS
TIMES = np.linspace(XRNG[0]-2*THK_REF,XRNG[1]+THK_REF,int(SCi/10))

HZ = 0.2


# colors
BLACK    = (   0,   0,   0)
WHITE    = ( 255, 255, 255)
GREEN    = (   0, 255,   0)
RED      = ( 255,   0,   0)
BLUE     = (   0,   0, 255)

GREY     = ( 247, 247, 247)
DARKGREY = (  47,  47,  47)
PURPLE   = ( 153, 142, 195)
GOLD     = ( 241, 163,  64)

_GREY     = np.array(( 247, 247, 247))/255.
_DARKGREY = np.array((  47,  47,  47))/255.
_PURPLE   = np.array(( 153, 142, 195))/255.
_GOLD     = np.array(( 241, 163,  64))/255.
