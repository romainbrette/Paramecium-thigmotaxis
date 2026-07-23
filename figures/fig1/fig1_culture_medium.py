'''
Proportion of attached cells vs. time in culture medium.
'''
from figures.figures import *
import os
import pandas as pd

filename = '/Volumes/DDRomain/Paramecium/Thigmotaxis/DATA/02___0.5x___with_tracking/01_culture_medium/ON_GLASS_COVERSLIPS/01_LOG_2h___culture_medium___2000_cell_ml___glass_slide_520um/tracking/count.tsv'
output_fig = os.path.expanduser('~/Downloads/fig1_culture_medium.pdf')

figsize = (2, 2)

# Read data
data = pd.read_csv(filename, sep='\t')
data['n'] = data['attached'] + data['swimming']
data['attached_p'] = data['attached']/data['n']

# Plot
fig, ax = plt.subplots(figsize=figsize)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)

window_size = 21 # times 15 s
ax.plot(data['t']/60., 100*data['attached_p'].rolling(window=window_size, center=True).mean(), 'k')

ax.set_xlabel('Time (min)')
ax.set_ylabel('Immobile cells (%)')
ax.set_ylim(0, 100)
ax.set_xticks([0, 60, 120])

plt.tight_layout()
plt.savefig(output_fig)
plt.show()
