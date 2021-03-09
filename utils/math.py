import math


def distance_between_points(point_one, point_two):
    return math.sqrt(
        pow(point_two[0] - point_one[0], 2) +
        pow(point_two[1] - point_one[1], 2)
    )
