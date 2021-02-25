from player_detector.imp_background_subtraction import *
from domain.player import *
from log.log import *

import cv2


class PlayerDetector:

    def __init__(self, debug: bool = False, **kwargs):
        self.debug = debug
        self.log = Log(self, LoggingPackage.player_detector)
        self.fgbg = cv2.createBackgroundSubtractorMOG2(history=100, detectShadows=False, varThreshold=50)
        self.players = []
        methods = {
            'background_subtraction': BackgroundSubtractionPlayerDetector(**kwargs['background_subtraction']),
        }

        self.method = methods[kwargs['method']]

    def detect_players_in_frame(self, frame, frame_number) -> [Player]:
        self.log.log("finding players", {"frame": frame_number})
        players = self.method.find_players(frame)
        self.log.log("detected players", {"amount": len(players), "players": players})
        return players
