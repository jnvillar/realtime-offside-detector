from player_detector.imp_background_subtraction import *
from player_detector.imp_edges import *
from domain.player import *
from domain.video import *
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

    def detect_players(self, video: Video) -> [Player]:
        self.log.log("finding players", {"frame": video.get_current_frame_number()})
        Timer.start()
        players = self.method.find_players(video.get_current_frame())
        elapsed_time = Timer.stop()
        self.save_event(video, players)
        self.log.log("detected players", {"cost": elapsed_time, "amount": len(players), "players": players})
        return players

    def save_event(self, video: Video, players: [Player]):
        self.analytics.save({
            'frame': video.get_current_frame_number(),
            'players': [player.get_data() for player in players]})
