from domain.team import *
from domain.box import *

number = 0


class Player:
    def __init__(self, bounding_box, number, team: Team = Team.unclassified):
        x, y, w, h = bounding_box
        self.bounding_box = bounding_box
        self.x_coordinate = x
        self.y_coordinate = y
        self.width = w
        self.height = h
        self.team = team
        self.number = number

    def box(self):
        return box_from_player(self)


def players_from_contours(contours):
    players = []
    global number

    for contour in contours:
        players.append(Player(contour, number))
        number += 1
    return players
