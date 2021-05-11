from enum import Enum
import numpy as np
import cv2


class Color(Enum):
    def __init__(self, name, color):
        self.color_name = name
        self.color = color
        b, g, r = color
        self.hsv = cv2.cvtColor(np.uint8([[[b, g, r]]]), cv2.COLOR_BGR2HSV)[0][0]

    def __str__(self):
        return self.color_name

    def __repr__(self):
        return str(self)

    def get_color(self):
        return self.color

    def get_hsv_lower(self):
        h, s, v = self.hsv
        return [h - 10, 100, 0]

    def get_hsv_upper(self):
        h, s, v = self.hsv
        return [h + 10, 255, 255]

    # remember this is bgr (blue, green, red)

    red = 'red', (0, 0, 255)
    violet = 'violet', (238, 130, 238)
    white = 'white', (0, 0, 0)
    orange = 'orange', (0, 128, 255)
    pink = 'pink', (255, 153, 255)

    black = 'black', (000, 000, 000)

    grey_1 = 'grey_1', (220, 220, 220)
    grey_2 = 'grey_2', (211, 211, 211)
    grey_3 = 'grey_3', (192, 192, 192)
    grey_4 = 'grey_4', (169, 169, 169)
    grey_5 = 'grey_5', (128, 128, 128)
    grey_6 = 'grey_6', (105, 105, 105)

    blue_blue = 'blue', (255, 000, 000)
    blue_powderblue = 'powderblue', (230, 224, 176)
    blue_lightblue = 'lightblue', (230, 216, 173)
    blue_lightskyblue = 'lightskyblue', (250, 206, 135)
    blue_skyblue = 'skyblue', (235, 206, 135)
    blue_deepskyblue = 'deepskyblue', (255, 191, 0)
    blue_lightsteelblue = 'lightsteelblue', (222, 196, 176)
    blue_dodgerblue = 'dodgerblue', (255, 144, 30)
    blue_cornflowerblue = 'cornflowerblue', (237, 149, 100)
    blue_steelblue = 'steelblue', (180, 130, 70)
    blue_cadetblue = 'cadetblue', (160, 158, 95)
    blue_darkslateblue = 'darkslateblue', (139, 61, 72)
    blue_royalblue = 'royalblue', (225, 105, 65)
    blue_mediumblue = 'mediumblue', (205, 000, 000)
    blue_darkblue = 'darkblue', (139, 000, 000)
    blue_navy = 'navy', (128, 000, 000)
    blue_midnightblue = 'midnightblue', (112, 25, 25)

    green_lawngreen = 'green_lawngreen', (000, 252, 124)
    green_chartreuse = 'green_chartreuse', (0, 255, 127)
    green_limegreen = 'green_limegreen', (50, 205, 50)
    green_lime = 'green_lime', (00, 255, 000)
    green_forestgreen = 'green_forestgreen', (34, 139, 34)
    green_green = 'green_green', (000, 128, 000)
    green_darkgreen = 'green_darkgreen', (000, 100, 000)
    green_greenyellow = 'green_greenyellow', (47, 255, 173)
    green_yellowgreen = 'green_yellowgreen', (50, 205, 154)
    green_springgreen = 'green_springgreen', (127, 255, 000)
    green_mediumspringgreen = 'green_mediumspringgreen', (154, 250, 000)
    green_lightgreen = 'green_lightgreen', (144, 238, 144)
    green_palegreen = 'green_palegreen', (152, 251, 152)
    green_darkseagreen = 'green_darkseagreen', (143, 188, 143)
    green_mediumseagreen = 'green_mediumseagreen', (113, 179, 60)
    green_lightseagreen = 'green_lightseagreen', (170, 178, 32)
    green_seagreen = 'green_seagreen', (87, 139, 46)
    green_olive = 'green_olive', (000, 128, 128)
    green_darkolivegreen = 'green_darkolivegreen', (47, 107, 85)
    green_olivedrab = 'green_olivedrab', (35, 142, 107)

    # white = 'white', (0, 0, 0), (0, 0, 255), (255, 255, 255)
    #
    # red_1 = "red", (0, 70, 50), (10, 255, 255), (255, 0, 0)
    # yellow = "yellow", (15, 100, 100), (35, 255, 255), (0, 255, 255)
    # green = "green", (25, 10, 6), (64, 255, 255), (0, 255, 0)
    #
    # blue = "blue", (90, 50, 50), (140, 255, 255), (255, 0, 0)
    # red_2 = "red", (170, 70, 50), (180, 255, 255), (255, 0, 0)
    #
    # grey = "grey", (0, 0, 50), (179, 50, 255), (255, 255, 255)
    # black = "black", (0, 0, 0), (50, 50, 100), (0, 0, 0)
    # violet = 'violet', (0, 0, 0), (50, 50, 100), (127, 0, 255)  # change this


class ColorRange(Enum):
    def __init__(self, color: Color, color_range: [Color], ):
        self.color = color
        self.color_range = color_range

    def __str__(self):
        return self.color.name

    def __repr__(self):
        return str(self)

    def get_color(self):
        return self.color

    red = Color.red, [
        Color.red
    ]

    grey = Color.grey_1, [
        Color.grey_1,
        Color.grey_2,
        Color.grey_3,
        Color.grey_4,
        Color.grey_5,
        Color.grey_6
    ]

    black = Color.black, [
        Color.black
    ]

    white = Color.white, [
        Color.white
    ]

    orange = Color.orange, [
        Color.orange
    ]

    pink = Color.pink, [
        Color.pink
    ]

    blue = Color.blue_blue, [
        Color.blue_powderblue,
        Color.blue_lightblue,
        Color.blue_lightskyblue,
        Color.blue_skyblue,
        Color.blue_deepskyblue,
        Color.blue_lightsteelblue,
        Color.blue_dodgerblue,
        Color.blue_cornflowerblue,
        Color.blue_steelblue,
        Color.blue_cadetblue,
        Color.blue_darkslateblue,
        Color.blue_royalblue,
        Color.blue_blue,
        Color.blue_mediumblue,
        Color.blue_darkblue,
        Color.blue_navy,
        Color.blue_midnightblue
    ]

    green = Color.green_lime, [
        Color.green_lawngreen,
        Color.green_chartreuse,
        Color.green_limegreen,
        Color.green_lime,
        Color.green_forestgreen,
        Color.green_green,
        Color.green_darkgreen,
        Color.green_greenyellow,
        Color.green_yellowgreen,
        Color.green_springgreen,
        Color.green_mediumspringgreen,
        Color.green_lightgreen,
        Color.green_palegreen,
        Color.green_darkseagreen,
        Color.green_mediumseagreen,
        Color.green_lightseagreen,
        Color.green_seagreen,
        Color.green_olive,
        Color.green_darkolivegreen,
        Color.green_olivedrab,
    ]

    # green = 'green', [Color.green], (0, 255, 0)
    # blue = 'blue', [Color.blue], (255, 0, 0)
    # gray = 'grey', [Color.grey, Color.white], (255, 255, 255)
    # yellow = 'yellow', [Color.yellow], (0, 255, 255)
    # violet = 'violet', [Color.violet], (127, 0, 255)
