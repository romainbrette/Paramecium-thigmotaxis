'''
Number of attached trichless cells.
'''
from figures.figures import *
import os
import pandas as pd

filename = os.path.join(data_path, 'Dynamics/Trichless/count.tsv')

output_fig = os.path.expanduser('~/Downloads/fig_extra_trichless.pdf')

figsize = (2, 2)

# Plot
fig, ax = plt.subplots(figsize=figsize)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)

# Read data
data = pd.read_csv(filename, sep='\t')
data = data[data['t']<2*3600] # first two hours
n = data[data['t']<1*60]['swimming'].mean() # they all swim at the beginning
data['attached_p'] = 1-data['swimming']/n

data_1h = data[(data['t']>55*60) & (data['t']<60*60)]
prop = data_1h['attached_p'].mean()
sd = (prop*(1-prop)/n)**.5
print("Attachment at 1 h:", prop*100, "% +-", sd*100, "% (n =", n, ")")

window_size = 21 # times 15 s
ax.plot(data['t']/3600., 100*data['attached_p'].rolling(window=window_size, center=True).mean(), 'k')

ax.set_xlabel('Time (h)')
ax.set_ylabel('Immobile cells (%)')
ax.set_ylim(0, 100)
ax.set_xticks([0, 1, 2])

plt.tight_layout()
plt.savefig(output_fig)
plt.show()
