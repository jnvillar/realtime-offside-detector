from domain.team import *
from domain.box import *
from domain.color import ColorRange

number = 0


class Player:
    def __init__(self, bounding_box, id, team: Team = Team.unclassified, color: ColorRange = None, debug=False):
        x, y, w, h = bounding_box
        self.bounding_box = bounding_box
        self.x_coordinate = x
        self.y_coordinate = y
        self.width = w
        self.height = h
        self.team = team
        self.color = color
        self.number = id
        self.is_last_defending_player = False
        self.tracking_process_iteration = 0
        self.debug = debug

    def __str__(self):
        return 'Player:' + str(self.number) + ' (' + str(self.x_coordinate) + ',' + str(self.y_coordinate) + ')'

    def __repr__(self):
        return str(self)

    def get_box(self) -> Box:
        return box_from_player(self)

    def get_name(self):
        name = ''
        if self.debug:
            name = "W: {width} H:{height}".format(width=self.width, height=self.height)

        if self.team is not Team.unclassified:
            name = " {label}: {number}".format(label=self.team.get_label(), number=self.number)
            return name

        if self.color is not None:
            name += ' test'
            return name

        return name

    def get_label_color(self):
        if self.is_last_defending_player:
            return ColorRange.violet.get_color()

        if self.team is not Team.unclassified:
            return self.team.get_color()

        if self.color is not None:
            return self.color.get_color()

        return None

    def get_color(self):
        if self.team is not Team.unclassified:
            return self.team.get_color()

        if self.color is not None:
            return self.color.get_color()

        return None


def get_players_bb(players: [Player]):
    bb = []
    for player in players:
        bb.append(player.bounding_box)

    return bb


def players_from_contours(contours, debug):
    players = []
    global number

    for contour in contours:
        players.append(Player(contour, number, debug=debug))
        number += 1
    return players
