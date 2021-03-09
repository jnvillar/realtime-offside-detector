from player_tracker.imp_opencv_tracker import *
from player_tracker.imp_tracker_by_distance import *


class PlayerTracker:

    def __init__(self, debug: bool = False, **kwargs):
        self.log = Log(self, LoggingPackage.player_sorter)
        self.debug = debug
        methods = {
            'opencv': OpenCVTracker(**kwargs['opencv']),
            'distance': DistanceTracker(**kwargs['distance']),
        }
        self.method = methods[kwargs['method']]

    def track_players(self, frame, players: [Player]):
        self.log.log("tracking players")
        players = self.method.track_players(frame, players)
        self.log.log("tracking players")
        return players
