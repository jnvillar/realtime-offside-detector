import cv2

from field_detector.field_detector import FieldDetector
from player_detector.player_detector import PlayerDetector
from test.dataset_generator.domain import *
import utils.math as math_utils
import math

from test.dataset_generator.utils import FrameDataPrinter
from utils.utils import ScreenManager, KeyboardManager


class FrameDataComparator:

    def compare(self, expected_frame_data: FrameData, actual_frame_data: FrameData):
        if expected_frame_data.get_frame_number() != actual_frame_data.get_frame_number():
            raise Exception(
                "The frame data objects that you are trying to compare belong to different frames (expected: {}, actual {})".format(
                    expected_frame_data.get_frame_number(), actual_frame_data.get_frame_number()))

        comparison_results = {
            'frame_number': actual_frame_data.get_frame_number(),
            'field': self.compare_field(expected_frame_data, actual_frame_data),
            # 'vanishing_point': self.compare_vanishing_point(expected_frame_data, actual_frame_data),
            # 'defending_team': self.compare_defending_team(expected_frame_data, actual_frame_data),
            # 'players': self.compare_players(expected_frame_data, actual_frame_data),
            # 'offside_line': self.compare_offside_line(expected_frame_data, actual_frame_data)
        }
        return comparison_results

    def compare_field(self, expected_frame_data: FrameData, actual_frame_data: FrameData):
        expected_field_mask = expected_frame_data.get_field_mask()
        actual_field_mask = actual_frame_data.get_field_mask()
        expected_field_mask_area = cv2.countNonZero(expected_field_mask)

        false_negatives_mask = cv2.subtract(expected_field_mask, actual_field_mask)
        false_negatives_area = cv2.countNonZero(false_negatives_mask)
        false_negative_percentage = false_negatives_area / expected_field_mask_area

        false_positives_mask = cv2.subtract(actual_field_mask, expected_field_mask)
        false_positives_area = cv2.countNonZero(false_positives_mask)
        false_positives_percentage = false_positives_area / expected_field_mask_area

        return {
            'missing_field_pixels': false_negatives_area,
            'missing_field_percentage': false_negative_percentage,
            'extra_field_pixels': false_positives_area,
            'extra_field_percentage': false_positives_percentage,
            'total_difference_percentage': false_negative_percentage + false_positives_percentage
        }

    def compare_vanishing_point(self, expected_frame_data: FrameData, actual_frame_data: FrameData):
        distance = math_utils.distance_between_points(expected_frame_data.get_vanishing_point(),
                                                      actual_frame_data.get_vanishing_point())
        x_axis_distance_percentage = distance / actual_frame_data.get_frame_width()
        y_axis_distance_percentage = distance / actual_frame_data.get_frame_height()

        return {
            'distance': distance,
            'x_axis_distance_percentage': x_axis_distance_percentage,
            'y_axis_distance_percentage': y_axis_distance_percentage
        }

    def compare_defending_team(self, expected_frame_data: FrameData, actual_frame_data: FrameData):
        expected_defending_team = expected_frame_data.get_players()[
            expected_frame_data.get_last_defense_player_index()].get_team()
        actual_defending_team = actual_frame_data.get_players()[
            actual_frame_data.get_last_defense_player_index()].get_team()

        defending_team_match = expected_defending_team == actual_defending_team
        return "Correct" if defending_team_match else "Incorrect"

    def compare_offside_line(self, expected_frame_data: FrameData, actual_frame_data: FrameData):
        expected_offside_line = expected_frame_data.get_offside_line()
        actual_offside_line = actual_frame_data.get_offside_line()

        slope1 = self._slope(expected_offside_line[0][0], expected_offside_line[0][1], expected_offside_line[1][0],
                             expected_offside_line[1][1])
        slope2 = self._slope(actual_offside_line[0][0], actual_offside_line[0][1], actual_offside_line[1][0],
                             actual_offside_line[1][1])

        return {'angle_difference': math.degrees(math.atan((slope2 - slope1) / (1 + (slope2 * slope1))))}

    def compare_players(self, expected_frame_data: FrameData, actual_frame_data: FrameData):
        detected_players: [Player] = actual_frame_data.get_players().copy()
        expected_players: [Player] = expected_frame_data.get_players().copy()

        correctly_detected_players = []
        correctly_detected_teams = []
        badly_detected_teams = []
        extra_detected_players = []

        # for every detected player, check if center is inside any expected player
        for detected_player in detected_players:
            detected_center = detected_player.get_center()
            possible_expected_players = []
            possible_expected_players_idx = []

            for idx, expected_player in enumerate(expected_players):
                if self.point_inside_bounding_box(detected_center, expected_player.get_position()):
                    possible_expected_players.append(expected_player)
                    possible_expected_players_idx.append(idx)

            # player is not expected
            if len(possible_expected_players) == 0:
                extra_detected_players.append(detected_player)
                break

            found = False


            for idx, possible in enumerate(possible_expected_players):
                if possible.team == detected_player.team:
                    correctly_detected_players.append(detected_player)
                    expected_players.pop(possible_expected_players_idx[idx])
                    correctly_detected_teams.append(detected_player)
                    found = True

            if not found:
                correctly_detected_players.append(detected_player)
                expected_players.pop(possible_expected_players_idx[0])
                badly_detected_teams.append(detected_player)

        # copy expected players and remove detected ones
        not_detected_players = expected_players

        return {
            'expected_players': len(expected_frame_data.get_players()),
            'detected_players': len(detected_players),
            'correctly_detected_players': len(correctly_detected_players),
            'extra_detected_players': len(extra_detected_players),
            'not_detected_players': len(not_detected_players),
            'badly_detected_teams': len(badly_detected_teams),
            'correctly_detected_teams': len(correctly_detected_players)
        }

    def point_inside_bounding_box(self, point, box):
        x, y = point
        down_left, upper_right = box

        if not (down_left[0] <= x <= upper_right[0]):
            return False

        if not (down_left[1] <= y <= upper_right[1]):
            return False

        return True

    # Line slope given two points:
    def _slope(self, x1, y1, x2, y2):
        return (y2 - y1) / (x2 - x1)


