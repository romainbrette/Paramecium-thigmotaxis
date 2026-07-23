'''
Measure cell growth in 10 uM RR vs. control
'''
from figures.figures import *
import pandas as pd
import os

filename_RR = os.path.join(data_path, 'Dynamics/Log cells in culture medium plus RR/count2.tsv')
filename_control = os.path.join(data_path, 'Dynamics/Log cells in culture medium plus RR/count.tsv')

# Read data
data_RR = pd.read_csv(filename_RR, sep='\t')
data_RR['n'] = data_RR['attached'] + data_RR['swimming']
data_control = pd.read_csv(filename_control, sep='\t')
data_control['n'] = data_control['attached'] + data_control['swimming']

# Initial number of cells
print("Growth in RR:", 100*data_RR[data_RR['t']>60*170]['n'].median() / data_RR[data_RR['t']<60*10.]['n'].median(), "%")
print("Growth in control:", 100*data_control[data_control['t']>60*170]['n'].median() / data_control[data_control['t']<60*10.]['n'].median(), "%")

