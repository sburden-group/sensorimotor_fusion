import sys
from copy import deepcopy

import numpy as np
#import pylab as plt
import matplotlib
from matplotlib import rc
#sys.path.append('C:\\Users\\BRL\\Momona\'s Google Drive\\Yamagami Lab_\\Slider Project\\hcps\\develop\\protocols')
sys.path.append('C:\\Users\\amber\\Documents\\VSCode\\basic\\protocols')
import globalsPython3

from dynamics import fo, so, zd11, zd12

from references import sum_of_sines_ramp as sos
from references import zero as zero
refs = dict(sos=sos,zer=zero)


# vector fields
#vfs = ['so']
vfs = ['so']
#vfs = ['fo','so','fo','so']
#
states = dict(fo=[0.],so=[0.,0.])
# time to complete task
dt = 1.
seed = 49
np.random.seed(seed)
#
period = 20 # sec
f_base = 1./period # Hz
# TODO go up to 3--5Hz -- check that Sam can track, and check when becomes sub-pixel
primes = np.asarray([2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199])
f_max = dict(fo=2,so=1)
p_max = dict([(vf,np.nonzero(primes*f_base <= f_max[vf])[0][-1]+1) for vf in vfs])
f_primes = dict([(vf,np.asarray(primes[:p_max[vf]])) for vf in vfs])
#
frequencies = dict([(vf,f_primes[vf]*f_base) for vf in vfs])
frequencies_r = frequencies.copy()
frequencies_d = frequencies.copy()
#
#print 'p_max = ',p_max,', primes[p_max] = ',primes[p_max]
amplitudes = dict([(vf,(1./f_primes[vf])*(0.5/f_primes[vf]).sum()) for vf in vfs])
amplitudes_r = amplitudes.copy()
amplitudes_d = amplitudes.copy()
#
num_refs = 15 # will generate double the number of refs
phase_shifts_r = dict([(vf,np.random.sample((num_refs,p_max[vf]))) for vf in vfs])

# only first disturbance signal differs from reference signals
#print phase_shifts_r
phase_shifts_d = deepcopy(phase_shifts_r)
shiftedPhase = {}
for vf in vfs:
    phase_shifts_d[vf][:] = phase_shifts_d[vf][:]*.8
#phase_shifts_d = dict([(vf,shiftedPhase[vf]) for vf in vfs])
# for vf in vfs:
#   phase_shifts_d[vf][0] = np.random.rand(p_max[vf])
#
ramp = 0.25*period
duration = 2*period + ramp
#
trial = dict(ramp=ramp,duration=duration)
# DEBUG

scale = dict(fo=0.,so=0.)
for vf in vfs:
  for _,phase_shift in enumerate(phase_shifts_r[vf]):
    t = np.arange(ramp,ramp+period,globalsPython3.STEP)
    dt = np.diff(t)
    r = sos(t,trial,None,frequencies_r[vf],amplitudes_r[vf],phase_shift)
    dr = np.diff(r)/dt
    ddr = np.diff(dr)/dt[1:]
    #
    if vf == 'fo':
      scale['fo'] = max(scale['fo'],np.abs(dr).max())
    elif vf == 'so':
      scale['so'] = max(scale['fo'],np.abs(dr).max())
#for phase_shift in phase_shifts_d:
#  trial = dict(ramp=ramp,duration=duration)
#  t = np.arange(ramp,ramp+period,globals.STEP)
#  d = np.abs(sos(t,trial,None,frequencies_d,amplitudes_d,phase_shift))
#  scale['fo'] = max(scale['fo'],d.max())
#  scale['so'] = max(scale['so'],d.max())
#

# randomize to provide random starting point
order = np.random.choice([0,1])
if order == 0:
    trialEO = [(1,'sos-E','sos+O'),(1,'sos-O','sos+E')]
elif order == 1:
    trialEO = [(1,'sos-O','sos+E'),(1,'sos-E','sos+O')]
def trial_gen(subject,protofile):
  for vf in vfs:
    for assay,(num_reps,ref_,dis_) in enumerate(trialEO*num_refs):

    # for assay,(num_reps,ref_,dis_) in enumerate([
    #                                     (1,'sos+E','sos+O'),
    #                                     (num_refs,'zer','sos+A'),
    #                                     (1,'sos+O','sos+E'),
    #                                     (num_refs,'sos+A','zer'),
    #                                     (1,'sos-E','sos+O'),
    #                                     (1,'sos-O','sos+E'),
    #                                     (1,'sos+E','sos+O'),
    #                                     ]):
      #for sgn in [+1,-1]:
        for shift_id in np.hstack((np.arange(1,num_reps),0)):#np.hstack((np.random.permutation(np.arange(1,num_reps)),0)):
            if ref_[-1] == 'E':
              sines_r = np.arange(p_max[vf])[0::2]
            elif ref_[-1] == 'O':
              sines_r = np.arange(p_max[vf])[1::2]
            else:
              sines_r = np.arange(p_max[vf])
            if dis_[-1] == 'E':
              sines_d = np.arange(p_max[vf])[0::2]
            elif dis_[-1] == 'O':
              sines_d = np.arange(p_max[vf])[1::2]
            else:
              sines_d = np.arange(p_max[vf])

            out = lambda x : x[0]

            ref = lambda t,trial,x=None : refs[ref_[:3]](t,trial,x,
                                                       frequencies_r[vf][sines_r],
                                                       amplitudes_r[vf][sines_r],
                                                       phase_shifts_r[vf][shift_id][sines_r])
            dis = lambda t,trial,x=None : refs[dis_[:3]](t,trial,x,
                                                       frequencies_d[vf][sines_d],
                                                       amplitudes_d[vf][sines_d],
                                                       phase_shifts_d[vf][shift_id][sines_d])
              #
            id = '%s_%s_r-%s_d-%s_s%d_p%da%d' % (subject,vf,ref_,dis_,seed,shift_id,assay)
            state = states[vf]
                  #
            trial.update(dict(id=id,init=state,vf=vf,ref=ref,dis=dis,out=out,scale=scale[vf],
                                   r=phase_shifts_r[vf][shift_id][sines_r][0],d=phase_shifts_d[vf][shift_id][sines_d][0]))
            yield trial


# plotting globals
lw = 1
col_out = 'indigo'
col_ref = 'darkorange'
col_inp = col_out
col_p_gain = 'dodgerblue'
col_pd_gain = 'dodgerblue'
alpha_trials = 0.0
alpha_fill = 0.2
#
ylim_out = (-1.,+1.)
#
prc = 0
prcs = [50,prc/2,100-prc/2]
do_bootstrap_means = False

def visualization(subject,protofile):
  ids = []; scales = []; jumps = []
  gen = trial_gen(subject,protofile)
  for trial in gen:
    id = trial['id']
    scale = trial['scale']
    sys,jump,i = id.split('_')
    if i[1:] in '0123456789' and sys in ['fo'] and jump[-1] in '12':
      ids.append(id)
      scales.append(scale)
      jumps.append(float(jump[1:]))
  #
  return dict(ids=ids,scales=scales,jumps=jumps)
