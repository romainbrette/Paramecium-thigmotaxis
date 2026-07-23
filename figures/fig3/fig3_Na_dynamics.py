'''
Proportion of attached cells vs. time in 411 vs. 411 + Na+ on glass
'''
from figures.figures import *
import os
import pandas as pd

filename_Na = '/Volumes/DDRomain/Paramecium/Thigmotaxis/DATA/02___0.5x___with_tracking/06_Na/01_LOG_2h___Left_411_plus_11.5mM_Na_Right_411___950_cell_ml___520um_spacer_coverslip/tracking/count2.tsv'
filename_control = '/Volumes/DDRomain/Paramecium/Thigmotaxis/DATA/02___0.5x___with_tracking/06_Na/01_LOG_2h___Left_411_plus_11.5mM_Na_Right_411___950_cell_ml___520um_spacer_coverslip/tracking/count.tsv'
output_fig = os.path.expanduser('~/Downloads/fig3_Na_2h.pdf')

figsize = (2, 2)

# Read data
data_Na = pd.read_csv(filename_Na, sep='\t')
data_Na['n'] = data_Na['attached'] + data_Na['swimming']
data_Na['attached_p'] = data_Na['attached']/data_Na['n']
data_control = pd.read_csv(filename_control, sep='\t')
data_control['n'] = data_control['attached'] + data_control['swimming']
data_control['attached_p'] = data_control['attached']/data_control['n']

print('Na+, n =', data_Na['n'].median())
print('Control, n =', data_control['n'].median())

# Plot
fig, ax = plt.subplots(figsize=figsize)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)

window_size = 30+1 # times 10 s = 5 min
ax.plot(data_control['t']/3600., 100*data_control['attached_p'].rolling(window=window_size, center=True).mean(), 'k')
ax.plot(data_Na['t']/3600., 100*data_Na['attached_p'].rolling(window=window_size, center=True).mean(), color='#1b9e77')

ax.set_xlabel('Time (h)')
ax.set_ylabel('Immobile cells (%)')
ax.set_ylim(0, 100)
ax.set_xticks([0, 1, 2])

plt.tight_layout()
plt.savefig(output_fig)
plt.show()
