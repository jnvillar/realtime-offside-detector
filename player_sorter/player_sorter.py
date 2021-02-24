from log.log import *
from player_sorter.imp_color_automatic import *
from player_sorter.imp_bsas import *
from player_sorter.imp_color_given import *


class PlayerSorter:

    def __init__(self, debug: bool = False, **kwargs):
        self.log = Log(self, LoggingPackage.player_sorter)
        self.debug = debug

        methods = {
            'bsas': PlayerSorterBSAS(),
            'automatic_by_color': PlayerSorterByColorAutomatic(),
            'by_color': PlayerSorterByColor()
        }

        self.method = methods[kwargs['method']]

    def sort_players(self, frame, players: [Player]):
        sorted_players = self.method.sort_players(frame, players)
        self.log.log("sorted players", {"players": players})
        return sorted_players
