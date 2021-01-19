from enum import Enum


class Color(Enum):
    def __init__(self, name, bgr_lower, bgr_upper):
        self.color_name = name
        self.lower = bgr_lower
        self.upper = bgr_upper

    green = "green", (29, 86, 6), (64, 255, 255)

    red_1 = "red", (0, 70, 50), (10, 255, 255)
    red_2 = "red", (170, 70, 50), (180, 255, 255)

    white = 'white', (0, 0, 0), (0, 0, 255)
    blue = "blue", (100, 50, 50), (130, 255, 255)
    yellow = "yellow", (15, 100, 100), (35, 255, 255)
    grey = "grey", (0, 0, 50), (179, 50, 255)
    black = "black", (0, 0, 0), (50, 50, 100)


class Colors(Enum):
    def __init__(self, colors: [Color]):
        self.colors = colors

    red = [Color.red_1, Color.red_2]
    green = [Color.green]
    blue = [Color.blue]
    gray = [Color.grey, Color.white]
    yellow = [Color.yellow]
