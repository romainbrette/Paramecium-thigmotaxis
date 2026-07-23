'''
Swimming speed in culture medium, at t = 1 hour
'''
import os
from trajectories.magic_loading import *
from interface import *
import matplotlib.pyplot as plt
from figures.figures import *

filename = os.path.join(data_path, 'Dynamics/Log cells in culture medium/tracking_linked_with_features_20.0_fps_1_um.tsv')
output_fig = os.path.expanduser('~/Downloads/fig1_speed.pdf')

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
ax.hist(selection['speed']/dt, bins=100, color='k')

ax.set_xlim(0, 1250)
ax.set_xlabel('Speed ($\mu$m/s)')

plt.tight_layout()
plt.savefig(output_fig)
plt.show()
