from player_tracker.imp_opencv_tracker import *
from player_tracker.imp_tracker_by_distance import *
from timer.timer import *


class PlayerTracker:

    def __init__(self, **kwargs):
        self.log = Log(self, LoggingPackage.player_tracker)

        methods = {
            'opencv': OpenCVTracker(**kwargs['opencv']),
            'distance': DistanceTracker(**kwargs['distance']),
        }

        self.method = methods[kwargs['method']]

    def track_players(self, frame, players: [Player]):
        self.log.log("tracking players")
        Timer.start()
        players = self.method.track_players(frame, players)
        elapsed_time = Timer.stop()
        self.log.log("players tracked", {'cost': elapsed_time})
        return players
