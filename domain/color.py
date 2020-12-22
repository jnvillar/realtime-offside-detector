from enum import Enum


class Color(Enum):
    def __init__(self, name, bgr_lower, bgr_upper):
        self.color_name = name
        self.lower = bgr_lower
        self.upper = bgr_upper

    green = "green", (29, 86, 6), (64, 255, 255)
    red = "red", (17, 15, 100), (50, 56, 200)
    blue = "blue", (86, 31, 4), (220, 88, 50)
    yellow = "yellow", (25, 146, 190), (62, 174, 250)
    grey = "grey", (103, 86, 65), (145, 133, 128)
