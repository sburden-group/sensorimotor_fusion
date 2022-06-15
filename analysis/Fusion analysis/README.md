# DATA ANALYSIS

# SETUP:
- run **Store_HCPS_data.ipynb** (store HCPS.pkl), make sure to update the "path" first
- run **Data_analysis.ipynb**(store DATA.pkl)
- run **Numerical_simulations.ipynb** (store SIM.pkl) , simulated y,y0,y1
- run **Transfer_functions.ipynb** (store TF.pkl, incluing F,B,TUR,TUD,TYR,TYD ... and find crossover frequency)
- run **Power_spectrum_density.ipynb** (store AvgDelta.pkl)

# PLOTS:
example plots: **example_plot.ipynb**, move these plotting files to the same folder as the data files (.pkl) first <br/>

CPHS conference paper figures: **CPHS_plots.ipynb** <br/>

Qual exam figures: **Qual_plots.ipynb**<br/>


# ANALYSIS:
## Plotting (for all participants): <br/>
- run **Sensorfusion_analysis_plots.ipynb** --> (update in Hypothesis 1)<br/>

## Bayesian integration: <br/>
- run **Bayesian_model.ipynb** (need to update)<br/>

## LQG framwork:<br/>
- run **LQG.ipynb** (store LQG_SIM.pkl, includes LQG_SIM_EO & LQG_SIM_OE, with simulated state x, input u (1-dim), and cursor output y in time domain, xyu are after scaling)<br/>
- run **LQG_extend.ipynb** (with 2-channel inputs)<br/>

## sensorimotor noises:
- run **Power_spectrum_density.ipynb** (store AvgDelta.pkl, includes avgdelta_mag (mean of magnitide of delta (freq domain) for each participant and each condition) &  avgdelta_time (time domain noise (from slider-only and emg-only) for each participant and each condition) )

## comparing conditions:

compare u_emg & u_slider:  
- run **Compare_u0_u1.ipynb** --> (the old Hypoethesis 2: people use EMG for high freq and slider for low freq)

evaluate the performance of 1-modality vs 2-modality:
- run **Compare_conditions.ipynb** --> (the old Hypoethesis 1: people do "better" with 2 modalities)

other examples:
- run **Phase_mean_calculation.ipynb**

