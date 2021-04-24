from numpy.linalg import lstsq
from domain.line import *
import numpy as np
import math


def distance_between_points(point_one, point_two):
    return math.sqrt(
        pow(point_two[0] - point_one[0], 2) +
        pow(point_two[1] - point_one[1], 2)
    )


def get_lines_intersection(line1: Line, line2: Line):
    p1, p2, p3, p4 = line1.p0, line1.p1, line2.p0, line2.p1

    x = ((p1[0] * p2[1] - p1[1] * p2[0]) * (p3[0] - p4[0]) - (p1[0] - p2[0]) * (p3[0] * p4[1] - p3[1] * p4[0])) / \
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


#  If the line equation is y = ax + b and the coordinates of a point is (x0, y0)
#  then compare y0 and ax0 + b, for example if y0 > ax0 + b then the point is above the line
def is_point_above_line(point, line: Line):
    line_slope = line.get_slope()
    line_y_interception = line.get_y_intercept()
    # < is used instead of > because frame is inverted
    return point[1] < point[0] * line_slope + line_y_interception
