import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
from collections import OrderedDict
from scipy.constants import speed_of_light
from matplotlib.cm import ScalarMappable
from matplotlib.colors import ListedColormap
from palettable import cartocolors
mpl.rcParams['text.usetex'] = True
import json
import argparse

argparser = argparse.ArgumentParser()
argparser.add_argument(
    '--add-legend',
    action='store_true'
)
args = argparser.parse_args()

ADD_LEGEND = args.add_legend

def do_reshape(amp_err: float | list):
    if type(amp_err) is list:
        return np.reshape(np.asarray(amp_err), (2,1))
    elif type(amp_err) is float:
        return amp_err
    elif not amp_err:
        return 0

def make_error(d: float, y_height: int, xerr: float | list, **kwargs):
    return plt.errorbar(d, y_height,
        xerr=xerr,
        **{
            'marker': '.',
            'markersize': 10,
            'color': 'cornflowerblue',
            **kwargs
        }
    )

def check_em_class(sample: str):
    radio = ['NVSS', 'RACS-low1', 'RACS-mid1', 'MALS', 'Joint', 'TGSS', 'SUMSS', 'WENSS']
    ir_optical = ['CatWISE2020', 'Quaia']
    
    if any(x in sample for x in radio):
        return 'radio'
    elif any(x in sample for x in ir_optical):
        return 'ir_optical'
    else:
        print(sample)
        return 'unknown'

def exclude(sample: str, study: str):
    pass
    # match study:
    #     case 'secrest+21':
    #         return True
    # match study:
    #     case _:
    #         pass

def iterate_class(em_class:str, ys: list):
    global start_y_ir_optical
    global start_y_radio
    
    match em_class:
        case 'ir_optical':
            i = start_y_ir_optical
            ys.append(i-0.2)
            start_y_ir_optical -= 1
        case 'radio':
            i = start_y_radio
            ys.append(i-0.2)
            start_y_radio -= 1
        case _:
            raise Exception('Nice rig.')
    
    return i

def survey_to_frequency(survey: str) -> float:
    match survey:
        case 'NVSS':
            return 1.400e9
        case 'RACS-low1':
            return 887.5e6
        case 'RACS-mid1':
            return 1367.5e6
        case 'CatWISE2020':
            return speed_of_light / 3.4e-6
        case 'MALS':
            return 1.27e9 # 1.27 GHz central frequency reported in wagenveld+24
        case 'Joint (NVSS x RACS-low1)':
            return None
        case 'Quaia-low':
            return speed_of_light / 0.673e-6  # Gaia DR2 G-band central wavelength to frequency
        case 'Combined (RACS-low1 x VLASS)':
            return None
        case 'TGSS':
            return 147e6 # siewert+21
        case 'SUMSS':
            return 843e6 # siewert+21
        case 'WENSS':
            return 325e6 # siewert+21

with open('lit_vals.json', 'r', encoding='utf-8') as file:
    lit_vals = json.load(file)

n_samples = 0
n_radio = 0
n_ir_optical = 0
for study, val in lit_vals.items():
    for sample in val.keys():
        if exclude(sample, study):
            continue
        else:
            em_class = check_em_class(sample)
            match em_class:
                case 'radio':
                    n_radio += 1
                case 'ir_optical':
                    n_ir_optical += 1
                case _:
                    raise Exception('Sample class not recognised.')

start_y_radio = 0
start_y_ir_optical = -n_radio - 1
plt.figure(figsize=(5,6))
i = 1
xs = []
ys = []
labs = []
sample_labs = []
error_artists = []
label_artists = []


# Use OrderedDict to preserve the order of samples
ordered_samples = OrderedDict(
    (sample, None) for val in lit_vals.values() for sample in val.keys()
)

# Sort samples by survey frequency (lowest to highest) and keep as OrderedDict
sorted_samples = OrderedDict(
    sorted(ordered_samples.items(), key=lambda item: survey_to_frequency(item[0]) or float('inf'))
)

# Normalize frequencies for colormap
frequencies = [survey_to_frequency(sample) for sample in ordered_samples.keys()]
# Define discrete colors for each survey frequency
unique_frequencies = sorted(set(filter(None, frequencies)))
base_cmap = cartocolors.qualitative.Prism_8.mpl_colormap
freq_colors = base_cmap(np.linspace(0, 1, len(unique_frequencies)))
grey_color = mpl.colors.to_rgba('grey')
cmap = ListedColormap([grey_color, *freq_colors])
colors = freq_colors
frequency_to_color = {freq: color for freq, color in zip(unique_frequencies, colors)}
frequency_to_color[None] = grey_color

# Discrete norm for colorbar: index-based bins (0 = grey/None)
norm = mpl.colors.BoundaryNorm(
    boundaries=np.arange(cmap.N + 1) - 0.5,
    ncolors=cmap.N
)

