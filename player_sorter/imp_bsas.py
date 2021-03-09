from domain.player import *
from pyclustering.cluster.bsas import bsas
from log.log import *
import utils.frame_utils as frame_utils


class PlayerSorterBSAS:
    def __init__(self, **kwargs):
        self.log = Log(self, LoggingPackage.player_sorter)
        self.debug = kwargs.get('debug', False)
        self.params = kwargs

    def sort_players(self, original_frame, players: [Player]):
        if len(players) < 2:
            return players

        player_histograms = frame_utils.get_player_histograms(original_frame, players)
        bsas_instance = bsas(data=player_histograms, maximum_clusters=self.params['clusters'], threshold= self.params['threshold'])
        bsas_instance = bsas_instance.process()

        clusters = bsas_instance.get_clusters()
        self.log.log('bsas_clusters', {'clusters': clusters})

        for idx, cluster in enumerate(clusters):
            for player_number in cluster:
                if idx == 0:
                    players[player_number].team = self.params['team_one']
                else:
                    players[player_number].team = self.params['team_two']

        return players
