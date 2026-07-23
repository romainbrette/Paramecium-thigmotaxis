'''
Maximum attachment in Na+ vs. control (411), glass.
'''
from figures.figures import *
import os
import pandas as pd

filename_Na = '/Volumes/DDRomain/Paramecium/Thigmotaxis/DATA/02___0.5x___with_tracking/06_Na/01_LOG_2h___Left_411_plus_11.5mM_Na_Right_411___950_cell_ml___520um_spacer_coverslip/tracking/count2.tsv'
filename_control = '/Volumes/DDRomain/Paramecium/Thigmotaxis/DATA/02___0.5x___with_tracking/06_Na/01_LOG_2h___Left_411_plus_11.5mM_Na_Right_411___950_cell_ml___520um_spacer_coverslip/tracking/count.tsv'

output_fig = os.path.expanduser('~/Downloads/fig3_bars_Na.pdf')

figsize = (2, 2)

# Read data
Na = pd.read_csv(filename_Na, sep='\t')
control = pd.read_csv(filename_control, sep='\t')

# 5 min rolling average
dt_Petri = 300/20.
window_size = int(300/dt_Petri)+1 # 5 min

Na['attached'] = Na['attached'].rolling(window=window_size, center=True).mean()
Na['attached'] = Na['attached'].rolling(window=window_size, center=True).mean()

control['swimming'] = control['swimming'].rolling(window=window_size, center=True).mean()
control['swimming'] = control['swimming'].rolling(window=window_size, center=True).mean()

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

bars_proportions_with_p(ax, ('Na', *max_attachment(Na)),
                            ('control', *max_attachment(control))
                            )

ax.set_xlabel(' ')
ax.set_ylabel('Immobile cells (%)')
ax.set_ylim(0, 110)

plt.tight_layout()
plt.savefig(output_fig)
plt.show()
