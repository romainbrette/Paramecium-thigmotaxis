'''
Maximum attachment in log. vs. stationary, glass vs. Petri.
'''
from figures.figures import *
import os
import pandas as pd

filename_log_glass = '/Volumes/DDRomain/Paramecium/Thigmotaxis/DATA/02___0.5x___with_tracking/04_411/01_LOG_STAT_2h/01_LOG_2h___411___800_cell_ml___20ul_drop___520um_coverslips/background_removed/tracking/count.tsv'
filename_stat_glass = '/Volumes/DDRomain/Paramecium/Thigmotaxis/DATA/02___0.5x___with_tracking/04_411/01_LOG_STAT_2h/02_STAT_2h___411___6900_cell_ml___25ul_drop___520um_coverslip/background_removed/tracking/count.tsv'
filename_log_Petri = '/Volumes/DDRomain/Paramecium/Thigmotaxis/DATA/02___0.5x___with_tracking/03_phase/01_LOG_STAT_same_culture/01_LOG___411___1000_cell_ml___Petri_cap/tracking/count.tsv'
filename_stat_Petri = '/Volumes/DDRomain/Paramecium/Thigmotaxis/DATA/02___0.5x___with_tracking/03_phase/01_LOG_STAT_same_culture/02_STAT___411___4700_cell_ml___Petri_cap/tracking/count.tsv'

output_fig = os.path.expanduser('~/Downloads/fig2_bars.pdf')

figsize = (2, 2)

# Read data
log_glass = pd.read_csv(filename_log_glass, sep='\t')
stat_glass = pd.read_csv(filename_stat_glass, sep='\t')
log_Petri = pd.read_csv(filename_log_Petri, sep='\t')
stat_Petri = pd.read_csv(filename_stat_Petri, sep='\t')

# 5 min rolling average
dt_Petri = 300/22.
window_size_Petri = int(300/dt_Petri)+1 # 5 min
window_size_glass = 30+1 # times 10 s = 5 min

log_glass['attached'] = log_glass['attached'].rolling(window=window_size_glass, center=True).mean()
stat_glass['attached'] = stat_glass['attached'].rolling(window=window_size_glass, center=True).mean()
log_Petri['attached'] = log_Petri['attached'].rolling(window=window_size_Petri, center=True).mean()
stat_Petri['attached'] = stat_Petri['attached'].rolling(window=window_size_Petri, center=True).mean()

log_glass['swimming'] = log_glass['swimming'].rolling(window=window_size_glass, center=True).mean()
stat_glass['swimming'] = stat_glass['swimming'].rolling(window=window_size_glass, center=True).mean()
log_Petri['swimming'] = log_Petri['swimming'].rolling(window=window_size_Petri, center=True).mean()
stat_Petri['swimming'] = stat_Petri['swimming'].rolling(window=window_size_Petri, center=True).mean()

# Maximum proportion of attached cells
def max_attachment(data):
    # Maybe average first?
    data['n'] = data['attached'] + data['swimming']
    data['attached_p'] = data['attached']/data['n']
    imax_control = data['attached_p'].idxmax()
    max_control = data.loc[imax_control, 'attached_p']
    n_control = data.loc[imax_control, 'n']
    return max_control, n_control

# Plot
fig, ax = plt.subplots(figsize=figsize)

bars_proportions(ax, ('log', *max_attachment(log_glass)),
                            ('stat', *max_attachment(stat_glass)),
                            (' log ', *max_attachment(log_Petri)),
                            (' stat ', *max_attachment(stat_Petri))
                            )

ax.set_xlabel(' ')
ax.set_ylabel('Immobile cells (%)')
ax.set_ylim(0, 110)

plt.tight_layout()
plt.savefig(output_fig)
plt.show()
