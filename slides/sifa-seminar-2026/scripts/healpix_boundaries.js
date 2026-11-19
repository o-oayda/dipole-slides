// HEALPix face-coordinate inverse projection. Sample edges, rather than joining
// only pixel corners: HEALPix edges are curved on the sphere.
// Geometry convention: https://healpix.sourceforge.io/doc/html/intro_Geometric_Algebraic_Properties_HEALPix.html
(() => {
  const jrll = [2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4];
  const jpll = [1, 3, 5, 7, 0, 2, 4, 6, 1, 3, 5, 7];
  function faceVector(x, y, face) {
    const jr = jrll[face] - x - y;
    const nr = jr < 1 ? jr : jr > 3 ? 4 - jr : 1;
    const z = jr < 1 ? 1 - nr * nr / 3 : jr > 3 ? nr * nr / 3 - 1 : (2 - jr) * 2 / 3;
    const phi = nr < 1e-14 ? 0 : (jpll[face] * nr + x - y) * Math.PI / (4 * nr);
    const r = Math.sqrt(Math.max(0, 1 - z * z));
    return [r * Math.cos(phi), r * Math.sin(phi), z];
  }
  function boundaries(nside, step = 16) {
    if (!Number.isInteger(nside) || nside < 1 || nside > 64 || (nside & (nside - 1))) {
      throw new RangeError('HEALPix nside must be a power of two between 1 and 64.');
    }
    if (!Number.isInteger(step) || step < 1) throw new RangeError('Boundary step must be positive.');
    const pixels = [];
    for (let face = 0; face < 12; face++) {
      for (let y = 0; y < nside; y++) for (let x = 0; x < nside; x++) {
        const points = [];
        // Counterclockwise around each face-coordinate cell.
        for (let edge = 0; edge < 4; edge++) for (let i = 0; i < step; i++) {
          const t = i / step;
          const u = edge === 0 ? x + t : edge === 1 ? x + 1 : edge === 2 ? x + 1 - t : x;
          const v = edge === 0 ? y : edge === 1 ? y + t : edge === 2 ? y + 1 : y + 1 - t;
          points.push(faceVector(u / nside, v / nside, face));
        }
        points.push(points[0]);
        pixels.push(points);
      }
    }
    return pixels;
  }
  // Return the face/y/x index used by boundaries(), rather than NESTED's
  // interleaved bit index. The angular-to-face mapping is the HEALPix mapping.
  function vectorPixel(nside, [x, y, z]) {
    const za = Math.abs(z);
    const phi = (Math.atan2(y, x) + 2 * Math.PI) % (2 * Math.PI);
    const tt = phi / (Math.PI / 2);
    let face, ix, iy;
    if (za <= 2 / 3) {
      const jp = Math.floor(nside * (0.5 + tt - 0.75 * z));
      const jm = Math.floor(nside * (0.5 + tt + 0.75 * z));
      const ifp = Math.floor(jp / nside), ifm = Math.floor(jm / nside);
      face = ifp === ifm ? (ifp & 3) + 4 : ifp < ifm ? ifp & 3 : (ifm & 3) + 8;
      ix = jm % nside;
      iy = nside - (jp % nside) - 1;
    } else {
      const ntt = Math.min(3, Math.floor(tt)), tp = tt - ntt;
      const tmp = nside * Math.sqrt(3 * (1 - za));
      const jp = Math.min(nside - 1, Math.floor(tp * tmp));
      const jm = Math.min(nside - 1, Math.floor((1 - tp) * tmp));
      face = z >= 0 ? ntt : ntt + 8;
      ix = z >= 0 ? nside - jm - 1 : jp;
      iy = z >= 0 ? nside - jp - 1 : jm;
    }
    return face * nside * nside + iy * nside + ix;
  }
  globalThis.HEALPixBoundaries = { faceVector, boundaries, vectorPixel };
})();
