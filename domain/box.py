from domain.player import *


class Box:
    def __init__(self, label, bounding_box, upper_left, upper_right, down_left, down_right, center):
        x, y, w, h = bounding_box

        self.label = label

        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self.upper_left = upper_left
        self.upper_right = upper_right
        self.down_left = down_left
        self.down_right = down_right
        self.center = (x + (w / 2), y + (h / 2))

    def get_label(self):
        return self.label

    def get_center(self):
        return self.center

    def get_width(self):
        return self.w

    def get_height(self):
        return self.h


def box_from_player(player) -> Box:
    x, y, w, h = player.bounding_box
    label = player.number

    return Box(
        label=label,
        bounding_box=player.bounding_box,

        upper_left=(x, y + h),
        down_left=(x, y),

        upper_right=(x + w, y + h),
        down_right=(x + w, y),

        center=(x + (w / 2), y + (h / 2))
    )
