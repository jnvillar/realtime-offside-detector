from player_detector.imp_background_subtraction import *
from player_detector.imp_edges import *
from domain.player import *
from log.log import *

import cv2


class PlayerDetector:

    def __init__(self, debug: bool = False, **kwargs):
        self.debug = debug
        self.log = Log(self, LoggingPackage.player_detector)

        methods = {
            'background_subtraction': BackgroundSubtractionPlayerDetector(**kwargs['background_subtraction']),
            'edges': EdgesPlayerDetector(**kwargs['edges'])
        }

        self.method = methods[kwargs['method']]

    def detect_players_in_frame(self, frame, frame_number) -> [Player]:
        self.log.log("finding players", {"frame": frame_number})
        players = self.method.find_players(frame)
        self.log.log("detected players", {"amount": len(players), "players": players})
        return players
