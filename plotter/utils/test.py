import math
from random import randint

import numpy as np
from py5 import Py5Vector
from scipy.interpolate import splev, splprep


# width: Maximum width
# n_points:
def generate_line(
    start_x: int, width: int, height: int, n_points: int
) -> list[Py5Vector]:
    vertices = []
    x_sin_amp = 4 * (width / (n_points - 1))
    x_sin_freq = (2 * math.pi) / (width / (n_points - 1) / 2)
    x_rand_amp = round(1.3 * (width / (n_points - 1)))

    y_sin_amp = 300
    y_sin_freq = (2 * math.pi) / (width / (n_points - 1))
    y_rand_amp = 200
    for i in range(n_points):
        x = start_x + (i * (width / (n_points - 1)))
        x += (i / n_points) * math.sin(x_sin_freq * x) * x_sin_amp + randint(
            -x_rand_amp, x_rand_amp
        )

        y = height + (i / n_points) * (
            math.sin(y_sin_freq * x) * y_sin_amp + randint(-y_rand_amp, y_rand_amp)
        )
        vertices.append(Py5Vector(x, y))
    return vertices


# Given an array of points representing vertices of a line,
# returns a new array of n points, representing equidistant samples
# on a spline fitted to the original.
def sample_spline(
    points: list[Py5Vector], n_samples: int, tightness: float = 0
) -> list[Py5Vector]:
    x = np.array([point.x for point in points])
    y = np.array([point.y for point in points])
    xy = np.stack((x, y), axis=-1)

    # calculate spline representation of curve
    tck, _ = splprep([*xy.T], s=0, k=3)

    # sample points on spline
    u = np.linspace(0, 1, n_samples)
    sampled_points = splev(u, tck)
    sampled_points = np.stack(sampled_points, axis=-1)
    inter_point_differences = np.diff(sampled_points, axis=0)
    inter_point_distances = np.linalg.norm(inter_point_differences, axis=-1)
    cumulative_distance = np.cumsum(inter_point_distances)
    cumulative_distance /= cumulative_distance[-1]

    # compute spline coefficients for normalised cumulative distance
    tck_prime, _ = splprep(
        [np.linspace(0, 1, num=len(cumulative_distance))],
        u=cumulative_distance,
        s=0,
        k=3,
    )

    equidistant_u = splev(u, tck_prime)
    equidistant_point_samples = splev(equidistant_u, tck)
    equidistant_point_samples = np.stack(equidistant_point_samples, axis=-1).squeeze(
        axis=0
    )

    return [Py5Vector(point[0], point[1]) for point in equidistant_point_samples]


# plt.plot(*equidistant_point_samples.T, 'ok', label='original points')
# plt.plot(*xy.T, 'ok', label='original points')
# plt.plot(*sampled_points.T, '-r', label='fitted spline k=3, s=.2')

# plt.axis('equal')
# plt.legend()
# plt.xlabel('x')
# plt.ylabel('y')
# plt.show()
