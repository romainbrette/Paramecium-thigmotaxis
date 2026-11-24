'''
Proportion of attached cells vs. time in culture medium.
'''
from figures.figures import *
import os
import pandas as pd

filename1 = os.path.join(data_path, 'Dynamics/Log cells in culture medium/count.tsv')
filename2 = os.path.join(data_path, 'Dynamics/Log cells in culture medium plus RR/count.tsv')
filename3 = os.path.join(data_path, 'Dynamics/Log cells in culture medium plus EGTA/0.4 mM EGTA vs control/count2.tsv')

output_fig = os.path.expanduser('~/Downloads/fig1_culture_medium.pdf')

figsize = (2, 2)

# Plot
fig, ax = plt.subplots(figsize=figsize)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)

for filename in (filename1, filename2, filename3):
    # Read data
    data = pd.read_csv(filename, sep='\t')
    data = data[data['t']<3600] # first hour
    data['n'] = data['attached'] + data['swimming']
    data['attached_p'] = data['attached']/data['n']

    window_size = 21 # times 15 s
    ax.plot(data['t']/60., 100*data['attached_p'].rolling(window=window_size, center=True).mean(), 'k')

ax.set_xlabel('Time (min)')
ax.set_ylabel('Immobile cells (%)')
ax.set_ylim(0, 100)
ax.set_xticks([0, 30, 60])

plt.tight_layout()
plt.savefig(output_fig)
plt.show()
