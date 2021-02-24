from player_tracker.imp_opencv_tracker import *


class PlayerTracker:

    def __init__(self, debug: bool = False, **kwargs):
        self.log = Log(self, LoggingPackage.player_sorter)
        self.debug = debug
        methods = {
            'opencv': OpenCVTracker(**kwargs['opencv']),
        }
        self.method = methods[kwargs['method']]

    def track_players(self, frame, players: [Player]):
        return self.method.track_players(frame, players)
