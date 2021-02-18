from domain.player import *
from pyclustering.cluster.bsas import bsas
from log.log import *
import utils.frame_utils as frame_utils


class PlayerSorterBSAS:
    def __init__(self, debug: bool = False):
        self.log = Log(self, LoggingPackage.player_sorter)
        self.debug = debug

    def sort_players(self, original_frame, players: [Player]):
        player_histograms = frame_utils.get_player_histograms(original_frame, players)
        bsas_instance = bsas(data=player_histograms, maximum_clusters=2, threshold=75)
        bsas_instance = bsas_instance.process()

        clusters = bsas_instance.get_clusters()
        self.log.log('bsas_clusters', {'clusters': clusters})

        for idx, cluster in enumerate(clusters):
            for player_number in cluster:
                if idx == 0:
                    players[player_number].team = Team.team_one
                else:
                    players[player_number].team = Team.team_two

        return players