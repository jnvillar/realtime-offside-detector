from player_sorter.imp_color_automatic import *
from player_sorter.imp_color_given import *
from player_sorter.imp_kmean import *
from player_sorter.imp_bsas import *
from domain.video import *
from timer.timer import *
from log.log import *


class PlayerSorter:

    def __init__(self, analytics, **kwargs):
        self.analytics = analytics
        self.log = Log(self, LoggingPackage.player_sorter)

        methods = {
            'bsas': PlayerSorterBSAS(**kwargs['bsas']),
            'automatic_by_color': PlayerSorterByColorAutomatic(**kwargs['automatic_by_color']),
            'by_color': PlayerSorterByColor(),
            'kmeans': PlayerSorterByKMeans(**kwargs['kmeans'])
        }

        self.method = methods[kwargs['method']]

    def sort_players(self, frame: Video, players: [Player]):
        self.log.log("sorting players")
        Timer.start()
        sorted_players = self.method.sort_players(frame.get_current_frame(), players)
        elapsed_time = Timer.stop()
        self.log.log("sorted players", {"cost": elapsed_time, "players": players})
        return sorted_players
