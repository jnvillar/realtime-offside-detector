from domain.team import *
from domain.box import *
from domain.color import ColorRange

number = 0


class Player:
    def __init__(self, bounding_box, number, team: Team = Team.unclassified, color: ColorRange = None):
        x, y, w, h = bounding_box
        self.bounding_box = bounding_box
        self.x_coordinate = x
        self.y_coordinate = y
        self.width = w
        self.height = h
        self.team = team
        self.color = color
        self.number = number

    def __str__(self):
        return 'Player:' + str(self.number)

    def __repr__(self):
        return str(self)

    def get_box(self):
        return box_from_player(self)

    def get_name(self):
        if self.team is not Team.unclassified:
            return self.team.id

        if self.color is not None:
            return 'test'

        return None

    def get_color(self):
        if self.team is not Team.unclassified:
            return self.team.get_color()

        if self.color is not None:
            return self.color.get_color()

        return None


def players_from_contours(contours):
    players = []
    global number

    for contour in contours:
        players.append(Player(contour, number))
        number += 1
    return players
