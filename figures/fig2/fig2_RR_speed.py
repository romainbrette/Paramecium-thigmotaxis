'''
Speed distribution with RR vs. control.
'''
import os
from trajectories.magic_loading import *
from interface import *
import matplotlib.pyplot as plt
from figures.figures import *

filename = os.path.join(data_path, 'Dynamics/Log cells in culture medium plus RR/tracking_linked_with_features_20.0_fps_1_um')
output_fig = os.path.expanduser('~/Downloads/fig2_RR_speed.pdf')

figsize = (2, 2)

# Read data
#data_count = pd.read_csv(filename_count, sep='\t')
data = magic_load_trajectories(filename) # could be a simple read_csv
fps, _ = guess_fps_and_pixelsize(filename)
print('FPS =', fps, 'Hz')
dt = 1/fps

# Plot
fig, ax = plt.subplots(figsize=figsize)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.spines["left"].set_visible(False)
ax.yaxis.set_visible(False)

selection = data[(data['frame']*dt>60*60) & (data['frame']*dt<65*60)]

sel_list = [selection0, selection3, selection, selection2, selection4]
labels = ['A', 'B', 'C', 'D', 'E']
#colors = ['k', 'tab:red', 'tab:blue', 'tab:green']
colors = plt.cm.viridis(np.linspace(0.05, 0.9, 5))
data = [s['speed'] / dt for s in sel_list]
# common bin edges covering all three datasets
bins = np.linspace(min(d.min() for d in data),
                   max(d.max() for d in data), 101)
for d, lab, c in zip(data, labels, colors):
    ax.hist(d, bins=bins, color=c, histtype='step', lw=1.5, density=True, label=lab)

ax.set_xlim(0, 1250)
ax.set_xlabel('Speed ($\mu$m/s)')

plt.tight_layout()
plt.savefig(output_fig)
plt.show()
