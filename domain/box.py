from domain.player import *


class Box:
    def __init__(self, label, bounding_box, upper_left, upper_right, down_left, down_right):
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

    def get_label(self):
        return self.label


def box_from_player(player):
    x, y, w, h = player.bounding_box
    label = player.number

    return Box(
        label=label,
        bounding_box=player.bounding_box,

        upper_left=(x, y + h),
        down_left=(x, y),

        upper_right=(x + w, y + h),
        down_right=(x + w, y)
    )
