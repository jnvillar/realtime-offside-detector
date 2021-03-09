from domain.player import *
from utils.math import *
from log.log import *


class DistanceTracker:

    def __init__(self, **kwargs):
        self.log = Log(self, LoggingPackage.player_tracker)
        self.previous_players = []
        self.initialized = True
        self.debug = kwargs.get('debug', False)

    def track_players(self, frame, players: [Player]):
        # if there are too few players, do not start tracker
        if len(players) > 2 and self.initialized:
            self.initialized = False
            self.previous_players = players
            return players

        for player in players:
            center = player.get_box().get_center()

            min_distance = None
            possible_previous_player = None
            for previous_player in self.previous_players:
                previous_center = previous_player.get_box().get_center()
                distance = distance_between_points(center, previous_center)
                if min_distance is None:
                    min_distance = distance
                    possible_previous_player = previous_player
                elif distance < min_distance:
                    min_distance = distance
                    possible_previous_player = previous_player

            if possible_previous_player is not None:
                player.number = possible_previous_player.number

        return players
