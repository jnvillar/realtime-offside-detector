import numpy as np
from typing import List
import utils.frame_utils as frame_utils
from video_repository.video_repository import *
from domain.player import *
from domain.aspec_ratio import *


class Step:
    def __init__(self, name: str, function, params=None, debug: bool = False, modify_original_frame=True):
        self.log = log.Log(self, log.LoggingPackage.player_detector)
        self.name = name
        self.function = function
        self.debug = debug
        self.params = params
        self.modify_original_frame = modify_original_frame

    def apply(self, number, original_frame, params=None):
        if params is None:
            params = self.params

        self.log.log('applying', {
            "number": number,
            "name": self.name,
            "params": self.params
        })

        frame = original_frame

        if not self.modify_original_frame:
            frame = original_frame.copy()

        frame = self.function(frame, params)

        if self.debug:
            frame_utils.show(frame, self.name, number)

        if self.modify_original_frame:
            return frame
        else:
            return original_frame


class PlayerDetector:

    def __init__(self, debug: bool = False):
        self.debug = debug
        self.last_frame = None
        self.log = log.Log(self, log.LoggingPackage.player_detector)
        self.fgbg = cv2.createBackgroundSubtractorMOG2(history=100, detectShadows=False, varThreshold=50)
        self.players = []

    def background_substitution(self, original_frame, params):
        frame = self.fgbg.apply(original_frame)
        return frame

    def save_players(self, original_frame, params):
        contours = frame_utils.detect_contours_with_params(original_frame, {
            'percentage_of_frame': params['percentage_of_frame'],
            'aspect_ratio': AspectRatio.taller
        })
        self.players = players_from_contours(contours)
        return original_frame

    def find_players(self, frame):
        self.players = []

        pipeline: List[Step] = [
            Step("remove green", frame_utils.remove_green, debug=self.debug),
            Step("background substitution", self.background_substitution, debug=self.debug),
            Step("delete small contours", frame_utils.delete_small_contours, params={'percentage_of_frame': 0.01}, debug=self.debug),
            Step("join close contours", frame_utils.join_close_contours, debug=self.debug),
            Step("delete small contours", frame_utils.delete_small_contours, params={'percentage_of_frame': 0.01}, debug=self.debug),
            Step("erode", frame_utils.apply_erosion, debug=self.debug),

            # Step("filter by aspect ratio", self.filter_contours_by_aspect_ratio, debug=True),
            # Step("apply dilatation", self.apply_dilatation, debug=True),
            # Step("mark players", mark_players, params={'label': 'players'}, debug=True, modify_original_frame=False),

            Step("save players", self.save_players, params={'percentage_of_frame': 0.01}),
        ]

        for idx, step in enumerate(pipeline):
            frame = step.apply(idx, frame)

        return self.players

    def detect_players_in_frame(self, frame, frame_number) -> List[Player]:
        self.log.log("finding players", {"frame": frame_number})
        players = self.find_players(frame)
        self.log.log("detected players", {"amount": len(players), "players": players})
        return players
