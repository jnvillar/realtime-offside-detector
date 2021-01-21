from domain.player import *


class Box:
    def __init__(self, upper_left, upper_right, down_left, down_right):
        self.upper_left = upper_left
        self.upper_right = upper_right
        self.down_left = down_left
        self.down_right = down_right


def box_from_bounding_box(bounding_box: []):
    x, y, w, h = bounding_box

    return Box(
        upper_left=(x, y + h),
        down_left=(x, y),

        upper_right=(x + w, y + h),
        down_right=(x + w, y)
    )
