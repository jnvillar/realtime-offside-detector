import utils.frame_utils as frame_utils
import utils.math as math
from sklearn.cluster import KMeans
from domain.player import *
from log.logger import *
import cv2


class PlayerSorterByKMeans:
    def __init__(self, **kwargs):
        self.log = Logger(self, LoggingPackage.player_sorter)
        self.debug = kwargs.get('debug', False)
        self.params = kwargs
        self.previous_centroids = None
        self.k_means = KMeans(n_clusters=2, random_state=0)

    def sort_players(self, original_frame, players: [Player]):
        if len(players) < 2:
            return players

        players_to_be_sorted = []
        if self.params.get('only_unclassified_players', False):
            for player in players:
                if player.team == team_unclassified:
                    players_to_be_sorted.append(player)
        else:
            players_to_be_sorted = players

        if len(players_to_be_sorted) == 0:
            return players

        if self.params.get('median', False):
            hsv_img = cv2.cvtColor(original_frame, cv2.COLOR_RGB2HSV)
            player_representative_pixel = frame_utils.get_players_median_colors(hsv_img, players_to_be_sorted, params=self.params)
        else:
            hsv_img = cv2.cvtColor(original_frame, cv2.COLOR_RGB2HSV)
            player_representative_pixel = frame_utils.get_players_mean_colors(hsv_img, players_to_be_sorted, params=self.params)

        player_labels = self.get_players_labels(player_representative_pixel)
        self.log.log('player representative pixels', {
            'players_to_be_sorted': players_to_be_sorted,
            'representative_pixels': player_representative_pixel,
            'labels': player_labels
        }) if self.debug else None

        for itx, label in enumerate(player_labels):
            if label == 0:
                players_to_be_sorted[itx].team = self.params.get('first_cluster_team', team_unclassified)
            else:
                players_to_be_sorted[itx].team = self.params.get('second_cluster_team', team_unclassified)

        return players

    def get_players_labels(self, player_mean_colors):
        if self.previous_centroids is None:
            k_means_result = self.k_means.fit(player_mean_colors)
            self.previous_centroids = k_means_result.cluster_centers_
            return k_means_result.labels_
        else:
            return self.k_means.predict(player_mean_colors)


def invert_player_labels(player_labels):
    return [1 if x == 0 else 0 for x in player_labels]
