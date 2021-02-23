from enum import Enum


class Color(Enum):
    def __init__(self, name, bgr_lower, bgr_upper):
        self.color_name = name
        self.lower = bgr_lower
        self.upper = bgr_upper

    def __str__(self):
        return self.color_name

    def __repr__(self):
        return str(self)

    green = "green", (25, 86, 6), (64, 255, 255)

    red_1 = "red", (0, 70, 50), (10, 255, 255)
    red_2 = "red", (170, 70, 50), (180, 255, 255)

    white = 'white', (0, 0, 0), (0, 0, 255)
    blue = "blue", (90, 50, 50), (140, 255, 255)
    yellow = "yellow", (15, 100, 100), (35, 255, 255)
    grey = "grey", (0, 0, 50), (179, 50, 255)
    black = "black", (0, 0, 0), (50, 50, 100)
    violet = 'violet', (0, 0, 0), (50, 50, 100)  # change this


class ColorRange(Enum):
    def __init__(self, name: str, color_range: [Color], color: Color):
        self.color_name = name
        self.color_range = color_range
        self.color = color

    def __str__(self):
        return self.color_name

    def __repr__(self):
        return str(self)

    def get_color(self):
        return self.color

    red = 'red', [Color.red_1, Color.red_2], (255, 0, 0)
    green = 'green', [Color.green], (0, 255, 0)
    blue = 'blue', [Color.blue], (255, 0, 0)
    gray = 'grey', [Color.grey, Color.white], (255, 255, 255)
    yellow = 'yellow', [Color.yellow], (0, 255, 255)
    violet = 'violet', [Color.violet], (127, 0, 255)