class ComparatorByStrategy:

    def __init__(self, comparison_strategy, debug):
        self.debug = debug
        self.comparison_strategy = comparison_strategy
        self.screen_manager = ScreenManager.get_manager()
        self.keyboard_manager = KeyboardManager()

    def compare(self, video, video_data):
        # index expected frame data by frame number
        video_data_map = {frame_data.get_frame_number(): frame_data for frame_data in video_data}
        results = []
        while True:
            frame = video.get_next_frame()
            if frame is None:
                break

            frame_number = video.get_current_frame_number()
            # perform comparison only if the frame is present in video_data_map
            if frame_number in video_data_map:
                expected_frame_data = video_data_map[frame_number]
                # preliminary steps (anything necessary to provide as input for the comparison step)
                self.comparison_strategy.prepare_for_detection(video, expected_frame_data)

                # detection and comparison of results
                comparison_results, detected_frame_data = self.comparison_strategy.detect_and_compare(video, expected_frame_data)
                print("Frame {}: {}".format(frame_number, comparison_results))
                results.append(comparison_results)
                break

                # debug visualization of results
                if self.debug:
                    self.comparison_strategy.show_comparison_results(detected_frame_data, expected_frame_data, video.get_current_frame())

                if self.debug:
                    key_code = cv2.waitKey(0)

                    # ESC to exit comparison
                    if self.keyboard_manager.key_was_pressed(key_code, constants.ESC_KEY_CODE):
                        break
            else:
                # some of the sub-problems require to perform detection over all frames to work properly, given that
                # results for one frame depend on results from previous frames
                self.comparison_strategy.detect_only(video)

        return results


class PlayerDetectorComparisonStrategy:

    def __init__(self, config):
        self.frame_data_printer = FrameDataPrinter()
        self.frame_data_comparator = FrameDataComparator()
        self.screen_manager = ScreenManager.get_manager()
        self.player_detector = PlayerDetector(None, **config['player_detector'])

    def prepare_for_detection(self, video, expected_frame_data):
        # apply detected field from dataset
        frame_with_field_detected = self.frame_data_printer.print(expected_frame_data, video.get_current_frame(), True, False, False, False, field_from_mask=True)
        video.set_frame(frame_with_field_detected)

    def detect_and_compare(self, video, expected_frame_data):
        detected_frame_data = self.detect_only(video)
        return self.frame_data_comparator.compare_players(expected_frame_data, detected_frame_data), detected_frame_data

    def detect_only(self, video):
        players = self.player_detector.detect_players(video)
        detected_frame_data = self._build_frame_data(video, players)
        return detected_frame_data

    def show_comparison_results(self, detected_frame_data, expected_frame_data, current_frame):
        detected_frame = self.frame_data_printer.print(detected_frame_data, current_frame.copy(), False, True, False, False)
        self.screen_manager.show_frame(detected_frame, "Detected players")
        expected_frame = self.frame_data_printer.print(expected_frame_data, current_frame.copy(), False, True, False, False)
        self.screen_manager.show_frame(expected_frame, "Expected players")

    def _build_frame_data(self, video, players):
        height, width = video.get_current_frame().shape[:2]
        return FrameDataBuilder()\
            .set_frame_number(video.get_current_frame_number())\
            .set_frame_height(height)\
            .set_frame_width(width)\
            .set_players_from_domain_players(players)\
            .build()


class FieldDetectorComparisonStrategy:

    def __init__(self, config):
        self.frame_data_printer = FrameDataPrinter()
        self.frame_data_comparator = FrameDataComparator()
        self.screen_manager = ScreenManager.get_manager()
        self.field_detector = FieldDetector(None, **config['field_detector'])

    def prepare_for_detection(self, video, expected_frame_data):
        frame_with_field_detected = self.frame_data_printer.print(expected_frame_data, video.get_current_frame(), True, False, False, False, field_from_mask=True)
        video.set_frame(frame_with_field_detected)

    def detect_and_compare(self, video, expected_frame_data):
        detected_frame_data = self.detect_only(video)
        return self.frame_data_comparator.compare_field(expected_frame_data, detected_frame_data), detected_frame_data

    def detect_only(self, video):
        video, field_mask = self.field_detector.detect_field(video)
        detected_frame_data = self._build_frame_data(video, field_mask)
        return detected_frame_data

    def show_comparison_results(self, detected_frame_data, expected_frame_data, current_frame):
        detected_frame = self.frame_data_printer.print(expected_frame_data, current_frame.copy(), True, False, False, False)
        self.screen_manager.show_frame(detected_frame, "Detected (mask) vs Expected (lines)")

    def _build_frame_data(self, video, field_mask):
        height, width = video.get_current_frame().shape[:2]
        return FrameDataBuilder()\
            .set_frame_number(video.get_current_frame_number())\
            .set_frame_height(height)\
            .set_frame_width(width)\
            .set_field_mask(field_mask)\
            .build()
