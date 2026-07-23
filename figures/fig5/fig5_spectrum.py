'''
Spectrum of beating movies.
'''
from figures.figures import *
import os

output_fig = os.path.expanduser('~/Downloads/fig5_spectrum.pdf')

fmin, fmax = 5., 100.

figsize = (4, 3)

filenames134 = [
             'cell 134/spectrum_170_207_52_74.txt',
             'cell 134/spectrum_189_281_88_118.txt',
             'cell 134/spectrum_182_304_19_54.txt']

filenames95 = [
             #'cell 95/spectrum_67_150_7_73.txt',
             'cell 95/spectrum_91_111_176_216.txt',
             'cell 95/spectrum_133_163_109_253.txt',
             'cell 95/spectrum_58_89_68_251.txt'
             ]#,
             #'cell 95/spectrum_147_168_193_276.txt']


# Plot
fig, axes = plt.subplots(nrows=len(filenames134), ncols=2, figsize=figsize)
#fig, ax = plt.subplots(figsize=figsize)

def load_spectrum(filename):
    freq, power = np.loadtxt(filename).T
    ind = (freq>fmin) & (freq<fmax)
    freq, power = freq[ind], power[ind]
    return freq, power

for i, (filename134, filename95) in enumerate(zip(filenames134, filenames95)):
    ax1 = axes[i][0]
    ax2 = axes[i][1]
    for ax in (ax1, ax2):
        ax.spines['left'].set_visible(False)
        ax.set_yticks([])
        ax.set_yticklabels([])
        ax.yaxis.set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)

    freq, power = load_spectrum(filename95)
    ax1.plot(freq, power/power.max(), 'k')

    freq, power = load_spectrum(filename134)
    ax2.plot(freq, power/power.max(), 'k')
    ax1.set_xlim(0, 100)
    ax2.set_xlim(0, 100)

plt.tight_layout()
plt.savefig(output_fig)
plt.show()
