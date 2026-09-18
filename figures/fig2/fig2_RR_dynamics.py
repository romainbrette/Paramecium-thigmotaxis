'''
Proportion of attached cells vs. time in control vs. 10 uM RR
'''
from figures.figures import *
import os
import pandas as pd

filename_RR = os.path.join(data_path, 'Dynamics/Log cells in culture medium plus RR/count2.tsv')
filename_control = os.path.join(data_path, 'Dynamics/Log cells in culture medium plus RR/count.tsv')
output_fig = os.path.expanduser('~/Downloads/fig2_RR_2h.pdf')

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
