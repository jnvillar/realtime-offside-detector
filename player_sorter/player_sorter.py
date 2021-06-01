from player_sorter.imp_color_automatic import *
from player_sorter.imp_color_given import *
from player_sorter.imp_kmean import *
from player_sorter.imp_bsas import *
from domain.video import *
from timer.timer import *
from log.logger import *


class PlayerSorter:

    def __init__(self, analytics, **kwargs):
        self.analytics = analytics
        self.log = Logger(self, LoggingPackage.player_sorter)

        methods = {
            'bsas': PlayerSorterBSAS(**kwargs['bsas']),
            'automatic_by_color': PlayerSorterByColorAutomatic(**kwargs['automatic_by_color']),
            'by_color': PlayerSorterByColor(),
            'kmeans': PlayerSorterByKMeans(**kwargs['kmeans'])
        }

        self.method = methods[kwargs['method']]

    def sort_players(self, video: Video, players: [Player]):
        self.log.log("sorting players")
        Timer.start('sorting players')
        sorted_players = self.method.sort_players(video.get_current_frame(), players)
        elapsed_time = Timer.stop('sorting players')
        self.save_event(video, sorted_players)
        self.log.log("sorted players", {"cost": elapsed_time, "players": sorted_players})
        return sorted_players

    def save_event(self, video: Video, players: [Player]):
        self.analytics.save({
            'frame': video.get_current_frame_number(),
            'players': [player.get_data() for player in players]})
