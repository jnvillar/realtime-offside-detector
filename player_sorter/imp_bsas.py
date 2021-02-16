from domain.player import *
from pyclustering.cluster.bsas import bsas
import utils.frame_utils as frame_utils


def cluster_players(original_frame, players: [Player]):
    bsas_instance = bsas(data=get_player_histograms(original_frame, players), maximum_clusters=3, threshold=1.0)
    bsas_instance.process()
    clusters = bsas_instance.get_clusters()
    print('clusters', clusters)


def get_player_histograms(original_frame, players: [Player]):
    player_histograms = []
    for player in players:
        player_histograms.append(frame_utils.get_histogram(original_frame, player.get_box()))
    return player_histograms
