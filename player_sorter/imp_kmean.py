import utils.frame_utils as frame_utils
import utils.math as math
from sklearn.cluster import KMeans
from domain.player import *
from log.log import *
import cv2


class PlayerSorterByKMeans:
    def __init__(self, **kwargs):
        self.log = Log(self, LoggingPackage.player_sorter)
        self.debug = kwargs.get('debug', False)
        self.params = kwargs
        self.previous_centroids = None
        self.k_means = KMeans(n_clusters=2, random_state=0)

    def sort_players(self, original_frame, players: [Player]):
        if len(players) < 2:
            return players

        if self.params.get('median', False):
            player_representative_pixel = frame_utils.get_players_median_colors(original_frame, players)
        else:
            hsv_img = cv2.cvtColor(original_frame, cv2.COLOR_RGB2HSV)
            player_representative_pixel = frame_utils.get_players_mean_colors(hsv_img, players)

        player_labels = self.get_players_labels(player_representative_pixel)

        for itx, label in enumerate(player_labels):
            if label == 0:
                players[itx].team = self.params.get('team_one', Team.unclassified)
            else:
                players[itx].team = self.params.get('team_two', Team.unclassified)

        return players

    def sort_centroids(self, current_centroids):
        if self.previous_centroids is None:
            return current_centroids, False

        previous_centroids = self.previous_centroids

        # this heavily assumes that new centroids will be close to previous centroids
        if math.euclidean_distance(previous_centroids[0], current_centroids[0]) > math.euclidean_distance(previous_centroids[0], current_centroids[1]):
            self.log.log('centroids inverted') if self.debug else None
            # reverse array
            return reverse(current_centroids), True

        return current_centroids, False

    def get_players_labels(self, player_mean_colors):
        k_means_result = self.k_means.fit(player_mean_colors)
        self.previous_centroids, centroids_were_inverted = self.sort_centroids(k_means_result.cluster_centers_)

        player_labels = k_means_result.labels_
        if centroids_were_inverted:
            player_labels = invert_player_labels(player_labels)

        return player_labels


def reverse(array):
    return array[::-1]


def invert_player_labels(player_labels):
    return [1 if x == 0 else 0 for x in player_labels]
