'''
Swimming speed in culture medium, distribution vs. t
'''
import os
from trajectories.magic_loading import *
from interface import *
import matplotlib.pyplot as plt
from figures.figures import *
from matplotlib.colors import LogNorm
from matplotlib.colors import PowerNorm
import seaborn as sns
from scipy.ndimage import gaussian_filter

filename = os.path.join(data_path, 'Dynamics/Log cells in culture medium/tracking_linked_with_features_20.0_fps_1_um.tsv')
output_fig = os.path.expanduser('~/Downloads/fig1_speed.pdf')

figsize = (3, 2)

# Read data
data = magic_load_trajectories(filename) # could be a simple read_csv
fps, _ = guess_fps_and_pixelsize(filename)
print('FPS =', fps, 'Hz')
dt = 1/fps

# Plot
fig = plt.figure(figsize=figsize, constrained_layout=True)
gs = fig.add_gridspec(1, 3, width_ratios=[5, 0.12, 1])
ax  = fig.add_subplot(gs[0])
cax = fig.add_subplot(gs[1])                 # colorbar, next to the density plot
axm = fig.add_subplot(gs[2], sharey=ax)      # marginal: P(speed)

#ax.spines['right'].set_visible(False)
#ax.spines['top'].set_visible(False)
#ax.spines["left"].set_visible(False)
#ax.yaxis.set_visible(False)

data['t'] = data['frame']*dt
data = data[(data['t']<7200) & (data['speed']/dt>50.) & (data['speed']/dt<2000.)] # 30 um/s
speed = np.asarray(data['speed'] / dt)
ok = np.isfinite(speed)
speed = speed[ok]
t = data['t']/60
t = t[ok]
t_bins = np.linspace(t.min(), t.max(), 31)
H, _, v_edges = np.histogram2d(t, speed, bins=[t_bins, 50])

counts = H.sum(axis=1, keepdims=True)

# smooth the counts, mostly along speed (axis 1), lightly along time (axis 0)
#H_s = gaussian_filter(H, sigma=(0.7, 2.0))

# renormalize each time column so it integrates to 1
#P = H_s / H_s.sum(axis=1, keepdims=True) / np.diff(v_edges)[None, :]
with np.errstate(invalid='ignore', divide='ignore'):
    P = H / counts / np.diff(v_edges)[None, :]
P[counts[:, 0] == 0] = np.nan
vmax = np.nanmax(P)

valid_cols = ~np.isnan(P).all(axis=1)       # keep this for the mode line
vmin=1e-2 * vmax
P_plot = np.where(np.isfinite(P), P, vmin)  # NaN (and inf) -> vmin
P_plot = np.maximum(P_plot, vmin)           # zeros / tiny values -> vmin

pcm = ax.pcolormesh(t_bins, v_edges, P_plot.T, cmap=sns.color_palette('Blues', as_cmap=True), shading='flat', # viridis ok too
                    norm=LogNorm(vmin=1e-2 * vmax, vmax=vmax))
# cmap = sns.color_palette('rocket', as_cmap=True)
# pcm = ax.pcolormesh(t_bins, v_edges, P.T, cmap=cmap, shading='flat')

# pcm = ax.pcolormesh(t_bins, v_edges, P.T, cmap='magma', shading='flat',
#                     norm=PowerNorm(gamma=0.4))

ax.axvline(60, color='k', ls='--', lw=1.5)
ax.set_xlabel('Time (min)')
ax.set_ylabel('Speed ($\mu$m/s)')
ax.set_xticks([0, 60, 120])

# Color bar
cbar = fig.colorbar(pcm, cax=cax)
cbar.ax.minorticks_off()
cbar.set_ticks([])

# overall distribution of speed, finer bins than the main panel
speed = speed[(t>60) & (t<65)]
v_fine = np.linspace(v_edges[0], v_edges[-1], 50)
v_mid = 0.5 * (v_fine[1:] + v_fine[:-1])
Pv, _ = np.histogram(speed, bins=v_fine, density=True)

axm.fill_betweenx(v_mid, 0, Pv, color='k', step='mid')  # solid black
axm.set_xlim(left=0)
axm.set_xticks([])
axm.set_xlabel('')
axm.spines['bottom'].set_visible(False)
axm.tick_params(labelleft=False)
for s in ('top', 'right'):
    axm.spines[s].set_visible(False)

plt.savefig(output_fig)
plt.show()
