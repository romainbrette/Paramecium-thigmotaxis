'''
Figure making
'''
from pylab import *
from stats import welch_binomial

#######################################
# CHANGE THIS TO THE ACTUAL DATA PATH #
#######################################
data_path = "/Volumes/DDRomain/Paramecium/Thigmotaxis/Zenodo"

def bars_proportions(ax, *conditions, verbose=True):
    '''
    Makes a plot with bars showing proportions of cells.
    Shows error bars based on binomial distribution (s.e.m.).

    `conditions` is a list of tuples (name, proportion, n).
    '''

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    name, prop, n = zip(*conditions)
    prop, n = np.array(prop), np.array(n)
    sd = (prop*(1-prop)/n)**.5

    ax.bar(
        name,
        100*prop,
        yerr=100*sd,
        color='0.6',
        width=0.6,
        capsize = 4,
        error_kw = dict(linewidth=1, zorder=3, ecolor="black")
    )

    ax.set_ylim(0, 100)
    ax.tick_params(direction='out', length=4, width=1)

    return ax

def bars_proportions_with_p(ax, *conditions, verbose=True):
    '''
    Makes a plot with bars showing proportions of cells.
    Shows error bars based on binomial distribution (s.e.m.).

    Works with just two conditions.
    '''

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    name, prop, n = zip(*conditions)
    prop, n = np.array(prop), np.array(n)
    sd = (prop*(1-prop)/n)**.5

    ax.bar(
        name,
        100*prop,
        yerr=100*sd,
        color='0.6',
        width=0.6,
        capsize = 4,
        error_kw = dict(linewidth=1, zorder=3, ecolor="black")
    )

    p = welch_binomial(prop[0], n[0], prop[1], n[1])
    if verbose:
        print('p =', p)

    # ---- Determine star based on p-value ----
    if p < 0.001:
        star = '***'
    elif p < 0.01:
        star = '**'
    elif p < 0.05:
        star = '*'
    else:
        star = 'ns'

    # ---- Draw significance bracket ----
    y_sig = 100 * (0.1 + max(prop + sd))
    h = 0.05  # height of bracket

    ax.plot([0, 0, 1, 1], [y_sig, y_sig + h, y_sig + h, y_sig], lw=1, c='black')
    ax.text(0.5, y_sig + h + 0.02, star, ha='center', va='bottom', fontsize=14)

    ax.set_ylim(0, 100)
    ax.tick_params(direction='out', length=4, width=1)

    return ax
