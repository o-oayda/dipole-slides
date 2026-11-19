import numpy as np
import matplotlib.pyplot as plt


N_SAMPLES = 10_000
xyz = np.random.normal(size=(N_SAMPLES, 3))
norm = np.linalg.norm(xyz, axis=1)
x, y, z = xyz[:, 0], xyz[:, 1], xyz[:, 2]
x /= norm
y /= norm
z /= norm

fig = plt.figure()
ax = fig.add_subplot(projection='3d')
ax.scatter(x, y, z, s=0.1, color='tomato')
ax.set_aspect('equal')
ax.set_xticklabels([])
ax.set_yticklabels([])
ax.set_zticklabels([])
plt.savefig('figures/points_3d.pdf', bbox_inches='tight')
plt.close()
