"""Plot theoretical angular spectra with the SBI CatWISE shell defaults."""

from argparse import ArgumentParser
from pathlib import Path

import camb
import glass
import glass.ext.camb as glass_camb
import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["text.usetex"] = True

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import Normalize


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path,
        default=Path(__file__).resolve().parents[1] / "figures/glass_shell_spectra.svg",
    )
    args = parser.parse_args()

    N_BINS = 12
    edges = np.linspace(0, 1.0, 12)
    lmax = 1_000
    shells = glass.tophat_windows(edges)
    params = camb.set_params(
        H0=67.4, ombh2=0.0224, omch2=0.120, tau=0.054,
        As=2e-9, ns=0.96, NonLinear=camb.model.NonLinear_both,
    )
    spectra = glass_camb.matter_cls(params, lmax, shells)

    bias = 1.0
    ell = np.arange(1, lmax + 1)
    fig, ax = plt.subplots(figsize=(4, 3), layout="constrained")
    norm = Normalize(edges[0], edges[-1])
    cmap = plt.get_cmap("magma")
    for i, redshift in enumerate((edges[:-1] + edges[1:]) / 2):
        # GLASS orders each row as (i,i), (i,i-1), ..., (i,0).
        auto = spectra[i * (i + 1) // 2]
        ax.loglog(ell, bias**2 * auto[1:], color=cmap(norm(redshift)), lw=1.2)

    fig.colorbar(
        plt.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax, label=r"Shell effective $z$"
    )
    ax.set_xlabel(r"Multipole $\ell$")
    ax.set_ylabel(r"$C_\ell^{ii}$")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, bbox_inches=0)
    plt.close(fig)
    print(args.output)


if __name__ == "__main__":
    main()
