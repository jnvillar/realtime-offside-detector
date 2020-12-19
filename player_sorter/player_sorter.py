from video_repository.video_repository import *
from domain.player import *
import random


def random_classifier(players: [Player]):
    for player in players:
        rand_number = random.randint(1, 2)
        if rand_number == 1:
            player.team = Team.team_one
        else:
            player.team = Team.team_two
    return players


class PlayerSorter:

    def __init__(self):
        self.log = log.Log(self, log.LoggingPackage.player_sorter)

    def sort_players(self, frame, players: [Player]):
        sorted_players = random_classifier(players)
        self.log.log("sorted players", {"players": players})
        return sorted_players
