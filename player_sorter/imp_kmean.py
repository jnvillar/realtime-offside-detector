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
        self.label_team = kwargs.get('klusters_team')
        self.k_means = KMeans(n_clusters=kwargs.get('klusters', 3), random_state=0)
        self.labels_teams = {}

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

        frame = original_frame
        if self.params.get('hsv', False):
            frame = cv2.cvtColor(original_frame, cv2.COLOR_RGB2HSV)

        if self.params.get('median', False):
            player_representative_pixel = frame_utils.get_players_median_colors(
                frame,
                players_to_be_sorted,
                params=self.params)
        else:
            player_representative_pixel = frame_utils.get_players_mean_colors(
                frame,
                players_to_be_sorted,
                params=self.params)

        player_labels = self.get_players_labels(player_representative_pixel)
        self.log.log('player representative pixels', {
            'players_to_be_sorted': players_to_be_sorted,
            'representative_pixels': player_representative_pixel,
            'labels': player_labels
        }) if self.debug else None

        if len(self.labels_teams) is 0:
            count = {}
            for label in player_labels:
                count[label] = count.get(label, 0) + 1

            pairs = []
            for label, count in count.items():
                pairs.append((label, count))

            pairs.sort(key=lambda x: x[1])

            priority = [team_three, team_two, team_one]
            for itx, pair in enumerate(pairs):
                self.labels_teams[pair[0]] = priority[itx]

        for itx, label in enumerate(player_labels):
            players_to_be_sorted[itx].team = self.labels_teams[label]

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
