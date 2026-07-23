'''
Stats of beating frequency
'''
from scipy.stats import mannwhitneyu
from scipy.stats import wilcoxon

mouth = ([71, 71, 73, 68],  [77, 82, 80, 81, 60])
oral = ([50, 51, 57, 49], [42, 49, 46, 43, 51])
anterior = ([24, 24, 25, 22], [27, 27])
dorsal = ([15, 17, 19, 17], [23, 24, 23, 22, 29])

print('Stats of beating frequency')
print()
print('Mouth:')
print('411 vs. Na+: p =', mannwhitneyu(mouth[0], mouth[1], alternative="two-sided", method="exact").pvalue)
print()
print('Oral groove:')
print('411 vs. Na+: p =', mannwhitneyu(oral[0], oral[1], alternative="two-sided", method="exact").pvalue)
print()
print('Dorsal:')
print('411 vs. Na+: p =', mannwhitneyu(dorsal[0], dorsal[1], alternative="two-sided", method="exact").pvalue)
print('411 < Na+: p =', mannwhitneyu(dorsal[0], dorsal[1], alternative="less", method="exact").pvalue)
print()
print('Anterior > dorsal in 411: p =', wilcoxon(anterior[0], dorsal[0], alternative="greater")[1])
#mannwhitneyu(x, y, alternative="greater", method="exact")

# Figures
# group1 = np.array(dorsal[0])
# group2 = np.array(dorsal[1])
#
# # --- tidy format ---
# df = pd.DataFrame({
#     "value": np.concatenate([group1, group2]),
#     "group": ["Group 1"] * len(group1) + ["Group 2"] * len(group2)
# })
#
# # --- plot ---
# plt.figure()
#
# # light boxplot (structure)
# # sns.boxplot(
# #     data=df, x="group", y="value",
# #     width=0.4, showcaps=True,
# #     boxprops={'facecolor':'none'},
# #     showfliers=False
# # )
#
# # raw data points
# sns.stripplot(
#     data=df, x="group", y="value",
#     jitter=0.08, size=6
# )
#
# # mean ± SEM
# means = df.groupby("group")["value"].mean()
# sems = df.groupby("group")["value"].sem()
#
# plt.errorbar(
#     x=[0, 1],
#     y=means,
#     yerr=sems,
#     fmt='o',
#     capsize=6,
#     linewidth=2
# )
#
# # --- aesthetics ---
# sns.despine()
# plt.xlabel("")
# plt.ylabel("Value")
# #plt.set_ylim(0,)
#
# plt.tight_layout()
# plt.show()
