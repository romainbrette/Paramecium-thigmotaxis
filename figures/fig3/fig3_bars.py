'''
Maximum attachment in log. vs. stationary, glass vs. Petri.
Compared with bacterized and filtered medium.
'''
from figures.figures import *
import os
import pandas as pd

filename_log_glass = os.path.join(data_path, 'Dynamics/Ca-K solution - glass - log/count.tsv')
filename_log_glass2 = os.path.join(data_path, 'Dynamics/Log cells in Ca-K-Na solution/count.tsv') # control of the Na+ experiment
filename_stat_glass = os.path.join(data_path, 'Dynamics/Ca-K solution - glass - stationary/count.tsv')
filename_log_Petri = os.path.join(data_path, 'Dynamics/Ca-K solution - Petri dish - log/count.tsv')
filename_log_Petri2 = os.path.join(data_path, 'Dynamics/Ca-K solution - Petri dish - log/count-replicate.tsv')
filename_stat_Petri = os.path.join(data_path, 'Dynamics/Ca-K solution - Petri dish - stationary/count.tsv')
filename_stat_Petri2 = os.path.join(data_path, 'Dynamics/Ca-K solution - Petri dish - stationary/count-replicate.tsv')

filename_filtered = os.path.join(data_path, 'Dynamics/Log cells in filtered medium/count.tsv') # on Petri dish  ## pb with these data!
filename_culture = os.path.join(data_path, 'Dynamics/Log cells in culture medium/count.tsv')
filename_culture_Petri = os.path.join(data_path, 'Dynamics/Log cells in culture medium plus RR/count.tsv')
filename_culture_Petri2 = os.path.join(data_path, 'Dynamics/Log cells in culture medium plus EGTA/0.4 mM EGTA vs control/count2.tsv')

output_fig = os.path.expanduser('~/Downloads/fig3_bars.pdf')

figsize = (2, 2)

# Read data
log_glass = pd.read_csv(filename_log_glass, sep='\t')
log_glass2 = pd.read_csv(filename_log_glass2, sep='\t')
stat_glass = pd.read_csv(filename_stat_glass, sep='\t')
log_Petri = pd.read_csv(filename_log_Petri, sep='\t')
log_Petri2 = pd.read_csv(filename_log_Petri2, sep='\t')
stat_Petri = pd.read_csv(filename_stat_Petri, sep='\t')
stat_Petri2 = pd.read_csv(filename_stat_Petri2, sep='\t')
filtered = pd.read_csv(filename_filtered, sep='\t')
culture = pd.read_csv(filename_culture, sep='\t')
culture_Petri = pd.read_csv(filename_culture_Petri, sep='\t')
culture_Petri2 = pd.read_csv(filename_culture_Petri2, sep='\t')

# 5 min rolling average
dt_Petri = 300/22.
window_size_Petri = int(300/dt_Petri)+1 # 5 min
window_size_glass = 30+1 # times 10 s = 5 min

for var in ('attached', 'swimming'):
    log_glass[var] = log_glass[var].rolling(window=window_size_glass, center=True).mean()
    log_glass2[var] = log_glass2[var].rolling(window=window_size_glass, center=True).mean()
    stat_glass[var] = stat_glass[var].rolling(window=window_size_glass, center=True).mean()
    log_Petri[var] = log_Petri[var].rolling(window=window_size_Petri, center=True).mean()
    log_Petri2[var] = log_Petri2[var].rolling(window=window_size_Petri, center=True).mean()
    stat_Petri[var] = stat_Petri[var].rolling(window=window_size_Petri, center=True).mean()
    stat_Petri2[var] = stat_Petri2[var].rolling(window=window_size_Petri, center=True).mean()
    filtered[var] = filtered[var].rolling(window=window_size_Petri, center=True).mean()
    culture[var] = culture[var].rolling(window=window_size_Petri, center=True).mean()
    culture_Petri[var] = culture_Petri[var].rolling(window=window_size_Petri, center=True).mean()
    culture_Petri2[var] = culture_Petri2[var].rolling(window=window_size_Petri, center=True).mean()

# Maximum proportion of attached cells
def max_attachment(data):
    data = data[(data['t']>0*60) & (data['t']<60*60)]
    data['n'] = data['attached'] + data['swimming']
    data['attached_p'] = data['attached']/data['n']
    imax_control = data['attached_p'].idxmax()
    max_control = data.loc[imax_control, 'attached_p']
    n_control = data.loc[imax_control, 'n']
    return max_control, n_control
    #return data['attached_p'].mean(), data['n'].mean()

# Plot
fig, ax = plt.subplots(figsize=figsize)

bars_proportions(ax, (1, *max_attachment(log_glass)),
                     (2, *max_attachment(log_glass2)),
                     (3, *max_attachment(stat_glass)),
                     (4, *max_attachment(log_Petri)),
                     (5, *max_attachment(log_Petri2)),
                     (6, *max_attachment(stat_Petri)),
                     (7, *max_attachment(stat_Petri2)),
                     (8, *max_attachment(filtered)),
                     (9, *max_attachment(culture)),
                     (10, *max_attachment(culture_Petri)),
                     (11, *max_attachment(culture_Petri2)),
                     )

ax.set_xlabel(' ')
ax.set_ylabel('Immobile cells (%)')
ax.set_ylim(0, 110)

plt.tight_layout()
plt.savefig(output_fig)
plt.show()
