'''
Proportion of swimming cells in filtered vs. unfiltered medium.
'''
from figures.figures import *
import os
import pandas as pd

filename_filtered = '/Volumes/DDRomain/Paramecium/Thigmotaxis/DATA/02___0.5x___with_tracking/2025_10_14__Log_3h__picked_in_filtered_culture_medium_4h_post_seed/tracking/count.tsv'
filename_control = '/Volumes/DDRomain/Paramecium/Thigmotaxis/DATA/02___0.5x___with_tracking/2025_10_14__Log_3h__picked_in_filtered_culture_medium_4h_post_seed/tracking/count2.tsv'
output_fig = os.path.expanduser('~/Downloads/fig1_filtered_dynamics.pdf')

figsize = (3, 2)

# Read data
control = pd.read_csv(filename_control, sep='\t')
filtered = pd.read_csv(filename_filtered, sep='\t')

# Restrict to first two hours (for comparison; and because there is growth)
control = control[control['t']<2*3600]
filtered = filtered[filtered['t']<2*3600]

# Initial number of swimming cells (first minute)
n_control = control[control['t']<60.]['swimming'].mean()
n_filtered = filtered[filtered['t']<60.]['swimming'].mean()
print('n_control =', n_control)
print('n_filtered = ', n_filtered)

# Plot
fig, ax = plt.subplots(figsize=figsize)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)

window_size = 60+1 # times 5 s = 5 min
ax.plot(control['t']/60, 100*control['swimming'].rolling(window=window_size, center=True).mean()/n_control, 'k')
ax.plot(filtered['t']/60, 100*filtered['swimming'].rolling(window=window_size, center=True).mean()/n_filtered, color='#1b9e77')

ax.set_xlabel('Time (min)')
ax.set_xticks([0, 60, 120])
ax.set_ylabel('Swimming cells (%)')
ax.set_xlim(0, 120)
ax.set_ylim(0, 110)
ax.set_xticks([0, 60, 120])

plt.tight_layout()
plt.savefig(output_fig)
plt.show()
