from matplotlib import pyplot as plt, rcParams
from matplotlib import colors as mcolors

FIG_WIDTH = 7  # width of figure in inches

TINY_SIZE = 6
SMALL_SIZE = 8
MEDIUM_SIZE = 10
BIGGER_SIZE = 12
MARKER_SIZE = 5

plt.rc('font', size=SMALL_SIZE)  # controls default text sizes
plt.rc('axes', titlesize=TINY_SIZE)  # fontsize of the axes title #, titleweight='bold'
plt.rc('axes', labelsize=SMALL_SIZE)  # fontsize of the x and y labels
plt.rc('xtick', labelsize=TINY_SIZE)  # fontsize of the tick labels
plt.rc('ytick', labelsize=TINY_SIZE)  # fontsize of the tick labels
plt.rc('legend', fontsize=TINY_SIZE)  # legend fontsize
plt.rc('figure', titlesize=SMALL_SIZE)  # fontsize of the figure title

rcParams['lines.linewidth'] = 1
rcParams['lines.markersize'] = 2
rcParams['axes.spines.top'] = False
rcParams['axes.spines.right'] = False
rcParams['axes.titlesize'] = SMALL_SIZE
rcParams['font.weight'] = 'ultralight'
rcParams['font.family'] = 'sans-serif'
rcParams['mathtext.fontset'] = 'dejavusans'
rcParams['axes.linewidth'] = 1
rcParams['boxplot.boxprops.linewidth'] = 0.5
rcParams['boxplot.capprops.linewidth'] = 0.5
rcParams['boxplot.flierprops.linewidth'] = 0.5
rcParams['boxplot.whiskerprops.linewidth'] = 0.5
rcParams['boxplot.medianprops.linewidth'] = 0.5
rcParams['boxplot.meanprops.linewidth'] = 0.5
rcParams['hatch.linewidth'] = 0.5

PLOT_FOLDER = 'Figs/'  # folder path to save plots
DATA_FOLDER = 'Data/'  # folder path for data files

prop_cycle = plt.rcParams['axes.prop_cycle']
python_colors = prop_cycle.by_key()['color'] # python default color cycle


# plotting parameters
colors = dict(M='#6600CC',
              F='#000000',
              B='#FFFFFF',
              H='#009900',
              r='#FDB119',
              u='#009900',
              u25='#BBF90F',
              u75='#006400',
              d='#FD6E19',
              #y='#0033FF',  #or 6600CC which is darker and I prefer 
              y='#6600CC',  #or 6600CC which is darker and I prefer 
              N='#0000CC',
              D='#CC0000',
              g='#B1B1B1', #grey
              first5='#B1B1B1',
              last5='#999999',
              BLUE = '#1f77b4',
              ORANGE = '#ff7f0e',
              GREEN = '#2ca02c',
              RED = '#d62728',
              PURPLE = '#9467bd',
              GOLD = '#FDB119') #default colors
              # D = dominant = right; N = nondominant = left


yfill = list(mcolors.to_rgba(colors['y']))
yfill[-1] = 0.3

ufill = list(mcolors.to_rgba(colors['u']))
ufill[-1] = 0.3

gfill = list(mcolors.to_rgba(colors['g']))
gfill[-1] = 0.3

rfill = list(mcolors.to_rgba(colors['r']))
rfill[-1] = 0.3

bfill = list(mcolors.to_rgba(colors['BLUE']))
bfill[-1] = 0.3