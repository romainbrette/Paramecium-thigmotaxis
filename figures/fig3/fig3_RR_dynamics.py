'''
Proportion of attached cells vs. time in control vs. 10 uM RR
'''
from figures.figures import *
import os
import pandas as pd

filename_RR = '/Volumes/DDRomain/Paramecium/Thigmotaxis/DATA/02___0.5x___with_tracking/05_Ca/02_LOG_Ruthenium_Red___L_Control__R_ruthenium_red_10uM___Petri_cap/Tracking/count2.tsv'
filename_control = '/Volumes/DDRomain/Paramecium/Thigmotaxis/DATA/02___0.5x___with_tracking/05_Ca/02_LOG_Ruthenium_Red___L_Control__R_ruthenium_red_10uM___Petri_cap/Tracking/count.tsv'
output_fig = os.path.expanduser('~/Downloads/fig3_RR_2h.pdf')

figsize = (2, 2)

# Read data
data_RR = pd.read_csv(filename_RR, sep='\t')
data_RR['n'] = data_RR['attached'] + data_RR['swimming']
data_RR['attached_p'] = data_RR['attached']/data_RR['n']
data_control = pd.read_csv(filename_control, sep='\t')
data_control['n'] = data_control['attached'] + data_control['swimming']
data_control['attached_p'] = data_control['attached']/data_control['n']

print('Na+, n =', data_RR['n'].median())
print('Control, n =', data_control['n'].median())

# Plot
fig, ax = plt.subplots(figsize=figsize)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)

window_size = 30+1 # times 10 s = 5 min
ax.plot(data_control['t']/3600., 100*data_control['attached_p'].rolling(window=window_size, center=True).mean(), 'k')
ax.plot(data_RR['t']/3600., 100*data_RR['attached_p'].rolling(window=window_size, center=True).mean(), color='#1b9e77')

ax.set_xlabel('Time (h)')
ax.set_ylabel('Immobile cells (%)')
ax.set_ylim(0, 100)
ax.set_xticks([0, 1, 2, 3])

plt.tight_layout()
plt.savefig(output_fig)
plt.show()
