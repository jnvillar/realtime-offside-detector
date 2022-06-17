from domain.color import *
from domain.team import *
from domain.box import *

number = 0


class Player:
    def __init__(self, contour, id, team: Team = team_unclassified, color: Color = None, debug=False):
        contour, bounding_box = contour
        x, y, w, h = bounding_box
        self.bounding_box = bounding_box
        self.contour = contour
        self.x_coordinate = x
        self.y_coordinate = y
        self.width = w
        self.height = h
        self.team = team
        self.color = color
        self.number = id
        self.is_last_defending_player = False
        self.tracking_process_iteration = 0
        self.living_time = 0
        self.debug = debug

    def __str__(self):
        return 'Player:' + str(self.number) + ' (' + str(self.x_coordinate) + ',' + str(self.y_coordinate) + ')'

    def __repr__(self):
        return {
            'id': self.number,
            'team': self.team,
        }

    def get_data(self):
        return {
            'id': self.number,
            'team': self.team,
            'x': self.x_coordinate,
            'y': self.y_coordinate,
            'w': self.width,
            'h': self.height
        }

    def get_upper_left(self):
        return (
            self.x_coordinate,
            self.y_coordinate + self.height
        )

    def get_down_right(self):
        return (
            self.x_coordinate + self.width,
            self.y_coordinate
        )

    def get_box(self, focused=False) -> Box:
        return box_from_player(self, focused)

    def get_label(self):
        name = ''
        if self.debug:
            name = "T: {} W: {} H:{} AR:{:.2f}".format(self.team.get_label(), self.width, self.height,
                                                       self.height / self.width)
            return name

        if self.team is not team_unclassified:
            name = " {label}: {number}".format(label=self.team.get_label(), number=self.number)
            return name

        if self.color is not None:
            name += ' test {}'.format(self.number)
            return name

        return name

    def get_label_color(self):
        if self.is_last_defending_player:
            return violet.get_color()

        return 0, 0, 0

    def get_color(self):
        if self.team is not team_unclassified:
            return self.team.get_color()

        if self.color is not None:
            return self.color.get_color()

        return None


def get_players_bb(players: [Player]):
    bb = []
    for player in players:
        bb.append(player.bounding_box)

    return bb


def get_defending_players(players: [Player]):
    res = []
    for player in players:
        if player.team.is_defending:
            res.append(player)
    return res


def update_last_defending_player(last_defending_player: Player, players: [Player]):
    for player in players:
        player.is_last_defending_player = False
    last_defending_player.is_last_defending_player = True


def get_last_defending_player(players: [Player]):
    for player in players:
        if player.is_last_defending_player:
            return player
    return None


def players_from_contours(contours, debug=False, team=team_unclassified):
    players = []
    global number

    for contour in contours:
        players.append(Player(contour, number, debug=debug, team=team))
        number += 1
    return players
