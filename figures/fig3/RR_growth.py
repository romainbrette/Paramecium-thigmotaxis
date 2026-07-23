'''
Measure cell growth in 10 uM RR vs. control
'''
from figures.figures import *

filename_RR = '/Volumes/DDRomain/Paramecium/Thigmotaxis/DATA/02___0.5x___with_tracking/05_Ca/02_LOG_Ruthenium_Red___L_Control__R_ruthenium_red_10uM___Petri_cap/Tracking/count2.tsv'
filename_control = '/Volumes/DDRomain/Paramecium/Thigmotaxis/DATA/02___0.5x___with_tracking/05_Ca/02_LOG_Ruthenium_Red___L_Control__R_ruthenium_red_10uM___Petri_cap/Tracking/count.tsv'

# Read data
data_RR = pd.read_csv(filename_RR, sep='\t')
data_RR['n'] = data_RR['attached'] + data_RR['swimming']
data_control = pd.read_csv(filename_control, sep='\t')
data_control['n'] = data_control['attached'] + data_control['swimming']

# Initial number of cells
print("Growth in RR:", 100*data_RR[data_RR['t']>60*170]['n'].median() / data_RR[data_RR['t']<60*10.]['n'].median(), "%")
print("Growth in control:", 100*data_control[data_control['t']>60*170]['n'].median() / data_control[data_control['t']<60*10.]['n'].median(), "%")

