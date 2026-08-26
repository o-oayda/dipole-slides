import healpy as hp
import numpy as np
from dipoleutils.utils.plotting import smooth_map
import matplotlib.pyplot as plt
from astropy.coordinates import BarycentricMeanEcliptic, SkyCoord


plt.rcParams.update({
    "text.usetex": True,
    "font.family": 'sans-serif',
})

CATWISE_PATH = '/Users/ooay3125/Documents/catsim/catwise_S21_probably.npy'
NSIDE = 64
ZERO_LAT_INTERC = 68.89 # deg^-2
SLOPE = -0.051
dmap = np.load(CATWISE_PATH)

def linear_correction(pixel_lon_ecl):
    return ZERO_LAT_INTERC / (ZERO_LAT_INTERC + SLOPE * np.abs(pixel_lon_ecl))

def smooth_wrapper(dmap, **kwargs):
    smooth_map(
        dmap, 
        map_is_nested=True, 
        cmap='coolwarm',
        fontsize={"cbar_label": 15, "cbar_tick_label": 14},
        format='%.4g',
        unit='Quasar count per deg$^2$ (smoothed)'
    )

# apply linear correction as in secrest+21
l, b = hp.pix2ang(nside=NSIDE, ipix=np.arange(hp.nside2npix(NSIDE)), lonlat=True, nest=True)
coord = SkyCoord(l, b, unit='deg', frame='galactic')
coord = coord.transform_to(BarycentricMeanEcliptic)
ecl_lon, ecl_lat = coord.lon.deg, coord.lat.deg

dmap_deg_sq = dmap / hp.nside2pixarea(nside=NSIDE, degrees=True)
correction_factor = linear_correction(ecl_lat)
dmap_corrected = dmap_deg_sq * correction_factor

smooth_wrapper(dmap_deg_sq)
plt.savefig('figures/catwise_dmap_true.pdf', bbox_inches='tight')
plt.close()

smooth_wrapper(dmap_corrected)
plt.savefig('figures/catwise_dmap_cor.pdf', bbox_inches='tight')
plt.close()

