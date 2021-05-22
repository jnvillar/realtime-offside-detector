from player_detector.imp_background_subtraction import *
from player_detector.imp_edges import *
from domain.player import *
from timer.timer import *
from log.log import *


class PlayerDetector:

    def __init__(self, analytics, **kwargs):
        self.analytics = analytics
        self.log = Log(self, LoggingPackage.player_detector)

        methods = {
            'background_subtraction': BackgroundSubtractionPlayerDetector(**kwargs['background_subtraction']),
            'edges': EdgesPlayerDetector(**kwargs['edges'])
        }

        self.method = methods[kwargs['method']]

    def detect_players_in_frame(self, frame, frame_number) -> [Player]:
        self.log.log("finding players", {"frame": frame_number})
        Timer.start()
        players = self.method.find_players(frame)
        elapsed_time = Timer.stop()
        players = [player for player in players if player.y_coordinate > 240]
        self.log.log("detected players", {"cost": elapsed_time, "amount": len(players), "players": players})

        return players
