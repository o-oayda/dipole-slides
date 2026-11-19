Original dipole_signal.pdf and .pdf_tex: euclid-dipole-seminar branch.

The deck uses scripts/doppler_sky.qmd: the original Mollweide artwork is raster, with inline SVG labels inheriting the document font and a vector velocity marker.
Regenerate the label-free artwork with:

    pdftocairo -png -singlefile -r 200 dipole_signal.pdf dipole_signal-artwork

The SED is a static inline SVG in scripts/sed_schematic.qmd, based on csiro-2024.
