import math
from random import randint

import numpy as np
from scipy.interpolate import splev, splprep, CubicSpline

from ..models.atoms import Line, Point
from ..pens import Pen


# width: Maximum width
# n_points:
def generate_line(
    start_x: int,
    width: int,
    height: int,
    n_points: int,
    x_sin_amp: float,
    x_sin_freq: float,
    x_rand_amp: float,
    x_sin_amp_exp: float,
    x_sin_freq_exp: float,
    x_rand_amp_exp: float,
    y_sin_amp: float,
    y_sin_freq: float,
    y_rand_amp: float,
    y_sin_amp_exp: float,
    y_sin_freq_exp: float,
    y_rand_amp_exp: float,
    pen: Pen,
) -> Line:
    line = Line([], pen)

    for i in range(n_points):
        x = start_x + (i * (width / (n_points - 1)))

        frac = i / n_points
        new_x_rand_amp = round(x_rand_amp ** (1 + frac * x_rand_amp_exp))
        x += math.sin(
            abs(x_sin_freq * x ** (1 + frac * x_sin_freq_exp))
        ) * x_sin_amp ** (1 + frac * x_sin_amp_exp) + randint(
            -new_x_rand_amp, new_x_rand_amp
        )

        new_y_rand_amp = round(y_rand_amp ** (1 + frac * y_rand_amp_exp))
        y = (
            height
            + math.sin(abs(y_sin_freq * x ** (1 + frac * y_sin_freq_exp)))
            * y_sin_amp ** (1 + frac * y_sin_amp_exp)
            + randint(-new_y_rand_amp, new_y_rand_amp)
        )
        line.add_point(Point(x, y, pen))
    return line


# Given an array of points representing vertices of a line,
# returns a new array of n points, representing equidistant samples
# on a spline fitted to the original.
def sample_spline(line: Line, n_samples: int, tightness: float = 0) -> Line:
    x = np.array([point.x for point in line.points])
    y = np.array([point.y for point in line.points])
    xy = np.stack((x, y), axis=-1)

    # return Line(
    #     [Point(point.x, point.y, line.pen) for point in line.points],
    #     line.pen,
    # )
    # calculate spline representation of curve
    tck, _ = splprep([*xy.T], s=0, k=3)

    # sample points on spline
    u = np.linspace(0, 1, n_samples)
    sampled_points = splev(u, tck)
    sampled_points = np.stack(sampled_points, axis=-1)
    return Line(
        [Point(pt[0], pt[1], line.pen) for pt in sampled_points],
        line.pen,
    )

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

    return Line(
        [Point(point[0], point[1], line.pen) for point in equidistant_point_samples],
        line.pen,
    )


# plt.plot(*equidistant_point_samples.T, 'ok', label='original points')
# plt.plot(*xy.T, 'ok', label='original points')
# plt.plot(*sampled_points.T, '-r', label='fitted spline k=3, s=.2')

# plt.axis('equal')
# plt.legend()
# plt.xlabel('x')
# plt.ylabel('y')
# plt.show()
