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
        self.previous_centers = None

    def sort_players(self, original_frame, players: [Player]):
        hsv_img = cv2.cvtColor(original_frame, cv2.COLOR_RGB2HSV)
        player_mean_colors = []

        for itx, player in enumerate(players):
            player_box = player.get_box(focused=True)
            player_mean_color = frame_utils.get_box_mean_color(hsv_img, player_box)
            player_mean_colors.append(list(player_mean_color)[0:3])

        result = KMeans(n_clusters=2, random_state=0).fit(player_mean_colors)
        labels = result.labels_
        if self.previous_centers is None:
            self.previous_centers = result.cluster_centers_
        else:
            centroid = self.previous_centers[0]
            if math.euclidean_distance(centroid, result.cluster_centers_[0]) > math.euclidean_distance(centroid, result.cluster_centers_[1]):
                print('labels inverted')
                labels = [1 if x == 0 else 0 for x in labels]
                # reverse array
                self.previous_centers = result.cluster_centers_[::-1]
            else:
                self.previous_centers = result.cluster_centers_

        for itx, label in enumerate(labels):
            if label == 0:
                players[itx].team = self.params.get('team_one', Team.unclassified)
            else:
                players[itx].team = self.params.get('team_two', Team.unclassified)

        return players
