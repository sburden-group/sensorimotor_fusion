#!/usr/bin/python

# code updated 070121 Amber
import warnings
warnings.filterwarnings("error")
import sys
import os
import glob
import time
from datetime import datetime
import serial
import serial.tools.list_ports
import importlib
import random
import csv as csv_
import numpy as np
import pygame
from protocols.globalsPython3 import *
from lib.ArduinoPython import slider as slider

def PyGame():

  scaleInput = 0.04616974606700115 #in input time domain out of -0.5~+0.5

  # size = (1000,250)
  RATIO = 1 #4
  if ORIENTATION == 'portrait':
    WIDTH = 800 #200
    size = (WIDTH,RATIO*WIDTH)
    SC = float(WIDTH) # modify SC to change lookahead
    SCi= WIDTH/4 #SCi= WIDTH
  else:
    HEIGHT = 400
    # HEIGHT = 200
    size = (RATIO*HEIGHT,HEIGHT)
    SC = float(HEIGHT) # modify SC to change lookahead
    SCi= HEIGHT


  # global constants
  FPS_ = 30
  FPS = FPS_

  WINDOW_MIN = -127.5  #0.
  WINDOW_MAX = 127.5   #4096.
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
  INP_SHIFT = -2. #-.5 #SHIP_SHIFT-4*RAD_SYS
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

  from protocols import dynamics
  proto = importlib.import_module('protocols.'+protocol)

  trial_gen = proto.trial_gen(subject,protocol)

  # --- helper functions for output to command line and graphical display

  # draw rectangle using frame-relative (x,y) coordinates
  def draw_rect(scr, col, sizes, thk):
    x,y,w,h = sizes
    c,r = xy2px([[x,y]],size,SC)[0]
    cw,rh = xy2px([[x+w,y+h]],size,SC)[0]
    #return pygame.draw.rect(scr,col,(c,r,int(SC*w),int(SC*h)),int(SC*thk))
    return pygame.draw.rect(scr,col,(c,r,cw-c,rh-r),int(SC*thk))

  def draw_circle(scr, col, sizes, r, thk):
    x,y = sizes
    px = xy2px([[x,y]],size,SC)[0]
    return pygame.draw.circle(scr,col,px,int(SC*r),int(SC*thk))

  def draw_lines(scr, col, clo, pts, thk):
    pxs = xy2px(pts,size,SC)
    return pygame.draw.lines(scr,col,clo,pxs,int(SC*thk))

  #def draw_line(scr, col, start_pos, end_pos, thk):
  #  pxs = xy2px(pts,size,SC)
  #  return pygame.draw.line(scr,col,start_pos,end_pos,pxs,int(SC*thk))

  def draw_polygon(scr, col, pts, thk):
    pxs = xy2px(pts,size,SC)
    return pygame.draw.polygon(scr,col,pxs,int(SC*thk))

  def draw_ref(scr, col, pts, thk):
    #return pygame.draw.lines(scr,WHITE,False,xy2px(pts,size,SC),10)
    pts = np.array(pts)
    diff = np.diff(pts,axis=0)
    perp = np.dot(diff,np.asarray([[0,1],[-1,0]]))
    nml = perp / np.sqrt(np.sum(perp**2,axis=1))[:,np.newaxis]
    pts_u = pts[:-1] + .2*thk * nml
    pts_d = pts[:-1] - .2*thk * nml
    pxs = xy2px(np.vstack((pts_u,pts_d[::-1])),size,SC)
    return pygame.draw.polygon(scr,col,pxs,0)

  class Point:
    # constructed using a normal tuple
    def __init__(self, point_t = (0,0)):
      self.x = float(point_t[0])
      self.y = float(point_t[1])
    # define all useful operators
    def __add__(self, other):
      return Point((self.x + other.x, self.y + other.y))
    def __sub__(self, other):
      return Point((self.x - other.x, self.y - other.y))
    def __mul__(self, scalar):
      return Point((self.x*scalar, self.y*scalar))
    def __div__(self, scalar):
      return Point((self.x/scalar, self.y/scalar))
    def length(self):
      return int(np.sqrt(self.x**2 + self.y**2))
    # get back values in original tuple format
    def get(self):
        return (self.x, self.y)

  def draw_dashed_line(surf, color, start_pos, end_pos, width=1, dash_length=10):
    origin = Point(xy2px([start_pos],size,SC)[0])
    target = Point(xy2px([end_pos],size,SC)[0])
    displacement = target - origin
    length = displacement.length()
    slope = displacement/length

    for index in range(0, length/dash_length, 2):
      start = origin + (slope *    index    * dash_length)
      end   = origin + (slope * (index + 1) * dash_length)
      pygame.draw.line(surf, color, start.get(), end.get(), width)

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

  # --- set up graphical display window

  # global variables
  FULLSCREEN = False
  #FULLSCREEN = True

  REACT_NUM = 0

  if FULLSCREEN:
    flags = pygame.FULLSCREEN #| pygame.DOUBLEBUF
  else:
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    os.environ['SDL_VIDEO_WINDOW_POS'] = '%d,%d'%(0,0)
    flags = pygame.RESIZABLE #| pygame.DOUBLEBUF
  screen = pygame.display.set_mode(size,flags)
  screen.set_alpha(None)
  fader = pygame.Surface(size, pygame.SRCALPHA)
  pygame.display.set_caption("hcps v0.1")
  pygame.event.set_allowed([pygame.QUIT,
                            pygame.KEYDOWN,
                            pygame.KEYUP,
                            pygame.VIDEORESIZE,
                            pygame.MOUSEBUTTONDOWN,
                            pygame.MOUSEBUTTONUP,
                          ])
  pygame.font.init()
  font = pygame.font.SysFont('Comic Sans MS',30)
  done = False
  clock = pygame.time.Clock()

  # --- variables and functions for ship and reference

  oldrects = []

  def rescale_inp(Threeinp): 
      return [i/scaleInput for i in Threeinp]
      # return [2 * i * trial['scale'] * (3./2.) for i in Threeinp]
      # return 2 * ( (inp - MIN) / (MAX - MIN) - .5) * trial['scale'] * (3./2.)

  try:
    trial = trial_gen.__next__()
    if not ALLOW_DUPLICATES:
      while len(glob.glob(os.path.join(subject_dir,'*'+protocol+'_'+str(trial['id'])+'.npz'))) > 0:
        dbg('SKIP subject='+subject_dir+'; protocol='+protocol+'_'+str(trial['id']))
        trial = trial_gen.__next__()
      dbg('RUN subject='+subject_dir+'; protocol='+protocol+'_'+str(trial['id']))
  except StopIteration:
    done = True

  trial_run = trial

  trial_reset = dict(duration=np.inf,
                    id=trial['id'],
                    scale=.5,
                    init=[0.],
                    dis=lambda t,x,_ : 0.,
                    out=lambda x : x[0],
                    ref=lambda t,_ : 0.*np.asarray(t),
                    vf='fo',
                    RAND_TIME=random.uniform(0,REACT_TIME-2.),
                    RAND_POINT=random.uniform(-.5,.5))

  def init(trial):
    state = trial['init']
    steps = 0
    _time = steps * STEP
    time_ = [_time]
    realtime_ = [time.time()]
    state_ = [state]
    Threeinp = inp(time_[-1],state_[-1])
    inp_ = [Threeinp[0]]
    inp0_ = [Threeinp[1]]
    inp1_ = [Threeinp[2]]
    dis_ = [trial['dis'](time_[-1],trial,state_[-1])]
    out_ = [trial['out'](state)]
    ref_ = [trial['ref'](time_[-1],trial)*SC_REF]
    return state,steps,_time,time_,realtime_,state_,inp_,inp0_,inp1_,dis_,out_,ref_

  def save(sfx='',csv=True,**trial_data):
    di = subject_dir
    id = str(trial['id'])
    fi = protocol+'_'+id+sfx
    if glob.glob(os.path.join(di,'*'+fi+'.npz')):
      dbg('WARN -- trial repeated')
    ds = datestring(sec=True)
    fi = ds+'_'+fi
    dbg('SAVE '+os.path.join(di,fi))
    np.savez(os.path.join(di,fi),filename=fi,**trial_data) #TODO check to see if this is working
    #if not sfx:
    #  err = np.sqrt(np.mean((np.asarray(trial_data['ref_'])-np.asarray(trial_data['state_']))**2))
    #  print(err)
    if csv:
      time = trial_data['time_']
      realtime = trial_data['realtime_']
      ref = trial_data['ref_']
      inp = trial_data['inp_']
      dis = np.asarray(trial_data['dis_']).flatten()
      state = np.asarray(trial_data['state_'])
      d = np.vstack((time,realtime,ref,inp,dis,state.T)).T
      np.savetxt(os.path.join(di,fi)+'.csv',d,delimiter=',',
                  header='\n'.join(10*['']+['time,realtime,ref,inp,dis,state...']))

  def saveEMG(sfx='',csv=True,**trial_data):
    di = subject_dir
    id = str(trial['id'])
    fi = protocol+'_'+id+sfx
    if glob.glob(os.path.join(di,'*'+fi+'.npz')):
      dbg('WARN -- trial repeated')
    ds = datestring(sec=True)
    fi = ds+'_'+fi
    dbg('SAVE '+os.path.join(di,fi))
    np.savez(os.path.join(di,fi),filename=fi,**trial_data) #TODO check to see if this is working
    #if not sfx:
    #  err = np.sqrt(np.mean((np.asarray(trial_data['ref_'])-np.asarray(trial_data['state_']))**2))
    #  print(err)
    if csv:
      time = trial_data['time_']
      realtime = trial_data['realtime_']
      ref = trial_data['ref_']
      inp = trial_data['inp_']
      inp0 = trial_data['inp0_']
      inp1 = trial_data['inp1_']
      dis = np.asarray(trial_data['dis_']).flatten()
      state = np.asarray(trial_data['state_'])
      d = np.vstack((time,realtime,ref,inp,inp0,inp1,dis,state.T)).T
      np.savetxt(os.path.join(di,fi)+'.csv',d,delimiter=',',
                  header='\n'.join(10*['']+['time,realtime,ref,inp,inp0,inp1,dis,state...']))
      # np.savetxt(os.path.join(di,fi)+'.csv',d,delimiter=',',
      #             header='\n'.join(10*['']+['time,realtime,ref,inp,dis,state...']))
      # if 'rst' not in sfx:
      #     with open(os.path.join(di,fi)+'_EMG.csv','w',newline='') as csvfile:
      #         csvwriter = csv_.writer(csvfile)
      #         while not q3.empty():
      #             csvwriter.writerow(q3.get())
      # else:
      #     with q3.mutex:
      #         q3.queue.clear()

      if joy is not None:
        with open(os.path.join(di,fi)+'_EMG.csv','w',newline='') as csvfile:
            csvwriter = csv_.writer(csvfile)
            while not joy.q_all.empty():
                csvwriter.writerow(joy.q_all.get())

  # def save(sfx='',csv=True,**trial_data):
  #   di = subject_dir
  #   id = str(trial['id'])
  #   fi = protocol+'_'+id+sfx
  #   if glob.glob(os.path.join(di,'*'+fi+'.npz')):
  #     dbg('WARN -- trial repeated')
  #   ds = datestring(sec=True)
  #   fi = ds+'_'+fi
  #   dbg('SAVE '+os.path.join(di,fi))
  #   np.savez(os.path.join(di,fi),filename=fi,**trial_data) #TODO check to see if this is working
  #   #if not sfx:
  #   #  err = np.sqrt(np.mean((np.asarray(trial_data['ref_'])-np.asarray(trial_data['state_']))**2))
  #   #  print(err)
  #   if csv:
  #     time = trial_data['time_']
  #     realtime = trial_data['realtime_']
  #     ref = trial_data['ref_']
  #     inp = trial_data['inp_']
  #     dis = np.asarray(trial_data['dis_']).flatten()
  #     state = np.asarray(trial_data['state_'])
  #     d = np.vstack((time,realtime,ref,inp,dis,state.T)).T
  #     np.savetxt(os.path.join(di,fi)+'.csv',d,delimiter=',',
  #               header='\n'.join(10*['']+['time,realtime,ref,inp,dis,state...']))  

  def savereact(sfx='',csv=True,**trial_data):
    di = subject_dir
    id = str(trial['id'])
    fi = protocol+'_'+id+sfx
    if glob.glob(os.path.join(di,'*'+fi+'.npz')):
      dbg('WARN -- trial repeated')
    ds = datestring(sec=True)
    fi = ds+'_'+fi
    dbg('SAVE '+os.path.join(di,fi))
    np.savez(os.path.join(di,fi),filename=fi,**trial_data) #TODO check to see if this is working
    #if not sfx:
    #  err = np.sqrt(np.mean((np.asarray(trial_data['ref_'])-np.asarray(trial_data['state_']))**2))
    #  print(err)
    if csv:
      time = trial_data['time_']
      realtime = trial_data['realtime_']
      ref = trial_data['ref_']
      inp = trial_data['inp_']
      reacttime = np.ones((len(time),))*trial_data['reacttime']
      reactpoint = np.ones((len(time),))*trial_data['reactpoint']
      dis = np.asarray(trial_data['dis_']).flatten()
      state = np.asarray(trial_data['state_'])
      d = np.vstack((time,realtime,ref,inp,dis,state.T,reacttime,reactpoint)).T
      np.savetxt(os.path.join(di,fi)+'.csv',d,delimiter=',',
                header='\n'.join(10*['']+['time,realtime,ref,inp,dis,state,reacttime,reactpoint...']))


  # -- initialize system
  if COM_PORT is None:
    inp = lambda time,state : [0.,0.,0.]

  else:
    inp = lambda time,state : rescale_inp(joy.grabData(EMGweight)) #joy.grabData() returns three inputs
  #
  TRIAL_STATE = 'reset1'
  trial = trial_reset
  # DEBUG
  #TRIAL_STATE = 'run'
  #trial = trial_run
  #
  state,steps,_time,time_,realtime_,state_,inp_,inp0_,inp1_,dis_,out_,ref_ = init(trial)

  # runge-kutta numerical integration assuming constant input
  def rk_(vf,t,x,u,d=None,dt=1.):
    dx1 = vf( t, x, u, d ) * dt
    dx2 = vf( t+.5*dt, x+.5*dx1, u, d ) * dt
    dx3 = vf( t+.5*dt, x+.5*dx2, u, d ) * dt
    dx4 = vf( t+dt, x+dx3, u, d ) * dt
    dx = (1./6.)*( dx1 + 2*dx2 + 2*dx3 + dx4 )
    return x + dx #every x should be x-d[-1]


  if PLOT:
    plt.ion()

    fig = plt.figure(1,figsize=(size[0]/100,size[1]/100))
    plt.clf()
    plt.grid('on'); plt.axis('equal')
    plt.xlim(RNG[:,0])
    plt.ylim(RNG[:,1])

  # ---- game loop

  while not done:

    # only handle events every SLIDER_SPT ticks
    if steps % SLIDER_SPT == 0:
      # --- handle events (keyboard / mouse input)
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          dbg("QUIT")
          done = True
        elif event.type == pygame.VIDEORESIZE:
          size = list(event.size)
          if ORIENTATION == 'portrait':
            WIDTH = size[0]
            size = (WIDTH,RATIO*WIDTH)
            SC = float(WIDTH) # modify SC to change lookahead
            SCi = WIDTH
            RNG = np.asarray(px2xy([[0.,0.],size],size,SC))
            SC_REF = (RNG[1,0]-RNG[0,0])
          else:
            HEIGHT = size[0]/RATIO
            size = (RATIO*HEIGHT,HEIGHT)
            SC = float(HEIGHT)
            SCi = HEIGHT
            RNG = np.asarray(px2xy([[0.,0.],size],size,SC))
            SC_REF = (RNG[1,1]-RNG[0,1])
          screen = pygame.display.set_mode(size,pygame.RESIZABLE)
          fader = pygame.Surface(size, pygame.SRCALPHA)
          dbg("RESIZE %s"%str(size))
        elif event.type == pygame.KEYDOWN:
          #dbg("KEYDOWN")
          if event.key in [pygame.K_SPACE,pygame.K_p]:
            if PAUSE:
              dbg("UNPAUSE")
            if not PAUSE:
              dbg("PAUSE")
            PAUSE = not PAUSE
          elif event.key == pygame.K_RIGHT:
            dbg("RIGHT")
            inp = lambda time,state : [+ACCEL,+ACCEL,+ACCEL]
          elif event.key == pygame.K_LEFT:
            dbg("LEFT")
            inp = lambda time,state : [-ACCEL,-ACCEL,-ACCEL]
          elif event.key == pygame.K_DOWN:
            dbg("DOWN")
            inp = lambda time,state : [0.,0.,0.]
          elif event.key == pygame.K_g:
            pass
          elif event.key == pygame.K_f:
            if FULLSCREEN:
              screen = pygame.display.set_mode(size,pygame.RESIZABLE)
              FULLSCREEN = False
            else:
              screen = pygame.display.set_mode(size,pygame.FULLSCREEN)
              FULLSCREEN = True
          elif event.key == pygame.K_s and COM_PORT is not None:
            inp = lambda time,state : rescale_inp(joy.grabData(EMGweight)) #joy.grabData() returns three inputs

          elif event.key == pygame.K_r:
            cmt = raw_input("> why reject? ")
            save(time_=time_,realtime_=realtime_,state_=state_,
                inp_=inp_,dis_=dis_,out_=out_,ref_=ref_,
                sfx="_rej",cmt=cmt)
            trial = trial_reset
            state,steps,_time,time_,realtime_,state_,inp_,inp0_,inp1_,dis_,out_,ref_ = init(trial)
          elif event.key in [pygame.K_q,pygame.K_ESCAPE]:
            dbg("QUIT")
            done = True
        #elif event.type == pygame.KEYUP:
        #  #dbg("KEYUP")
        #  if event.key in [pygame.K_LEFT,pygame.K_RIGHT]:
        #    dbg("0.")
        #    inp = lambda time,state : 0.
        elif event.type == pygame.MOUSEBUTTONDOWN:
          pass
          #dbg("MOUSEBUTTONDOWN")
        elif event.type == pygame.MOUSEBUTTONUP:
          pass
          #dbg("MOUSEBUTTONUP")

    _Threeinp = inp(time_[-1],state_[-1])
    _inp = _Threeinp[0] #fusion (1-EMGweight)*slider + EMGweight*EMG
    _inp0 = _Threeinp[1] #emg in fusion
    _inp1 = _Threeinp[2] #slider in fusion
    _dis = trial['dis'](time_[-1],trial,state_[-1])

    if not PAUSE:
      # duration
      if TRIAL_STATE == 'run' and _time + SHIP_SHIFT > trial['duration']:
        saveEMG(time_=time_,realtime_=realtime_,state_=state_,inp_=inp_,inp0_=inp0_,inp1_=inp1_,dis_=dis_,out_=out_,ref_=ref_)

        try:
          trial = trial_gen.__next__()
          if not ALLOW_DUPLICATES:
            while len(glob.glob(os.path.join(subject_dir,'*'+protocol+'_'+str(trial['id'])+'.npz'))) > 0:
              dbg('SKIP subject='+subject_dir+'; protocol='+protocol+'_'+str(trial['id']))
              trial = trial_gen.__next__()
          dbg('RUN subject='+subject_dir+'; protocol='+protocol+'_'+str(trial['id']))
          TRIAL_STATE = 'reset0'
          trial_reset['init'] = [_inp]
          trial = trial_reset
          state,steps,_time,time_,realtime_,state_,inp_,inp0_,inp1_,dis_,out_,ref_ = init(trial)
        except StopIteration:
          done = True

      if TRIAL_STATE == 'reset0':
        if time_[-1] >= CONGRATULATIONS_TIME:
          save(time_=time_,realtime_=realtime_,state_=state_,inp_=inp_,dis_=dis_,out_=out_,ref_=ref_,sfx="_rst0")
          TRIAL_STATE = 'reset1'
          trial_reset['init'] = [_inp]
          trial = trial_reset
          state,steps,_time,time_,realtime_,state_,inp_,inp0_,inp1_,dis_,out_,ref_ = init(trial)
          FADE = -1

      if TRIAL_STATE == 'reset1':
        if (np.abs(out_[-FPS*SLIDER_SPT:]).max() > .5):
          save(time_=time_,realtime_=realtime_,state_=state_,inp_=inp_,dis_=dis_,out_=out_,ref_=ref_,sfx="_rst1")
          TRIAL_STATE = 'reset2'
          trial_reset['init'] = [_inp]
          trial = trial_reset
          state,steps,_time,time_,realtime_,state_,inp_,inp0_,inp1_,dis_,out_,ref_ = init(trial)
          FADE = -1

      if TRIAL_STATE == 'reset2':
        if (np.abs(out_[-FPS*SLIDER_SPT:]).max() < RAD_SYS*8):
          save(time_=time_,realtime_=realtime_,state_=state_,inp_=inp_,dis_=dis_,out_=out_,ref_=ref_,sfx="_rst2")
          if REACT_NUM < REACT_THRESH:
              TRIAL_STATE = 'react'
              REACT_NUM = REACT_NUM + 1
              trial_reset['init'] = [_inp]
              trial_reset['RAND_TIME']=random.uniform(0,REACT_TIME-2.)
              trial_reset['RAND_POINT']=random.uniform(-.5,.5)
              trial = trial_reset
          else:
              TRIAL_STATE = 'run'
              trial = trial_run
          state,steps,_time,time_,realtime_,state_,inp_,inp0_,inp1_,dis_,out_,ref_ = init(trial)
          FADE = -1

      if TRIAL_STATE == 'react': # test reaction time
        if time_[-1] >= REACT_TIME:
          savereact(time_=time_,realtime_=realtime_,state_=state_,inp_=inp_,dis_=dis_,
              out_=out_,ref_=ref_,reacttime=trial_reset['RAND_TIME'],reactpoint=trial_reset['RAND_POINT'],sfx="_react")
          TRIAL_STATE = 'reset1'
          trial_reset['init'] = [_inp]
          trial_reset['RAND_TIME']=random.uniform(0,REACT_TIME-2.)
          trial_reset['RAND_POINT']=random.uniform(-.5,.5)
          trial = trial_reset
          state,steps,_time,time_,realtime_,state_,inp_,inp0_,inp1_,dis_,out_,ref_ = init(trial)
          FADE = -1

      ## out of bounds
      #if np.abs(out_[-1]) > 0.5:
      #  save(time_=time_,realtime_=realtime_,state_=state_,inp_=inp_,dis_=dis_,out_=out_,ref_=ref_,sfx="_oob")
      #  state,steps,_time,time_,realtime_,state_,inp_,dis_,out_,ref_ = init(trial)
      #  PAUSE = True

      ## saturated input
      #if np.abs(_inp/(trial['scale']*3./2.)) > .95:
      #  save(time_=time_,realtime_=realtime_,state_=state_,inp_=inp_,dis_=dis_,out_=out_,ref_=ref_,sfx="_max")
      #  state,steps,_time,time_,realtime_,state_,inp_,dis_,out_,ref_ = init(trial)
      #  PAUSE = True

      if TRIAL_STATE in ['run','reset0','reset1','reset2','react']:
        steps += 1
        _time = steps * STEP
        # --- update game state
        if TRIAL_STATE in 'run':
          state = rk_(eval('dynamics.'+trial['vf']),_time,state,_inp,_dis,STEP)
        else:
          state = [_inp]
        # --- record game state
        realtime_.append(time.time())
        time_.append(_time)
        state_.append(state)
        inp_.append(_inp)
        inp0_.append(_inp0)
        inp1_.append(_inp1)
        dis_.append(_dis)
        out_.append(trial['out'](state))
        ref_.append(trial['ref']([SHIP_SHIFT + _time,_time],trial)[0]*SC_REF)
        if not TRIAL_STATE == 'reset0':
          # --- compute error (MSE)
          err = np.sqrt(np.mean((np.asarray(ref_)-np.asarray(out_))**2))
          # --- compute error (total error)
          # err = np.sqrt(np.sum(np.asarray(ref_)-np.asarray(out_))**2)

    # only draw every SLIDER_SPT ticks -- SPT = samples per tick
    if steps % SLIDER_SPT == 0 and not done:

      if TRIAL_STATE in ['run']:
        bg_color = BLACK
        ref_color = GOLD
        out_color = PURPLE
      elif TRIAL_STATE in ['reset0','reset1','reset2','react']:
        bg_color = BLACK
        ref_color = GOLD
        out_color = PURPLE

      # --- draw
      screen.fill(bg_color) # this will occlude any drawing above


      if SHOW_GRID:
        xticks = np.arange(-RATIO/2,RATIO/2,.5)
        for g in xticks:
          draw_dashed_line(screen, DARKGREY, (g,YRNG[0]), (g,YRNG[1]),
                          width=1, dash_length=10)
        #yticks = np.hstack((-np.arange(-(SHIP_SHIFT-GRID_SPACE),-(XRNG[0]-GRID_SPACE),GRID_SPACE)[::-1],np.arange(SHIP_SHIFT,XRNG[1]+GRID_SPACE,GRID_SPACE)))# - np.mod(_time,GRID_SPACE)
        yticks = np.arange(-1,1,.5)
        for g in yticks:
          draw_dashed_line(screen, DARKGREY, (XRNG[0],g), (XRNG[1],g),
                          width=1, dash_length=10)
      #
      rects = []
      if TRIAL_STATE in ['run']:
        #TIMES = np.linspace(XRNG[0]-2*THK_REF,XRNG[1]+THK_REF,size[0]/10)
        # TIMES = np.linspace(-0.5-THK_REF,0.5+THK_REF,int(SCi/10))
        TIMES = np.linspace(-2-THK_REF,2+THK_REF,int(SCi/5)) #new look ahead 2.5 sec

        pts = np.vstack((trial['ref'](TIMES + _time,trial),TIMES)).T
        #pts = pts[np.all(np.logical_not(np.isnan(pts),),axis=1)]
        pts = pts[np.all(np.isfinite(pts),axis=1)]
        # reference curve
        if SHOW_REF:
          rects.append(draw_ref(screen, ref_color, pts, THK_REF))
        # reference glyph
        pts = [ref_[-1],0] + np.asarray([[-RAD_SYS,0],[0,RAD_SYS],[RAD_SYS,0],[0,-RAD_SYS]])
        rects.append(draw_polygon(screen, out_color, pts, THK_SYS))
        #rects.append(draw_rect(screen, ref_color, (ref_[-1]+SHIP_SHIFT-RAD_SYS,-RAD_SYS, 2*RAD_SYS, 2*RAD_SYS), THK_SYS))

        # error bars
        # instantaneous
        #rects.append(draw_rect(screen, out_color, (0,+THK_REF/2,-THK_REF,ref_[-1]), 0))
        rects.append(draw_rect(screen, out_color, (out_[-1],-THK_REF/4,ref_[-1]-out_[-1],THK_REF/2), 0))
        # if (out_[-1]) > 2:
        #   out_max = 2.5
        #   rects.append(draw_rect(screen, out_color, (out_max,-THK_REF/4,ref_[-1]-out_max,THK_REF/2), 0))
        # elif (out_[-1]) < -2:
        #   out_min = -2.5
        #   rects.append(draw_rect(screen, out_color, (out_min,-THK_REF/4,ref_[-1]-out_min,THK_REF/2), 0))
        # else:
        #   rects.append(draw_rect(screen, out_color, (out_[-1],-THK_REF/4,ref_[-1]-out_[-1],THK_REF/2), 0))
        # MSE bar
        #rects.append(draw_lines(screen, WHITE, False, [(RATIO/2-THK_REF,-.5),(RATIO/2-THK_REF,-.5+np.arctan(err/MSE_SCALE)/(np.pi/2))], 2*THK_REF))
      elif TRIAL_STATE in ['reset0']:
        # MSE bar
        MSE = np.arctan(err/MSE_SCALE)/(np.pi/2)
        # rects.append(draw_lines(screen, WHITE, False, [(RATIO/2-THK_REF,-.5),(RATIO/2-THK_REF,-.5+MSE)], 2*THK_REF))
        # MSE text
        text = font.render('%d%% !!!'%int(100*MSE), False, WHITE)
        w,h = text.get_rect().width,text.get_rect().height
        screen.blit(text,[(size[0]-w)/2,size[1]/4])
      elif TRIAL_STATE in ['react']:
        if time_[-1] > trial_reset['RAND_TIME']:
          rects.append(draw_rect(screen, out_color, (trial_reset['RAND_POINT'],-.5,2*RAD_SYS,+1.),THK_SYS))
          #pts = [out_[-1],0] + np.asarray([[-RAD_SYS,0],[0,RAD_SYS],[RAD_SYS,0],[0,-RAD_SYS]])
          #rects.append(draw_polygon(screen, out_color, pts, THK_SYS))
      elif TRIAL_STATE in ['reset1']:
        #rects.append(draw_rect(screen, ref_color, (-RATIO/2,0.5,RATIO/2-.5,1.),THK_SYS))
        #rects.append(draw_rect(screen, ref_color, (.5,1.,RATIO/2-.5,+RATIO/2),THK_SYS))
        rects.append(draw_rect(screen, ref_color, (-.5,-2,-RATIO*2,4.),THK_SYS))
        rects.append(draw_rect(screen, ref_color, (+.5,-2,+RATIO*2,4.),THK_SYS))
        #rects.append(draw_rect(screen, ref_color, (),THK_SYS))
      elif TRIAL_STATE in ['reset2','done']:
        #rects.append(draw_rect(screen, ref_color, (-RAD_SYS,1.,2*RAD_SYS,+2.),THK_SYS))
        # rects.append(draw_rect(screen, ref_color, (-RAD_SYS,-.5,2*RAD_SYS,+1.),THK_SYS))
        rects.append(draw_rect(screen, ref_color, (-RAD_SYS,-4.,2*RAD_SYS,+8.),THK_SYS))

      # output glyph
      #rects.append(draw_rect(screen, out_color, (out_[-1]+SHIP_SHIFT-.5*RAD_SYS,1.5*RAD_SYS, 1*RAD_SYS, 3*RAD_SYS), THK_SYS))
      pts = [out_[-1],0] + np.asarray([[-RAD_SYS,0],[0,RAD_SYS],[RAD_SYS,0],[0,-RAD_SYS]])
      rects.append(draw_polygon(screen, out_color, pts, THK_SYS))

      if SHOW_INP:
        # input
        rects.append(draw_lines(screen, WHITE, False, [[0.,INP_SHIFT],[_inp/(trial['scale']),INP_SHIFT]], THK_INP))
        # rects.append(draw_lines(screen, WHITE, False, [[0.,INP_SHIFT],[_inp,INP_SHIFT]], THK_INP))

      if SHOW_DIS:
        # input
        rects.append(draw_lines(screen, WHITE, False, [[0.,DIS_SHIFT],[_dis/(trial['scale']),DIS_SHIFT]], THK_DIS))
        # rects.append(draw_lines(screen, WHITE, False, [[0.,DIS_SHIFT],[_dis,DIS_SHIFT]], THK_DIS))


      activerects = rects + oldrects
      activerects = filter(bool, activerects)

      if PLOT:
        plt.clf()
        plt.grid('on'); plt.axis('equal')
        plt.plot(TIMES,trial['ref'](TIMES + _time,trial)*SC_REF,'.-',lw=10,color=_GOLD)
        plt.plot(SHIP_SHIFT,state[0],'.',ms=40,color=_PURPLE)
        if SHOW_GRID:
          plt.xticks(xticks)
        plt.xlim(XRNG)
        plt.ylim(YRNG)
        plt.yticks([])
        plt.draw()

      if FADE > 0:
        fader.fill((0.,0.,0.,FADE))
        screen.blit(fader,(0,0))
        FADE += 20
        if FADE >= 255:
          FADE = 0

      if FADE < 0:
        fader.fill((0.,0.,0.,255+FADE))
        screen.blit(fader,(0,0))
        FADE -= 20
        if FADE < -255:
          FADE = 0

      # --- update screen
      pygame.display.flip()

      #dbg('t = %0.1f, FPS = %0.1f' % (clock.get_time(),
      #                                clock.get_fps()))

    # --- limit update rate to FPS
    clock.tick(FPS*SLIDER_SPT)

    if (steps+1) % 60 == 0:
      dbg('%d t = %0.1f, FPS = %0.1f, inp = %0.1f, state = %s' %
          (len(inp_), time_[-1], clock.get_fps(), _inp, state))
  
  #print the last trial's MSE score
  MSE = np.arctan(err/MSE_SCALE)/(np.pi/2)
  print('%d%% !!!'%int(100*MSE))

  if COM_PORT is not None:
    joy.close()
  pygame.display.quit()
  pygame.quit()
  sys.exit(0)

