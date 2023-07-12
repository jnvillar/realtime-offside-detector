from numpy.linalg import lstsq
from domain.line import *
import numpy as np
import math
import numpy


def distance_between_points(point_one, point_two):
    return math.sqrt(
        pow(point_two[0] - point_one[0], 2) +
        pow(point_two[1] - point_one[1], 2)
    )


def get_lines_intersection(line1: Line, line2: Line):
    p1, p2, p3, p4 = line1.p0, line1.p1, line2.p0, line2.p1
    denominator = (p1[0] - p2[0]) * (p3[1] - p4[1]) - (p1[1] - p2[1]) * (p3[0] - p4[0])
    # lines are parallel or coincident
    if denominator == 0:
        return None

    a = (p1[0] * p2[1] - p1[1] * p2[0])
    b = (p3[0] * p4[1] - p3[1] * p4[0])
    x = (a * (p3[0] - p4[0]) - (p1[0] - p2[0]) * b) / denominator
    y = (a * (p3[1] - p4[1]) - (p1[1] - p2[1]) * b) / denominator

    return int(round(x)), int(round(y))


def get_line(p1, p2):
    points = [p1, p2]
    x_coords, y_coords = zip(*points)
    A = np.vstack([x_coords, np.ones(len(x_coords))]).T
    m, c = lstsq(A, y_coords)[0]
    return m, c


def euclidean_distance(a, b):
    return numpy.linalg.norm(numpy.subtract(a, b))


def get_line_points(rho, theta):
    length = 2000
    a = np.cos(theta)
    b = np.sin(theta)
    x0 = a * rho
    y0 = b * rho
    x1 = int(x0 + length * (-b))
    y1 = int(y0 + length * (a))
    x2 = int(x0 - length * (-b))
    y2 = int(y0 - length * (a))

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


# Unit conversion function that converts degrees to radians
def degrees_to_radians(degrees):
    return degrees * np.pi / 180


# Calculates the angle between the given vector and the vector given by the x-axis (i.e (1, 0) vector). The
# given vector is expected to be a 2d vector, i.e an (x, y) vector
# Reference: https://www.omnicalculator.com/math/angle-between-two-vectors
def calculate_angle_from_vector(vector):
    numerator = vector[0]
    denominator = math.sqrt(pow(vector[0], 2) + pow(vector[1], 2))
    return math.acos(numerator / denominator)


# Calculates the location in an ellipse border from the given angle (in radians). The ellipse is defined by the given
# major and minor radius, with centroid in (0, 0)
def get_ellipse_point_from_angle(major_radius, minor_radius, angle):
    return major_radius * math.cos(angle), minor_radius * math.sin(angle)
