'''
Speed distribution with RR vs. control.
'''
import os
from trajectories.magic_loading import *
from interface import *
import matplotlib.pyplot as plt
from figures.figures import *

filename_control = os.path.join(data_path, 'Dynamics/Log cells in culture medium plus RR/tracking_linked_with_features_20.0_fps_1_um_control.tsv')
filename_RR = os.path.join(data_path, 'Dynamics/Log cells in culture medium plus RR/tracking_linked_with_features_20.0_fps_1_um_RR.tsv')
output_fig = os.path.expanduser('~/Downloads/fig2_RR_speed.pdf')

figsize = (2, 2)

# Read data
data_control = magic_load_trajectories(filename_control) # could be a simple read_csv
data_RR = magic_load_trajectories(filename_RR) # could be a simple read_csv
fps, _ = guess_fps_and_pixelsize(filename_control)
print('FPS =', fps, 'Hz')
dt = 1/fps

# Plot
fig, ax = plt.subplots(figsize=figsize)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.spines["left"].set_visible(False)
ax.yaxis.set_visible(False)

# common bin edges covering all three datasets
# bins = np.linspace(min(d.min() for d in data),
#                    max(d.max() for d in data), 101)

for data, color in ((data_control, 'k'), (data_RR, 'r')):
    selection = data[(data['frame']*dt>60*60) & (data['frame']*dt<65*60)]
    ax.hist(data['speed']/dt, color=color, histtype='step', lw=1.5, density=True)

ax.set_xlim(0, 1250)
ax.set_xlabel('Speed ($\mu$m/s)')

plt.tight_layout()
plt.savefig(output_fig)
plt.show()
