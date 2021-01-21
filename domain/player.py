from domain.team import *
from domain.box import *


class Player:
    def __init__(self, bounding_box, team: Team = Team.unclassified):
        x, y, w, h = bounding_box
        self.bounding_box = bounding_box
        self.x_coordinate = x
        self.y_coordinate = y
        self.width = w
        self.height = h
        self.team = team

    def box(self):
        return box_from_bounding_box(self.bounding_box)


def players_from_contours(contours):
    players = []
    for contour in contours:
        players.append(Player(contour))
    return players
