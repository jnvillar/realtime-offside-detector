from video_repository.video_repository import *
from domain.player import *
from domain.color import *
import utils.frame_utils as frame_utils
import random


def random_classifier(frame, players: [Player]):
    for player in players:
        rand_number = random.randint(1, 2)
        if rand_number == 1:
            player.team = Team.team_one
        else:
            player.team = Team.team_two
    return players


def color_classifier(original_frame, players: [Player], colors: [Colors]):
    frame = frame_utils.remove_color(original_frame, Colors.green.colors)
    frame = frame_utils.remove_color(frame, Colors.blue.colors)

    frame_utils.show(frame, 'remove team colors', 1)

    for player in players:
        if frame_utils.is_area_black(frame, player.box()):
            player.team = Team.team_boca
        else:
            player.team = Team.team_river

    return players


class PlayerSorter:

    def __init__(self, debug: bool = False):
        self.log = log.Log(self, log.LoggingPackage.player_sorter)
        self.debug = debug

    def sort_players(self, frame, players: [Player]):
        sorted_players = color_classifier(frame, players, [])
        self.log.log("sorted players", {"players": players})
        return sorted_players
