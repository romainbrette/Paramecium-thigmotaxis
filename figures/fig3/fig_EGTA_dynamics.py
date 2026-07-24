'''
Number swimming cells vs. time in EGTA (relative to t=0)

We could add 0.038 mM EGTA.
'''
from figures.figures import *
import os
import pandas as pd

filename_control = os.path.join(data_path, 'Dynamics/Log cells in culture medium plus EGTA/0.4 mM EGTA vs control/count2.tsv')
filename_032_EGTA = os.path.join(data_path, 'Dynamics/Log cells in culture medium plus EGTA/0.38 mM vs. 0.37 mM vs. 0.32 mM EGTA/count2.tsv')
filename_037_EGTA = os.path.join(data_path, 'Dynamics/Log cells in culture medium plus EGTA/0.38 mM vs. 0.37 mM vs. 0.32 mM EGTA/count.tsv')
output_fig = os.path.expanduser('~/Downloads/fig_EGTA_dynamics.pdf')

figsize = (3, 2)

# Read data
control = pd.read_csv(filename_control, sep='\t')
EGTA_032 = pd.read_csv(filename_032_EGTA, sep='\t')
EGTA_037 = pd.read_csv(filename_037_EGTA, sep='\t')

# Initial number of swimming cells (first minute)
n_control = control[control['t']<60.]['swimming'].mean()
n_032 = EGTA_032[EGTA_032['t']<60.]['swimming'].mean()
n_037 = EGTA_037[EGTA_037['t']<60.]['swimming'].mean()
print('n_control =', n_control)
print('n_032 = ', n_032)
print('n_037 = ', n_037)

# Plot
fig, ax = plt.subplots(figsize=figsize)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)

window_size = 60+1 # times 5 s = 5 min
ax.plot(control['t']/60, 100*control['swimming'].rolling(window=window_size, center=True).mean()/n_control, 'k')
ax.plot(EGTA_032['t']/60, 100*EGTA_032['swimming'].rolling(window=window_size, center=True).mean()/n_032, color='#1b9e77')
ax.plot(EGTA_037['t']/60, 100*EGTA_037['swimming'].rolling(window=window_size, center=True).mean()/n_037, color='#d95f02')

ax.set_xlabel('Time (min)')
ax.set_xticks([0, 30, 60])
ax.set_ylabel('Swimming cells (%)')
ax.set_xlim(0, 60)
ax.set_ylim(0, 110)
ax.set_xticks([0, 30, 60])

plt.tight_layout()
plt.savefig(output_fig)
plt.show()
