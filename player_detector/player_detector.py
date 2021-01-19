import numpy as np
from typing import List
import utils.frame_utils as frame_utils
from video_repository.video_repository import *
from domain.player import *
from domain.color import *


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

    def remove_green(self, original_frame, params):
        frame = frame_utils.remove_color(original_frame, Colors.green.colors)
        return frame

    def apply_dilatation(self, frame, params):
        dilated_frame = frame_utils.apply_dilatation(frame)
        return dilated_frame

    def apply_erosion(self, frame, params):
        eroded_frame = frame_utils.apply_erosion(frame)
        return eroded_frame

    def delete_small_contours(self, frame, params):
        (contours, hierarchy) = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        for pic, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            contour_percentage_of_frame = frame_utils.percentage_of_frame(frame, area)
            if contour_percentage_of_frame < params['percentage_of_frame']:
                cv2.fillPoly(frame, pts=[contour], color=0)
                continue

        return frame

    # https://stackoverflow.com/questions/52247821/find-width-and-height-of-rotatedrect
    def filter_contours_by_aspect_ratio(self, frame, params):
        (contours, hierarchy) = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        for pic, c in enumerate(contours):
            rect = cv2.minAreaRect(c)
            (x, y), (w, h), angle = rect
            # Assume player must be more tall than narrow, so, filter the ones that has more width than height

            if w > h:
                cv2.fillPoly(frame, pts=[c], color=0)

            # Assume player bb must be a rectangle, so, the division of larger side / shorter side must be more than 1

            aspect_ratio = max(w, h) / max(min(w, h), 1)
            if aspect_ratio < 0.9:
                cv2.fillPoly(frame, pts=[c], color=0)
                continue

        return frame

    # Use "close" morphological operation to close the gaps between contours
    # https://stackoverflow.com/questions/18339988/implementing-imcloseim-se-in-opencv
    def join_close_contours(self, original_frame, params):
        frame = cv2.morphologyEx(original_frame, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (6, 6)))
        return frame

    def background_substitution(self, original_frame, params):
        frame = self.fgbg.apply(original_frame)
        return frame

    def save_players(self, original_frame, params):
        (contours, hierarchy) = cv2.findContours(original_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        for pic, c in enumerate(contours):
            area = cv2.contourArea(c)
            contour_percentage_of_frame = frame_utils.percentage_of_frame(original_frame, area)
            if contour_percentage_of_frame < params['percentage_of_frame']:
                continue

            x, y, w, h = cv2.boundingRect(c)

            # Assume player must be more tall than narrow, so, filter the ones that has more width than height
            if w > h:
                continue

            # Assume player bb must be a rectangle, so, the division of larger side / shorter side must be more than 1
            aspect_ratio = max(w, h) / max(min(w, h), 1)
            if aspect_ratio < 0.9:
                continue

            x, y, w, h = cv2.boundingRect(c)
            self.players.append(Player([x, y, w, h]))

        return original_frame

    def find_players(self, frame):
        self.players = []

        pipeline: List[Step] = [
            Step("remove green", self.remove_green, debug=self.debug),
            Step("background substitution", self.background_substitution, debug=self.debug),
            Step("delete small contours", self.delete_small_contours, params={'percentage_of_frame': 0.01}, debug=self.debug),
            Step("join close contours", self.join_close_contours, debug=self.debug),
            Step("delete small contours", self.delete_small_contours, params={'percentage_of_frame': 0.01}, debug=self.debug),

            Step("erode", self.apply_erosion, debug=self.debug),

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
        return players
