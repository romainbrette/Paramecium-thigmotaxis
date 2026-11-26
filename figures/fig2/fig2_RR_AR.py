'''
Avoiding reactions with RR vs. control.
'''
import os
from trajectories.magic_loading import *
from interface import *
import matplotlib.pyplot as plt
from figures.figures import *
from trajectories.trajectory_analysis import *

filename_control = os.path.join(data_path, 'Dynamics/Log cells in culture medium plus RR/tracking_linked_with_features_20.0_fps_1_um_control.tsv')
filename_RR = os.path.join(data_path, 'Dynamics/Log cells in culture medium plus RR/tracking_linked_with_features_20.0_fps_1_um_RR.tsv')
output_fig = os.path.expanduser('~/Downloads/fig2_RR_AR.pdf')

figsize = (2, 2)

# Read data
data_control = magic_load_trajectories(filename_control) # could be a simple read_csv
data_RR = magic_load_trajectories(filename_RR) # could be a simple read_csv
fps, _ = guess_fps_and_pixelsize(filename_control)
print('FPS =', fps, 'Hz')
dt = 1/fps

# Plot
fig, (ax_hist, ax) = plt.subplots(
    2, 1, sharex=True, figsize=figsize,
    gridspec_kw={'height_ratios': [1.5, 3], 'hspace': 0.1},
    layout='constrained'
)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)

ax_hist.spines['right'].set_visible(False)
ax_hist.spines['top'].set_visible(False)
ax_hist.spines["left"].set_visible(False)
ax_hist.yaxis.set_visible(False)


for data, color in ((data_control, 'k'), (data_RR, '#1b9e77')):
    selection = data[(data['frame']*dt>50*60) & (data['frame']*dt<60*60)]
    # Mean speed over the 20 previous frames (not including the current and previous ones)
    selection['speed_prev20'] = selection.groupby('id')['speed'].transform(lambda s: s.shift(2).rolling(20, min_periods=20).mean())

    d = selection.dropna(subset=['speed_prev20']).copy()
    d['speed_prev20'] /= dt
    d['speed_bin'] = pd.cut(d['speed_prev20'], bins=np.linspace(0, 1200, 50))

    g = d.groupby('speed_bin', observed=True).agg(
        rate=('mAR_start', 'mean'),
        speed=('speed_prev20', 'mean'),
    )
    g['rate'] *= fps

    ax.plot(g['speed'], g['rate'], color)

    # Distribution of speed
    speed = selection['speed_prev20']/dt
    ax_hist.hist(speed[speed<1200.], bins=100, color=color, histtype='step', lw=1.5, density=True)
    ax_hist.hist(speed[speed<1200.], bins=100, color=color, lw=1.5, density=True, alpha=0.5)


ax.set_xlim(0, 1200)
ax.set_xticks([0, 500, 1000])
ax.set_ylim(0, 1.)
ax.set_yticks([0, 0.5, 1])
ax.set_xlabel('Speed ($\mu$m/s)')
ax.set_ylabel('AR rate (Hz)')

plt.savefig(output_fig)
plt.show()
