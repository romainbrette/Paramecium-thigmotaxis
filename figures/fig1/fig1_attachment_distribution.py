'''
Distribution of attachment duration in log cells in culture medium.
'''
import os
from trajectories.magic_loading import *
from trajectories.linking import *
from figures.figures import *
import numpy as np
from scipy.stats import linregress

filename = os.path.join(data_path, 'Dynamics/Log cells in culture medium/background/tracking_linked_20.0_fps_1_um.tsv')
output_fig = os.path.expanduser('~/Downloads/fig1_attachment_duration.pdf')

figsize = (3, 2)

# Read data
data = magic_load_trajectories(filename) # could be a simple read_csv
dt = 15. # s

# Track still cells
del data['id']
attached_tracks = trackpy_track(data, search_range=50, memory=5)

trajectories = trajectories_from_table(attached_tracks)
durations = np.array([traj['frame'].max() + 1 - traj['frame'].min()
                      for traj in tqdm(trajectories) if len(traj) > 2])*dt/60

# ax.set_xscale('log')
# xlim(0, 300)
print(np.mean(durations)*60, np.std(durations)*60)

# Plot
fig, ax = plt.subplots(figsize=figsize)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)

#ax.hist(durations[durations<10.], bins=10, log=False, color='k')
#ax.set_xlim(0, 10)

## In log scale
#ax.hist(durations[durations<10.], bins=30, log=True, color='k')
data = durations[durations < 10.]
counts, edges = np.histogram(data, bins=30)
centers = 0.5 * (edges[:-1] + edges[1:])
mask = counts > 0
res = linregress(centers[mask], np.log(counts[mask])) # linear regression in log scale

ax.hist(data, bins=edges, log=True, color='k')
x = np.linspace(centers[mask].min(), centers[mask].max(), 200)
ax.plot(x, np.exp(res.intercept + res.slope * x), 'k--')
print("Characteristic decay:", -1/res.slope, "min")

ax.set_xlabel('Duration (min)')
ax.set_ylabel('Frequency (a.u.)')

plt.tight_layout()
plt.savefig(output_fig)
plt.show()
