from domain.player import *
from pyclustering.cluster.bsas import bsas, bsas_visualizer
import utils.frame_utils as frame_utils


def cluster_players(original_frame, players: [Player]):
    player_histograms = get_player_histograms(original_frame, players)
    bsas_instance = bsas(data=player_histograms, maximum_clusters=2, threshold=1.0)
    bsas_instance = bsas_instance.process()

    print('clusters', bsas_instance.get_clusters())
    print('representatives',  bsas_instance.get_representatives())
    bsas_visualizer.show_clusters(player_histograms, bsas_instance.get_clusters(), bsas_instance.get_representatives())


def get_player_histograms(original_frame, players: [Player]):
    player_histograms = []
    for player in players:
        player_histograms.append(frame_utils.get_histogram(original_frame, player.get_box()))
    return player_histograms
