'''
Speed distribution with EGTA vs. control.
'''
import os
from trajectories.magic_loading import *
from interface import *
import matplotlib.pyplot as plt
from figures.figures import *

filename_control = os.path.join(data_path, 'Dynamics/Log cells in culture medium plus EGTA/0.4 mM EGTA vs control/tracking_linked_with_features_20.0_fps_1_um_control.tsv')
filename_RR = os.path.join(data_path, 'Dynamics/Log cells in culture medium plus RR/tracking_linked_with_features_20.0_fps_1_um_RR.tsv')
output_fig = os.path.expanduser('~/Downloads/fig2_RR_speed.pdf')

figsize = (1.5, 2)

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

for data, color in ((data_control, 'k'), (data_RR, '#1b9e77')):
    selection = data[(data['frame']*dt>60*60) & (data['frame']*dt<65*60)]
    speed = data['speed']/dt
    ax.hist(speed[speed<1200.], bins=100, color=color, histtype='step', lw=1.5, density=True)

#ax.set_xlim(0, 1250)
ax.set_xlabel('Speed ($\mu$m/s)')
ax.set_xticks([0, 500, 1000])

plt.tight_layout()
plt.savefig(output_fig)
plt.show()
