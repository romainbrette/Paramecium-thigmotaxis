'''
Various statistics
'''
import numpy as np
from bisect import bisect_right
from scipy import stats

def remove_nan(sample):
    # Remove nans from a sample
    return sample[~np.isnan(sample)]

def welch(mean1, sd1, n1, mean2, sd2, n2):
    # Welch's t-test (with unequal samples)
    # t-statistic
    t = (mean1 - mean2) / np.sqrt(sd1 ** 2 / n1 + sd2 ** 2 / n2)

    # degrees of freedom (Welch-Satterthwaite)
    df = (sd1 ** 2 / n1 + sd2 ** 2 / n2) ** 2 / ((sd1 ** 2 / n1) ** 2 / (n1 - 1) + (sd2 ** 2 / n2) ** 2 / (n2 - 1))

    # two-tailed p-value
    p = 2 * stats.t.sf(np.abs(t), df)

    return p

def welch_binomial(mean1, n1, mean2, n2):
    # Welch's t-test applied to binary variables
    sd1 = mean1*(1-mean1)
    sd2 = mean2*(1-mean2)
    return welch(mean1, sd1, n1, mean2, sd2, n2)

def cohen_d(sample1, sample2, n1=None, n2=None):
    if n1 is None:
        n1 = len(sample1)
        n2 = len(sample2)
    mean_diff = np.mean(sample1) - np.mean(sample2)
    pooled_std = np.sqrt(((n1 - 1) * np.var(sample1, ddof=1) +
                          (n2 - 1) * np.var(sample2, ddof=1)) /
                         (n1 + n2 - 2))
    return mean_diff / pooled_std


def cliffs_delta(sample1, sample2):
    # probability that a value from sample1 is greater than a value in sample2
    sample2_sorted = sorted(sample2)  # O(n log n)
    x_greater = sum(bisect_right(sample2_sorted, x) for x in sample1)
    x_less = len(sample1)*len(sample2) - x_greater
    return (x_greater - x_less) / (len(sample1) * len(sample2))

def bootstrap_difference(sample1, sample2, n_bootstraps = 10000):
    # Returns 95% confidence interval for mean difference
    boot_diffs = np.zeros(n_bootstraps)

    for i in range(n_bootstraps):
        boot_before = np.random.choice(sample1, size=len(sample1), replace=True)
        boot_after = np.random.choice(sample2, size=len(sample2), replace=True)
        boot_diffs[i] = np.mean(boot_after) - np.mean(boot_before)

    # Compute 95% confidence interval
    ci_lower, ci_upper = np.percentile(boot_diffs, [2.5, 97.5])

    # Mean difference estimate
    mean_diff_boot = np.mean(boot_diffs)

    return mean_diff_boot, ci_lower, ci_upper
