'''
Proportion of attached cells vs. time in 411 on Petri dish, stat. vs. log.
'''
from figures.figures import *
import os
import pandas as pd

filename_log = os.path.join(data_path, 'Dynamics/Ca-K solution - Petri dish - log/count.tsv')
filename_stat = os.path.join(data_path, 'Dynamics/Ca-K solution - Petri dish - stationary/count.tsv')
output_fig = os.path.expanduser('~/Downloads/fig2_411_Petri.pdf')

figsize = (3, 2)

# Read data
data_log = pd.read_csv(filename_log, sep='\t')
data_log['n'] = data_log['attached'] + data_log['swimming']
data_log['attached_p'] = data_log['attached']/data_log['n']
data_stat = pd.read_csv(filename_stat, sep='\t')
data_stat['n'] = data_stat['attached'] + data_stat['swimming']
data_stat['attached_p'] = data_stat['attached']/data_stat['n']

print('Log, n =', data_log['n'].median())
print('Stat, n =', data_stat['n'].median())

# Plot
fig, ax = plt.subplots(figsize=figsize)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)

dt = 300/22.
window_size = int(300/dt)+1 # 5 min
ax.plot(data_stat['t']/3600., 100*data_stat['attached_p'].rolling(window=window_size, center=True).mean(), 'k')
ax.plot(data_log['t']/3600., 100*data_log['attached_p'].rolling(window=window_size, center=True).mean(), color='#1b9e77')

ax.set_xlabel('Time (h)')
ax.set_ylabel('Immobile cells (%)')
ax.set_ylim(0, 100)
ax.set_xlim(0, 9)
#ax.set_xticks([0, 60, 120])

plt.tight_layout()
plt.savefig(output_fig)
plt.show()
