from video_repository.video_repository import *
from player_sorter.imp_color_automatic import *
from player_sorter.imp_bsas import *
from player_sorter.imp_color_given import *


class PlayerSorter:

    def __init__(self, debug: bool = False, **kwargs):
        self.log = log.Log(self, log.LoggingPackage.player_sorter)
        self.debug = debug
        self.methods = {
            'bsas': PlayerSorterBSAS(),
            'automatic_by_color': PlayerSorterByColorAutomatic(),
            'by_color': PlayerSorterByColor()
        }

    def sort_players(self, frame, players: [Player], method='by_color'):
        sorted_players = self.methods[method].sort_players(frame, players)
        self.log.log("sorted players", {"players": players})
        return sorted_players
