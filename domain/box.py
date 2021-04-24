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

    def __str__(self):
        return 'Box: ' + ' ul:' + str(self.upper_left) + ' ur: ' + str(self.upper_right) + ' dl: ' + str(self.down_left) + ' dr: ' + str(self.down_right)


def box_from_player(player, focused=False) -> Box:
    x, y, w, h = player.bounding_box
    label = player.number

    resize_x = 0
    resize_y = 0
    if focused:
        resize_x = int(w / 3)
        resize_y = int(h / 3)

    return Box(
        label=label,
        bounding_box=player.bounding_box,

        upper_left=(x + resize_x, y + h - resize_y),
        down_left=(x + resize_x, y + resize_y),

        upper_right=(x - resize_x + w, y + h - resize_y),
        down_right=(x + w - resize_x, y + resize_y),

        center=(x + (w / 2), y + (h / 2))
    )
