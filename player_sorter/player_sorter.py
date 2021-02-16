from video_repository.video_repository import *
from player_sorter.imp_color_automatic import *
from player_sorter.imp_bsas import *


class PlayerSorter:

    def __init__(self, debug: bool = False):
        self.log = log.Log(self, log.LoggingPackage.player_sorter)
        self.debug = debug

    def sort_players(self, frame, players: [Player]):
        cluster_players(frame, players)
        sorted_players = automatic_color_classifier(frame, players)

        # sorted_players = color_classifier(frame, players, [])
        self.log.log("sorted players", {"players": players})
        return sorted_players
