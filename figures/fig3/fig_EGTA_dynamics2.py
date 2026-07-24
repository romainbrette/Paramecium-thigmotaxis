'''
Proportion of attached cells vs. time in EGTA
'''
from figures.figures import *
import os
import pandas as pd

filename_control = os.path.join(data_path, 'Dynamics/Log cells in culture medium plus EGTA/0.4 mM EGTA vs control/count2.tsv')
filename_037_EGTA = os.path.join(data_path, 'Dynamics/Log cells in culture medium plus EGTA/0.38 mM vs. 0.37 mM vs. 0.32 mM EGTA/count2.tsv')
filename_032_EGTA = os.path.join(data_path, 'Dynamics/Log cells in culture medium plus EGTA/0.38 mM vs. 0.37 mM vs. 0.32 mM EGTA/count.tsv')
output_fig = os.path.expanduser('~/Downloads/fig_EGTA_dynamics2.pdf')

figsize = (2, 2)

# Read data
control = pd.read_csv(filename_control, sep='\t')
control['n'] = control['attached'] + control['swimming']
control['attached_p'] = control['attached']/control['n']

EGTA_032 = pd.read_csv(filename_032_EGTA, sep='\t')
EGTA_032['n'] = EGTA_032['attached'] + EGTA_032['swimming']
EGTA_032['attached_p'] = EGTA_032['attached']/EGTA_032['n']

EGTA_037 = pd.read_csv(filename_037_EGTA, sep='\t')
EGTA_037['n'] = EGTA_037['attached'] + EGTA_037['swimming']
EGTA_037['attached_p'] = EGTA_037['attached']/EGTA_037['n']

# Initial number of swimming cells (first minute)
# n_control = control[control['t']<60.]['swimming'].mean()
# n_032 = EGTA_032[EGTA_032['t']<60.]['swimming'].mean()
# n_037 = EGTA_037[EGTA_037['t']<60.]['swimming'].mean()
# print('n_control =', n_control)
# print('n_032 = ', n_032)
# print('n_037 = ', n_037)

# Plot
fig, ax = plt.subplots(figsize=figsize)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)

window_size = 30+1 # times 10 s = 5 min
ax.plot(control['t']/60., 100*control['attached_p'].rolling(window=window_size, center=True).mean(), 'k')
ax.plot(EGTA_032['t']/60., 100*EGTA_032['attached_p'].rolling(window=window_size, center=True).mean(), color='#1b9e77')
ax.plot(EGTA_037['t']/60., 100*EGTA_037['attached_p'].rolling(window=window_size, center=True).mean(), color='#d95f02')

ax.set_ylabel('Immobile cells (%)')
ax.set_ylim(0, 100)
ax.set_xlabel('Time (min)')
ax.set_xticks([0, 30, 60])
ax.set_xlim(0, 60)

plt.tight_layout()
plt.savefig(output_fig)
plt.show()