if __name__ == '__main__':

  # -- Setup

  args = sys.argv

  help = """
  usage:
    experiment subject protocol [port]

  data will be stored in
    data/subject

  print available serial ports by running
    lib/print_serial
  """

  if len(args) < 2:
    print ('\nABORT -- no subject specified')
    print (help)
    sys.exit(0)

  if len(args) < 3:
    print ('\nABORT -- no protocol specified')
    print (help)
    sys.exit(0)

  subject = args[1]
  protocol = args[2]

  subject_dir = os.path.join('data',subject)

  # debugging
  def dbg(s):
    print(s)

  COM_PORT = None
  if len(args) >= 4:
    COM_PORT = args[3]
  elif 0:
    arduinoPorts = [p.device
      for p in serial.tools.list_ports.comports()
      if 'Arduino' in p.description
    ]
    COM_PORT = arduinoPorts[0]

  if len(args) >= 5:
    EMGweight = float(args[4])
  else: EMGweight = 0. 

  if COM_PORT is None:
    joy = None
    print ('WARN -- COM_PORT is None, using keyboard for input')
  else:
    try:
      joy = slider(port=COM_PORT)
    except:
      print ('ABORT -- slider not detected at COM_PORT =',COM_PORT)
      sys.exit(0)

    dbg('COM_PORT='+COM_PORT)

    joy.startArduino()
    
  if not os.path.exists(subject_dir):
    os.mkdir(subject_dir)

  PyGame()