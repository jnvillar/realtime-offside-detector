from player_detector.step import *
from utils.frame_utils import *
from log.log import *


class EdgesPlayerDetector:

    def __init__(self, **kwargs):
        self.debug = kwargs['debug']
        self.log = Log(self, LoggingPackage.player_detector)
        self.params = kwargs

    def find_players(self, frame):
        pipeline: [Step] = [
            Step(
                "remove green",
                remove_green, {},
                debug=self.debug
            ),

            Step(
                "detect edges",
                detect_edges, {
                    'threshold1': self.params['threshold1'],
                    'threshold2': self.params['threshold2']
                },
                debug=self.debug),

            Step(
                "dilatate",
                apply_dilatation, {},
                debug=self.debug),

            Step(
                "fill contours",
                fill_contours, {},
                debug=self.debug),

            Step(
                "erode",
                apply_erosion, {'iterations': 3},
                debug=self.debug),

            Step(
                "dilatate",
                apply_dilatation, {'iterations': 2},
                debug=self.debug),

            # Step(
            #     "apply_dilatation",
            #     apply_dilatation, {},
            #     debug=self.debug),

            # Step(
            #     "blur_image",
            #     apply_blur, {},
            #     debug=self.debug),

            # Step(
            #     "delete small contours",
            #     delete_small_contours, {
            #         'percentage_of_frame': 0.005
            #     }, debug=self.debug),
            #
            # Step("erode",
            #      apply_erosion,
            #      debug=self.debug),
            #
            # Step("join close edges",
            #      morphological_closing,
            #      debug=self.debug),
            #
            # Step("erode",
            #      apply_erosion,
            #      debug=self.debug),
            #
            # Step("join close edges",
            #      morphological_closing,
            #      debug=self.debug),
            #
            # Step("delete small contours",
            #      delete_small_contours, {'percentage_of_frame': 0.05},
            #      debug=self.debug),

            #
            # Step(
            #     "join close contours",
            #     join_close_contours,
            #     debug=self.debug),

            # Step("background substitution", self.background_substitution, debug=self.debug),
            # ,
            # Step("join close contours", join_close_contours, debug=self.debug),
            # Step("delete small contours", delete_small_contours, params={'percentage_of_frame': self.params['ignore_contours_smaller_than']}, debug=self.debug),
            # Step("erode", apply_erosion, debug=self.debug),

            # Step("filter by aspect ratio", self.filter_contours_by_aspect_ratio, debug=True),
            # Step("apply dilatation", self.apply_dilatation, debug=True),
            # Step("mark players", mark_players, params={'label': 'players'}, debug=True, modify_original_frame=False),
        ]

        for idx, step in enumerate(pipeline):
            frame = step.apply(idx, frame)

        players = detect_contours(frame, params=self.params)

        return players_from_contours(players)
