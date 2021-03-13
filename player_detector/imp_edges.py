from player_detector.step import *
from utils.frame_utils import *
from log.log import *


class EdgesPlayerDetector:

    def __init__(self, **kwargs):
        self.debug = kwargs['debug']
        self.log = Log(self, LoggingPackage.player_detector)
        self.params = kwargs

    def find_players(self, frame):
        pipeline: [Step] = self.steps()

        for idx, step in enumerate(pipeline):
            frame = step.apply(idx, frame)

        players = detect_contours(frame, params=self.params)

        return players_from_contours(players, self.debug)

    def steps(self):
        return [
            Step(
                "get h component",
                get_h_component, {},
                debug=self.debug
            ),
            Step(
                "detect edges",
                detect_edges, self.params,
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
