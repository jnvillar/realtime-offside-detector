import numpy as np
from typing import List
import utils.utils as utils
from video_repository.video_repository import *


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
            self.show(number, frame)

        if self.modify_original_frame:
            return frame
        else:
            return original_frame

    def show(self, number, frame):

        min_number = 0

        if number < min_number:
            return

        number = number - min_number

        name = str(number) + " " + self.name
        cv2.imshow(name, frame)
        x = number * 500
        y = int(x / 1500)
        if x > 1001:
            x = x - (1500 * y)
        cv2.moveWindow(name, x, (y * 500))


class Player:
    def __init__(self, coordinates, team=None):
        self.coordinates = coordinates
        self.team = team


class PlayerDetector:

    def __init__(self):
        self.last_frame = None
        self.log = log.Log(self, log.LoggingPackage.player_detector)
        self.frame_utils = utils.FrameUtils()
        self.fgbg = cv2.createBackgroundSubtractorMOG2(history=100, detectShadows=False, varThreshold=50)
        self.players = []

        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        self.kernel_dil = np.ones((1, 1), np.uint8)

    def mark_players(self, original_frame):
        for idx, player in enumerate(self.players):
            [x, y, w, h] = player.coordinates
            cv2.rectangle(original_frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(original_frame, 'p', (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2, cv2.LINE_AA)

        cv2.imshow('final result', original_frame)

    def remove_green(self, frame, params):
        # convert to hsv color space
        green_lower = (29, 86, 6)
        green_upper = (64, 255, 255)

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, green_lower, green_upper)

        ## mask shows where the green pixels are, so we negate it
        frame = cv2.bitwise_and(frame, frame, mask=~mask)
        return frame

    def apply_dilatation(self, frame, params):
        dilated_frame = cv2.dilate(frame, None, iterations=1)
        return dilated_frame

    def apply_erosion(self, frame, params):
        kernel = np.ones((3,), np.uint8)
        eroded_frame = cv2.erode(frame, None, iterations=1)
        return eroded_frame

    def delete_small_contours(self, frame, params):
        (contours, hierarchy) = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        for pic, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            contour_percentage_of_frame = self.frame_utils.percentage_of_frame(frame, area)
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
            contour_percentage_of_frame = self.frame_utils.percentage_of_frame(original_frame, area)
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
        original_frame = frame.copy()

        self.players = []

        pipeline: List[Step] = [
            Step("remove green", self.remove_green, debug=True),
            Step("background substitution", self.background_substitution, debug=True),
            Step("delete small contours", self.delete_small_contours, params={'percentage_of_frame': 0.01}, debug=True),
            Step("join close contours", self.join_close_contours, debug=True),
            Step("erode", self.apply_erosion, debug=True),

            # Step("filter by aspect ratio", self.filter_contours_by_aspect_ratio, debug=True),
            # Step("apply dilatation", self.apply_dilatation, debug=True),
            # Step("mark players", mark_players, params={'label': 'players'}, debug=True, modify_original_frame=False),

            Step("save players", self.save_players, params={'percentage_of_frame': 0.01}),
        ]

        for idx, step in enumerate(pipeline):
            frame = step.apply(idx, frame)

        self.mark_players(original_frame)

        return self.players

    def detect_players_in_frame(self, frame: Frame) -> List[Player]:
        self.log.log("finding players", {"frame": frame.get_frame_number()})

        frame = frame.get_frame()
        frame = cv2.resize(frame, (500, 500))
        players = self.find_players(frame)
        return players