for sample in sorted_samples.keys():
    for study, value in lit_vals.items():
        if sample in value:
            data = value[sample]
            if exclude(sample, study):
                continue
            else:
                D_measured = data['measured_amp']
                D_errors = data['amp_1sigma']
                D_expected = data['expected_amp']
                em_class = check_em_class(sample)
                freq = survey_to_frequency(sample)
                c = frequency_to_color[freq]

                if type(D_measured) is dict:
                    amps = list(D_measured.values())
                    amp_1sigmas = list(D_errors.values())
                    for amp, err in zip(amps, amp_1sigmas):
                        i = iterate_class(em_class, ys)
                        d = amp / D_expected
                        
                        sample_lab = sample
                        if sample_lab in sample_labs:
                            lab = None
                        else:
                            lab = sample_lab
                            sample_labs.append(sample_lab)
                        
                        err = make_error(d, i,
                            xerr=do_reshape(amp_1sigmas) / D_expected, color=c,
                            label=lab
                        )
                        error_artists.append((err, study))
                        xs.append(d)
                        labs.append(study)
                    continue
                else:

                    i = iterate_class(em_class, ys)
                    sample_lab = sample
                    if sample_lab in sample_labs:
                        lab = None
                    else:
                        lab = sample_lab
                        sample_labs.append(sample_lab)

                    d = D_measured / D_expected
                    err = make_error(d, i,
                        xerr=do_reshape(D_errors) / D_expected, color=c,
                        label=lab
                    )
                    error_artists.append((err, study))
                    xs.append(d)
                    labs.append(study)

ax = plt.gca()
fig = plt.gcf()

for lab, y in zip(labs, ys):
    txt = ax.annotate(lab.capitalize(), (-0.6, y-0.2), horizontalalignment='right',
        verticalalignment='bottom', annotation_clip=False, size=9
    )
    label_artists.append((txt, lab))

# ax.tick_params(axis='y', which='both', length=0)
# plt.yticks([-n_radio / 2 + 0.5, start_y_ir_optical + n_ir_optical + 0.5])
# ax.set_yticklabels(['Radio', 'IR/Optical'])
# plt.setp(ax.get_yticklabels(), rotation=90)
# plt.yticks(fontsize=12)


# Add labels on the right y-axis

plt.xlabel('$\mathcal{D} / \mathcal{D}_{\mathrm{CMB}}$')
plt.axvline(x=1, c='black', alpha=0.3, zorder=-2)
# plt.axhline(
    # y=start_y_ir_optical + n_ir_optical + 0.5, color='black', alpha=0.2, linestyle='--'
# )
fig.tight_layout(rect=[-0.02, -0.005, 0.92, 0.82])

legend = None
if ADD_LEGEND:
    legend = plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.28), ncol=2)

# # Annotate 'Radio' and 'IR/Optical' on the right y-axis using axis coordinates
# ax.annotate(
#     'Radio', xy=(0.99, 0.6), xycoords='axes fraction',  xytext=(5, 0),
#     textcoords='offset points', ha='left', va='center', fontsize=12, rotation=270
# )
# ax.annotate(
#     'IR/Optical', xy=(0.99, 0.08), xycoords='axes fraction',  xytext=(5, 0),
#     textcoords='offset points', ha='left', va='center', fontsize=12, rotation=270
# )

# Create a ScalarMappable for the colorbar
sm = ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])

# Add the colorbar to the plot
cbar = plt.colorbar(sm, ax=ax, orientation='vertical', pad=0.02)
# cbar.set_label('Survey Frequency')

# Set colorbar ticks to each discrete level
cbar.set_ticks(np.arange(cmap.N))

# Update colorbar tick labels with numeric suffixes
def format_frequency_label(freq):
    if freq >= 1e12:
        return f'{freq/1e12:.3g} THz'
    elif freq >= 1e9:
        return f'{freq/1e9:.3g} GHz'
    elif freq >= 1e6:
        return f'{freq/1e6:.3g} MHz'
    else:
        return f'{freq:.3g} Hz'

tick_labels = ['Joint radio', *[format_frequency_label(freq) for freq in unique_frequencies]]
cbar.set_ticklabels(tick_labels)
cbar.ax.invert_yaxis()
cbar.ax.minorticks_off()

ax.set_yticks([])
ax.xaxis.set_major_locator(mpl.ticker.MaxNLocator(integer=True))
ax.set_xticks(np.arange(0, int(max(xs)) + 3))

def set_errorbar_visible(container, visible: bool):
    data_line, caplines, barlinecols = container.lines
    if data_line is not None:
        data_line.set_visible(visible)
    for cap in caplines:
        cap.set_visible(visible)
    for bar in barlinecols:
        bar.set_visible(visible)

def apply_visibility(mode: str, target_study: str = 'blake+02'):
    target = target_study.lower()
    for container, study in error_artists:
        show = mode == 'full' or (mode == 'blake' and study.lower() == target)
        set_errorbar_visible(container, show)
    for txt, lab in label_artists:
        show = mode == 'full' or (mode == 'blake' and lab.lower() == target)
        txt.set_visible(show)
    if legend:
        legend.set_visible(mode == 'full')

apply_visibility('full')
fig.canvas.draw()
full_bbox = fig.get_tightbbox(fig.canvas.get_renderer())

apply_visibility('blank')
plt.savefig('figures/amp_lit_values_blank.pdf', dpi=300, bbox_inches=full_bbox)

apply_visibility('blake')
plt.savefig('figures/amp_lit_values_blake02.pdf', dpi=300, bbox_inches=full_bbox)

apply_visibility('full')
plt.savefig('figures/amp_lit_values.pdf', dpi=300, bbox_inches=full_bbox)
plt.show()
