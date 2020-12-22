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


def color_classifier(original_frame, players: [Player]):

    frame = frame_utils.remove_color(original_frame, Color.blue)
    frame_utils.show(frame, 'remove blue', 1)

    return players


class PlayerSorter:

    def __init__(self, debug: bool = False):
        self.log = log.Log(self, log.LoggingPackage.player_sorter)
        self.debug = debug

    def sort_players(self, frame, players: [Player]):
        sorted_players = color_classifier(frame, players)
        self.log.log("sorted players", {"players": players})
        return sorted_players
