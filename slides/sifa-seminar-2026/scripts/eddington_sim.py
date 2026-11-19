import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from dipoleska.utils.plotting import plot_log_log_histogram


S_LOW = 1
S_CUT = 2
N_SAMPLES = 1_000_000
X = 3
BINS = 100
ABS_NOISE = 0.7
X_LIM_MAX = 30
rng = np.random.default_rng(42)


def format_flux_axis():
    ax = plt.gca()
    ax.set_xticks([1, S_CUT, 10, 10 * S_CUT])
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:g}'))


flux_samples = S_LOW * (1 - rng.uniform(size=N_SAMPLES)) ** (- 1 / X)
bin_width = (np.log10(flux_samples.max()) - np.log10(flux_samples.min())) / BINS
lower_bin = int(np.floor((np.log10(flux_samples.min()) - np.log10(S_CUT)) / bin_width))
upper_bin = int(np.ceil((np.log10(flux_samples.max()) - np.log10(S_CUT)) / bin_width))
bins = 10 ** (np.log10(S_CUT) + bin_width * np.arange(lower_bin, upper_bin + 1))
bins[-lower_bin] = S_CUT

plt.figure(figsize=(4,3))
plot_log_log_histogram(flux_samples, bins=bins)
plt.axvline(x=S_CUT, linestyle='--', color='black', alpha=0.5)
plt.xlabel('Flux density (brightness)')
plt.ylabel('Count in each flux bin')
plt.xlim(None, X_LIM_MAX)
format_flux_axis()
plt.savefig('figures/flux_dist_true.pdf', bbox_inches='tight')
plt.close()

# make cut at S_LOW with no error
flux_samples_cut = flux_samples[flux_samples > S_CUT]
plt.figure(figsize=(4,3))
plot_log_log_histogram(flux_samples, alpha=0.2, bins=bins)
plot_log_log_histogram(flux_samples_cut, bins=bins)
plt.axvline(x=S_CUT, linestyle='--', color='black', alpha=0.5)
plt.xlabel('Flux density (brightness)')
plt.ylabel('Count in each flux bin')
plt.xlim(None, X_LIM_MAX)
format_flux_axis()
plt.savefig('figures/flux_dist_cut.pdf', bbox_inches='tight')
plt.close()

# add absolute error and cut
flux_samples_noisy = flux_samples + rng.normal(scale=ABS_NOISE, size=len(flux_samples))
flux_samples_noisy_cut = flux_samples_noisy[flux_samples_noisy > S_CUT]
plt.figure(figsize=(4,3))
plot_log_log_histogram(flux_samples, alpha=0.2, bins=bins)
plot_log_log_histogram(flux_samples_noisy_cut, bins=bins, color='tomato')
plt.axvline(x=S_CUT, linestyle='--', color='black', alpha=0.5)
plt.xlabel('Flux density (brightness)')
plt.ylabel('Count in each flux bin')
plt.xlim(None, X_LIM_MAX)
format_flux_axis()
plt.savefig('figures/flux_dist_noisy_cut.pdf', bbox_inches='tight')
plt.close()
