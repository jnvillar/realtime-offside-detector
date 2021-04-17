import math
import numpy as np
from numpy.linalg import lstsq


def distance_between_points(point_one, point_two):
    return math.sqrt(
        pow(point_two[0] - point_one[0], 2) +
        pow(point_two[1] - point_one[1], 2)
    )


def get_lines_intersection(line1, line2):
    if line1.__class__.__name__ in ('list', 'tuple'):
        p1, p2, p3, p4 = line1[0], line1[1], line2[0], line2[1]
    else:
        p1, p2, p3, p4 = line1['p1'], line1['p2'], line2['p1'], line2['p2']

    x = (
                (p1[0] * p2[1] - p1[1] * p2[0]) * (p3[0] - p4[0]) - (p1[0] - p2[0]) * (p3[0] * p4[1] - p3[1] * p4[0])) / \
        ((p1[0] - p2[0]) * (p3[1] - p4[1]) - (p1[1] - p2[1]) * (p3[0] - p4[0]))
    y = ((p1[0] * p2[1] - p1[1] * p2[0]) * (p3[1] - p4[1]) - (p1[1] - p2[1]) * (p3[0] * p4[1] - p3[1] * p4[0])) / (
            (p1[0] - p2[0]) * (p3[1] - p4[1]) - (p1[1] - p2[1]) * (p3[0] - p4[0]))

    return x, y


def get_line(p1, p2):
    points = [p1, p2]
    x_coords, y_coords = zip(*points)
    A = np.vstack([x_coords, np.ones(len(x_coords))]).T
    m, c = lstsq(A, y_coords)[0]
    return m, c


def get_line_points(rho, theta):
    a = np.cos(theta)
    b = np.sin(theta)
    x0 = a * rho
    y0 = b * rho
    x1 = int(x0 + 1000 * (-b))
    y1 = int(y0 + 1000 * (a))
    x2 = int(x0 - 1000 * (-b))
    y2 = int(y0 - 1000 * (a))

    return (x1, y1), (x2, y2)


def same_lines(line1, line2):
    rho1, theta1 = line1
    rho2, theta2 = line2
    return abs(rho1 - rho2) < 20 and abs(theta1 - theta2) < 0.1
