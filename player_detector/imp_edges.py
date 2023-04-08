from player_detector.step import *
from utils.frame_utils import *
from log.logger import *


class EdgesPlayerDetector:

    def __init__(self, **kwargs):
        self.debug = kwargs['debug']
        self.log = Logger(self, LoggingPackage.player_detector)
        self.params = kwargs

    def find_players(self, frame):
        ScreenManager.get_manager().show_frame(frame, "original") if self.debug else None

        pipeline: [Step] = self.steps()

        for idx, step in enumerate(pipeline):
            frame = step.apply(idx, frame)

        players = detect_contours(frame, params=self.params)

        return players_from_contours(players, self.debug)

    def steps(self):
        return [
            Step(
                "get h component",
                get_hsv_component, {'component': 'h'},
                debug=self.debug
            ),
            Step(
                "detect edges",
                detect_edges, {'threshold1': self.params.get('threshold1', 50), 'threshold2': self.params.get('threshold2', 60)},
                debug=self.debug),
            Step(
                "dilate",
                apply_dilatation, {'iterations': 2},
                debug=self.debug),
            Step(
                "fill contours",
                fill_contours, {},
                debug=self.debug),
        ]

    def form_two(self):
        return [
            Step(
                "remove green",
                remove_green, {},
                debug=self.debug
            ),

            Step(
                "detect edges",
                detect_edges, self.params,
                debug=self.debug
            ),

            Step(
                "closing",
                morphological_closing, {},
                debug=self.debug
            ),

            Step(
                "opening",
                morphological_opening, {},
                debug=self.debug
            ),

            Step(
                "fill contours",
                fill_contours, {},
                debug=self.debug
            ),

            Step(
                "closing",
                morphological_closing, {},
                debug=self.debug
            ),

            Step(
                "dilate",
                apply_dilatation, {},
                debug=self.debug
            ),

            Step(
                "opening",
                morphological_opening, {},
                debug=self.debug),

            Step(
                "opening",
                morphological_opening, {},
                debug=self.debug),

            Step(
                "fill contours",
                fill_contours, {},
                debug=self.debug),

            Step(
                "opening",
                morphological_opening, {},
                debug=self.debug),

            Step(
                "closing",
                morphological_closing, {},
                debug=self.debug
            ),

            Step(
                "fill contours",
                fill_contours, {},
                debug=self.debug),

            Step(
                "opening",
                morphological_opening, {},
                debug=self.debug),

            Step(
                "opening",
                morphological_opening, {},
                debug=self.debug),

            Step(
                "dilate",
                apply_dilatation, {},
                debug=self.debug),

            Step(
                "fill contours",
                fill_contours, {},
                debug=self.debug),

            Step(
                "dilatate",
                apply_dilatation, {'iterations': 2},
                debug=self.debug)]
