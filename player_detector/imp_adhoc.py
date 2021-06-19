from player_detector.step import *
from utils.frame_utils import *
from log.logger import *

COLOR_MIN = np.array([20, 0, 0])
COLOR_MAX = np.array([80, 255, 255])


class AdHoc:

    def __init__(self, **kwargs):
        self.debug = kwargs['debug']
        self.log = Logger(self, LoggingPackage.player_detector)
        self.params = kwargs

    def find_players(self, original_frame):
        detect_player_zones = original_frame
        field_mask = original_frame

        pipeline: [Step] = self.steps_field()
        for idx, step in enumerate(pipeline):
            field_mask = step.apply(idx, field_mask)

        pipeline: [Step] = self.steps_players_zones()
        for idx, step in enumerate(pipeline):
            detect_player_zones = step.apply(idx, detect_player_zones, params={'field_mask': field_mask})

        ScreenManager.get_manager().show_frame(detect_player_zones, 'final result')

        players = detect_contours(detect_player_zones, params=self.params)

        return players_from_contours(players, self.debug)

    def steps_players(self):
        return [
            Step(
                "get h component",
                get_hsv_component, {'component': 'h'},
                debug=self.debug
            ),
            Step(
                "detect edges 2",
                detect_edges, {'threshold1': self.params.get('threshold1', 50), 'threshold2': self.params.get('threshold2', 60)},
                debug=self.debug),
            Step(
                "apply player mask",
                apply_mask, {'mask': 'player_mask'},
                debug=self.debug),
            Step(
                "dilatation 2",
                apply_dilatation, {'iterations': 1, 'element_size': (10, 10)},
                debug=self.debug),
            Step(
                "fill contours 2",
                fill_contours, {},
                debug=self.debug),

        ]

    def steps_field(self):
        return [
            Step(
                "get green mask",
                color_mask, {'min': COLOR_MIN, 'max': COLOR_MAX},
                debug=self.debug
            ),
            Step(
                "erosion on green mask",
                apply_erosion, {'iterations': 2},
                debug=self.debug
            ),
            Step(
                "closing on green mask",
                morphological_closing, {'percentage_of_frame': 6, 'iterations': 1},
                debug=self.debug
            ),
            Step(
                "fill on green mask",
                fill_contours, {},
                debug=self.debug
            ),
            Step(
                "erosion on green mask again",
                apply_erosion, {'iterations': 2},
                debug=self.debug
            ),
        ]

    def steps_players_zones(self):
        return [
            Step(
                "get h component",
                get_hsv_component, {'component': 'h'},
                debug=self.debug
            ),
            Step(
                "detect edges on h component",
                detect_edges, {'threshold1': self.params.get('threshold1', 50), 'threshold2': self.params.get('threshold2', 60)},
                debug=self.debug
            ),
            Step(
                "apply green mask on edges",
                apply_mask, {'mask': 'field_mask'},
                debug=self.debug),
            Step(
                "dilate edges",
                apply_dilatation, {'element_size': (15, 15)},
                debug=self.debug
            ),
            Step(
                "fill dilatation",
                fill_contours, {},
                debug=self.debug
            ),
        ]
