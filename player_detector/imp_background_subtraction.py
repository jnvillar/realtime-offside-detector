from player_detector.step import *
from utils.frame_utils import *
from log.logger import *
import cv2


class BackgroundSubtractionPlayerDetector:

    def __init__(self, **kwargs):
        self.debug = kwargs['debug']
        self.log = Logger(self, LoggingPackage.player_detector)
        self.fgbg = cv2.createBackgroundSubtractorMOG2(
            history=kwargs['history'],
            detectShadows=kwargs['detect_shadows'],
            varThreshold=kwargs['var_threshold'])

        self.params = kwargs

    def background_substitution(self, original_frame, params):
        frame = self.fgbg.apply(original_frame)
        return frame

    def find_players(self, frame):
        pipeline: [Step] = [
            # Step("remove green", remove_green, debug=self.debug),
            Step("background substitution", self.background_substitution, debug=self.debug),
            Step("delete small contours", delete_small_contours, params=self.params, debug=self.debug),
            Step("remove lines", remove_lines_canny, params=self.params | {'gray_image': True}, debug=self.debug),
            Step("join close contours", morphological_closing, debug=self.debug),
            Step("delete small contours", delete_small_contours, params=self.params, debug=self.debug),
            Step("erode", apply_erosion, debug=self.debug),
        ]

        for idx, step in enumerate(pipeline):
            frame = step.apply(idx, frame)

        players = detect_contours(frame, params=self.params)

        return players_from_contours(players)
