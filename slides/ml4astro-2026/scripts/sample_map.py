from dipoleutils.utils.samples import SimulatedDipoleMap
from dipoleutils.utils.plotting import smooth_map
import matplotlib
import matplotlib as mpl

matplotlib.use('Agg')

import matplotlib.pyplot as plt
import healpy as hp
import numpy as np


def sphere_map(hmap, cmap='coolwarm', unit='', nlon=96, nlat=48):
    lon = np.linspace(0, 2 * np.pi, nlon)
    lat = np.linspace(-np.pi / 2, np.pi / 2, nlat)
    lon2, lat2 = np.meshgrid(lon, lat)

    theta = np.pi / 2 - lat2
    phi = lon2
    values = hp.get_interp_val(hmap, theta.ravel(), phi.ravel()).reshape(theta.shape)

    x = np.cos(lat2) * np.cos(lon2)
    y = np.cos(lat2) * np.sin(lon2)
    z = np.sin(lat2)

    cmap = plt.get_cmap(cmap)
    norm = mpl.colors.Normalize(vmin=np.nanmin(values), vmax=np.nanmax(values))
    facecolors = cmap(norm(values))

    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(
        x, y, z,
        rstride=1,
        cstride=1,
        facecolors=facecolors,
        linewidth=0,
        antialiased=False,
        shade=False,
        rasterized=True,
    )
    ax.set_axis_off()
    ax.set_box_aspect([1, 1, 1])
    ax.view_init(elev=20, azim=35)

    mappable = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
    mappable.set_array([])
    fig.colorbar(mappable, ax=ax, shrink=0.65, label=unit)


sim = SimulatedDipoleMap()
dmap = sim.make_map(mean_density=100)


plt.rcParams.update({
    "text.usetex": True,
    "font.family": 'sans-serif',
})

hp.projview(
    dmap, cmap='coolwarm', unit='Number of galaxies',
    fontsize={"cbar_label": 15, "cbar_tick_label": 14},
    cb_orientation='vertical'
)
plt.savefig('figures/sample_dmap.pdf', bbox_inches='tight')
plt.close()

smooth_map(
    dmap, cmap='coolwarm', unit='Number of galaxies (smoothed)',
    fontsize={"cbar_label": 15, "cbar_tick_label": 14}, format='%.4g',
    cb_orientation='vertical'
)
plt.savefig('figures/sample_dmap_smooth.pdf', bbox_inches='tight')
plt.close()

sphere_map(dmap, cmap='coolwarm', unit='Number of galaxies')
plt.savefig('figures/sample_dmap_sphere.png', bbox_inches='tight', dpi=300)
plt.close()
