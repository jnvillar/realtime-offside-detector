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
        self.center = (int(x + (w / 2)), int(y + (h / 2)))

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

    move_y = 0

    # this is an attempt to focus the shorts/down part of the t-shirt
    if focused:
        resize_x = int(w / 3)
        resize_y = int(h / 2.2)
        move_y = int(h / 25)

    return Box(
        label=label,
        bounding_box=(x + resize_x, y + resize_y + move_y, w - (2 * resize_x), h - 2 * resize_y),

        upper_left=(x + resize_x, y + h - resize_y - move_y),
        down_left=(x + resize_x, y + resize_y - move_y),

        upper_right=(x - resize_x + w, y + h - resize_y - move_y),
        down_right=(x + w - resize_x, y + resize_y - move_y),

        center=(x + (w / 2), y + (h / 2))
    )
