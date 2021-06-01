from player_tracker.imp_tracker_by_distance import *
from player_tracker.imp_opencv_tracker import *
from domain.video import *
from timer.timer import *


class PlayerTracker:

    def __init__(self, analytics, **kwargs):
        self.analytics = analytics
        self.log = Logger(self, LoggingPackage.player_tracker)

        methods = {
            'opencv': OpenCVTracker(**kwargs['opencv']),
            'distance': DistanceTracker(**kwargs['distance']),
        }

        self.method = methods[kwargs['method']]

    def track_players(self, frame: Video, players: [Player]):
        self.log.log("tracking players")
        Timer.start('tracking players')
        players = self.method.track_players(frame.get_current_frame(), players)
        elapsed_time = Timer.stop('tracking players')
        self.log.log("players tracked", {'cost': elapsed_time})
        return players
