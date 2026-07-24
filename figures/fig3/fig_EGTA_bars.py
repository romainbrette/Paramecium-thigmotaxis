'''
Maximum attachment in culture medium with varying EGTA concentration.
'''
from figures.figures import *
import os
import pandas as pd

filename_control = os.path.join(data_path, 'Dynamics/Log cells in culture medium plus EGTA/0.4 mM EGTA vs control/count2.tsv')
filename_037_EGTA = os.path.join(data_path, 'Dynamics/Log cells in culture medium plus EGTA/0.38 mM vs. 0.37 mM vs. 0.32 mM EGTA/count2.tsv')
filename_032_EGTA = os.path.join(data_path, 'Dynamics/Log cells in culture medium plus EGTA/0.38 mM vs. 0.37 mM vs. 0.32 mM EGTA/count.tsv')

output_fig = os.path.expanduser('~/Downloads/fig_bars_EGTA.pdf')

figsize = (2, 2)

# 5 min rolling average
dt_Petri = 200/20.
window_size = int(300/dt_Petri)+1 # 5 min

# Read data
control = pd.read_csv(filename_control, sep='\t')
EGTA_032 = pd.read_csv(filename_032_EGTA, sep='\t')
EGTA_037 = pd.read_csv(filename_037_EGTA, sep='\t')

EGTA_037['attached'] = EGTA_037['attached'].rolling(window=window_size, center=True).mean()
EGTA_037['swimming'] = EGTA_037['swimming'].rolling(window=window_size, center=True).mean()

control['attached'] = control['attached'].rolling(window=window_size, center=True).mean()
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

print(max_attachment(EGTA_037))
bars_proportions_with_p(ax, ('EGTA', *max_attachment(EGTA_037)),
                            ('control', *max_attachment(control))
                            )

ax.set_xlabel(' ')
ax.set_ylabel('Immobile cells (%)')
ax.set_ylim(0, 110)

plt.tight_layout()
plt.savefig(output_fig)
plt.show()
