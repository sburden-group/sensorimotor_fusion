**This project has been submitted to the CPHS 2022 and [bioRxiv](https://doi.org/10.1101/2022.06.29.498180). Please contact the corresponding author (hachou@uw.edu) before reusing the data.**

# sensorimotor fusion 

This version is based on version v4.2.5 of Amber's sensorfusion git repo. Working version for various gains (both EMG and slider).

# Arduino setup
Bottom EMG (A0, bicep), top EMG (A1, tricep), slider (A2, 3.3V).<br/>
Open Arduino IDE, upload sliderino (in lib) to Arduino.<br/>
Note: make sure the COM number after connection, change # in ArduinoPython.py

# SETTING UP 
(UPDATED 2021/5/24 by Amber Chou)

1. create virtual environment for python 3.5.4, [your path] -m venv venv35, for example: <br/>
`$ /Users/amber/AppData/Local/Programs/Python/Python35/python.exe -m venv venv35`<br/>
and then activate the virtual environment<br/>
`venv35\Scripts\activate.bat`<br/>

(or via conda)<br/>
`conda create --name my-project python=3.5.4 pip`<br/>
`conda activate my-project`<br/>
(back to base) `conda deactivate`<br/>

(view list of venv) `conda info --envs`<br/>


2. install correct versions of packages<br/>

`$ pip install -U matplotlib `<br/>
`$ pip install numpy==1.14.3 `<br/>
`$ pip install ipython==6.1.0 `<br/>
`$ pip install pygame==1.9.2 `<br/>
`$ pip install pyserial==3.2.1`<br/>


for spikershields EMG+slider (sensorfusion):<br/>

`$ pip install pandas` <br/>
`$ pip install scipy`


3. change to hcps directory, for example: <br/>
`$ cd /path/to/hcps/directory`

4. start ipython:<br/>
`$ ipython`<br/>
alternative: <br/>
`$ python`<br/>
`$ python -m IPython`<br/>
or:
`$ import IPython` <br/>
`$ IPython.embed()`

5. run experiment<br/>
`In [1]: run experiment subject protocol port EMGweight`<br/>
for example: `run expFusion HCPS1XX_fusion_emg50 Fusion21so COM4 0.5` <br/>
(Note: if using keyboard, press down to start the game, and then use left and right to control the diamond)

# RUNNING EXPERIMENT

**calibration**<br/>
`cd lib`<br/>
`python ArduinoPython.py`

**pygame**<br/>
`conda activate sensorfusion-venv`<br/>
`ipython`

**EMG only**<br/>
`run expFusion HCPS1XX_emg_ctl Fusion21so_ctl COM4 1`<br/>
**Slider only**<br/>
`run expFusion HCPS1XX_slider_ctl Fusion21so_ctl COM4 0`<br/>
**Fusion**<br/>
`run expFusion HCPS1XX_fusion_emg25 Fusion21so COM4 0.25`<br/>
`run expFusion HCPS1XX_fusion_emg50 Fusion21so COM4 0.5`<br/>
`run expFusion HCPS1XX_fusion_emg75 Fusion21so COM4 0.75`<br/>
**EMG only 2**<br/>
`run expFusion HCPS1XX_emg_ctl2 Fusion21so_ctl2 COM4 1`<br/>
**Slider only 2**<br/>
`run expFusion HCPS1XX_slider_ctl2 Fusion21so_ctl2 COM4 0`<br/>

# DATA ANALYSIS
See README in the fusion analysis folder.

# DEVELOPMENT NOTES 

-- UPDATED 2021/7/1 Amber Chou
(Note: comment out lines su18CP in __init__.py)

-  run experiment with sliderino
In [1]: run experiment subject protocol port 
for example: run experimentPython3 subject0 su19fo COM3

-  run experiment with SpikerShields EMG
run experimentPython3 subject0 su19fo COM3

-- UPDATED 2021/7/12 Amber Chou
*** EMG calibration code adapted from expCHI.py
*** python-Arduno communication code adapted from https://thepoorengineer.com/en/arduino-python-plot/#combine

Updated these files to run the SpikerShields EMG via Arduino Uno:
1. sliderPython3.py (original code in the same file for reference) 
2. experimentPython3.py (changes from line 231-245 for the rescale_inp)
3. silderino.ino code saved in sliderino_EMG_only (original code saved in sliderino_original for reference)

Note that these code also works for slider via Arduino Uno, with changes in all three files: 
1. sliderPython3.py line 53; 
2. experimentPython3.py line 235; 
3. silderino code saved in sliderino_slider_only

-- UPDATED 2021/7/22 Amber Chou, sensori-fusion code

Process:
1. change sliderPython3.py line 20 & 22 (COM and where to save EMGcalibration.txt)
2. run sliderPython3.py and do the calibration
3. run pygame

Note: if would like to check EMG value, can uncommon line 113 (scaled data) or line 93 (raw data), and run sliderPython3.py for data collection process.


-- UPDATED 2021/7/29 Amber Chou, save raw EMG data in seperate csv file
made new funciton saveEMGData to save raw "EMG1 (bicep), EMG2 (tricep), adn slider" data
(ignore these updates!)

-- UPDATED 2021/7/30 Amber Chou, made two threads (1. EMG raw data collection, 2. Pygame)
Note: EMG raw data collection updates 2000Hz. Since the Arduino sends data with 115200 buatrate (too fast, game lags).

-- UPDATED 2021/8/2 Amber Chou,
1. revised sliderino, make EMG data unfiltered (raw)
2. revised silderPython3.py, filter raw EMG data (detrending)
pip install scipy

-- UPDATED 2021/8/10 Amber Chou,
1. removed the detrend code, do demean + rectification + moving average (500 data point window) in a new thread. Added time resolution to ms when saving raw EMG data in csv file. 
2. issues: 
- MA window = 500, for sampling rate of 9600Hz, it should be 960 data for 100 ms...
- MA window sliding rate?
- increase the threshold to 0.1 (10%), it was 2.5%

-- UPDATED 2021/8/11 Amber Chou,
- fixed: in expPython3.py, lin 572, if TRIAL_STATE == 'reset2':if (np.abs(out_[-FPS*SLIDER_SPT:]).max() < RAD_SYS*5): makes RAD_SY times 5 --> decreases the game starting time
- change threshold back to 2.5%
- change MA window = 960, for sampling rate of 9600Hz, this is 100 ms window.

-- UPDATED 2021/8/19 Amber Chou,
- pilot data collection: (1) slider only (5 trials), (2) EMG only (6 trials), (3) slider + EMG equal weighting (5 trials)

-- UPDATED 2021/8/24 Amber Chou,
- update expPython3.py, save slider input and EMG input seperately in pygame data (joy.grabdata())
- all previous data saved in Google Drive
- fix Mac DS_store (https://stackoverflow.com/questions/107701/how-can-i-remove-ds-store-files-from-a-git-repository)

-- UPDATED 2021/8/30 Amber Chou,
1. Fix issues in expPython3.py, save slider input and EMG input seperately in pygame data (Threeinp = joy.grabdata())
2. Fix scaling for slider and EMG input to match percent screen (-50%~+50%)
3. rename expPython3.py as expFusion.py, rename sliderPython3.py as ArduinoPython.py

-- 2021/11/13 Pilot data collection with Version 4.2.3 (old scaling). tested on Amber.

-- UPDATED 2021/11/24 Amber Chou,
Fix issues (sensrofusion_v4.2.4):
1. Generate d in input space by making the amplitudes of disturbance be Md/M
2. Fix randomness issue, now the consecutive trials all have different phases
3. Generate all 30 trials then fix the scaling issues (scaleOutput = 0.8120629258740933; scaleOutputScreen = 1/4; scaleInput = 0.04616974606700115) where Output screen is -0.66~0.66 out of -2~+2 and Input slider is -0.165~0.165 out of -0.5~+0.5
4. new Protocol Fusion21so.py
5. (deleted) fixed cues at the begining of the game, make the input before starting trials always 100% slider. 
HOW to run:
run expFusion [subject] Fusion21so COM4 0

-- 2021/12/02 Pilot data collection with Version 4.2.4. tested on Momona.
-- 2021/12/02 Test data collection with Version 4.2.4 with Coban and without Coban. tested on Amber.

-- UPDATED 2021/12/3 Amber Chou,
1. print last trial's MSE after game finishes.
2. create new protocol files: Fusion21so.py, Fusion21so_ctl.py, Fusion21so_ctl2.py
3. change look ahead time from 0.5 sec to 2 sec

-- 2021/12/06 Pilot data collection with Version 4.2.5. tested on Momona.

-- UPDATED 2021/12/7 Amber Chou,
change EMG scales by *2, make EMG measurement more sensitive.

-- 2021/12/7 Pilot data collection with Version 4.2.5 (with new EMG scaling). tested on Amber.


