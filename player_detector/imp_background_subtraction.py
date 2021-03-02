from player_detector.step import *
from utils.frame_utils import *
from log.log import *
import cv2


class BackgroundSubtractionPlayerDetector:

    def __init__(self, debug: bool = True, **kwargs):
        self.debug = debug
        self.log = Log(self, LoggingPackage.player_detector)
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
            Step("remove green", remove_green, debug=self.debug),
            Step("background substitution", self.background_substitution, debug=self.debug),
            Step("delete small contours", delete_small_contours, params={'percentage_of_frame': self.params['ignore_contours_smaller_than']}, debug=self.debug),
            Step("join close contours", morphological_closing, debug=self.debug),
            Step("delete small contours", delete_small_contours, params={'percentage_of_frame': self.params['ignore_contours_smaller_than']}, debug=self.debug),
            Step("erode", apply_erosion, debug=self.debug),

            # Step("filter by aspect ratio", self.filter_contours_by_aspect_ratio, debug=True),
            # Step("apply dilatation", self.apply_dilatation, debug=True),
            # Step("mark players", mark_players, params={'label': 'players'}, debug=True, modify_original_frame=False),
        ]

        for idx, step in enumerate(pipeline):
            frame = step.apply(idx, frame)

        players = detect_contours(frame, params={
            'ignore_contours_smaller_than': self.params['ignore_contours_smaller_than'],
            'keep_contours_by_aspect_ratio': self.params['keep_contours_by_aspect_ratio']
        })

        return players_from_contours(players)
