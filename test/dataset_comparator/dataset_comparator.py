import cv2

from field_detector.field_detector import FieldDetector
from player_detector.player_detector import PlayerDetector
from player_tracker.player_tracker import PlayerTracker
from player_sorter.player_sorter import PlayerSorter
from test.dataset_generator.domain import *
from domain.player import *
import utils.math as math_utils
import math
from utils.frame_utils import *

from test.dataset_generator.utils import FrameDataPrinter
from utils.utils import ScreenManager, KeyboardManager
from vanishing_point_finder.vanishing_point_finder import VanishingPointFinder


class FrameDataComparator:

    def compare(self, expected_frame_data: FrameData, actual_frame_data: FrameData):
        if expected_frame_data.get_frame_number() != actual_frame_data.get_frame_number():
            raise Exception(
                "The frame data objects that you are trying to compare belong to different frames (expected: {}, actual {})".format(
                    expected_frame_data.get_frame_number(), actual_frame_data.get_frame_number()))

        comparison_results = {
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

        intersection_area = cv2.countNonZero(cv2.bitwise_and(expected_field_mask, actual_field_mask))
        union_area = cv2.countNonZero(cv2.bitwise_or(expected_field_mask, actual_field_mask))
        jaccard_index = intersection_area / union_area

        return {
            'missing_field_pixels': false_negatives_area,
            'missing_field_percentage': false_negative_percentage,
            'extra_field_pixels': false_positives_area,
            'extra_field_percentage': false_positives_percentage,
            'total_difference_percentage': false_negative_percentage + false_positives_percentage,
            'jaccard_index': jaccard_index
        }

    def compare_vanishing_point(self, expected_frame_data: FrameData, actual_frame_data: FrameData,
                                central_circle_radius):
        expected_vp = expected_frame_data.get_vanishing_point()
        actual_vp = actual_frame_data.get_vanishing_point()
        distance_pixels = math_utils.distance_between_points(expected_vp, actual_vp)
        # the segment given by the distance between the expected vp and the actual vp, has a direction which can be
        # described by an angle. We use that angle to calculate the pixels:meters ratio in that specific direction
        distance_direction_vector = (expected_vp[0] - actual_vp[0], expected_vp[1] - actual_vp[1])
        distance_meters = self._calculate_distance_in_meters(distance_pixels, distance_direction_vector,
                                                             central_circle_radius)
        x_axis_distance_percentage = distance_pixels / actual_frame_data.get_frame_width()
        y_axis_distance_percentage = distance_pixels / actual_frame_data.get_frame_height()

        return {
            'distance_pixels': distance_pixels,
            'distance_meters': distance_meters,
            'distance_direction': distance_direction_vector,
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
        extra_detected_players = []

        # for every detected player, check if center is inside any expected player
        for detected_player in detected_players:
            detected_center = detected_player.get_center()
            match = False

            for idx, expected_player in enumerate(expected_players):
                if self._point_inside_bounding_box(detected_center, expected_player.get_position()):
                    correctly_detected_players.append(detected_player)
                    expected_players.pop(idx)
                    match = True
                    break

            if not match:
                extra_detected_players.append(detected_player)

        # copy expected players and remove detected ones
        not_detected_players = expected_players

        return {
            'expected_players': len(expected_frame_data.get_players()),
            'detected_players': len(detected_players),
            'correctly_detected_players': len(correctly_detected_players),
            'extra_detected_players': len(extra_detected_players),
            'not_detected_players': len(not_detected_players)
        }

    def compare_teams(self, expected, detected):
        detected_players: [Player] = detected.get_players().copy()
        expected_players: [Player] = expected.get_players().copy()

        expected_defending_player = expected_players[expected.last_defense_player_index]
        detected_defending_player = detected_players[expected.last_defense_player_index]

        expected_defending_team = expected_defending_player.team
        detected_defending_team = detected_defending_player.team

        ## switch teams if they are inverted
        # if (expected_defending_team != detected_defending_team):
        #     for player in detected_players:
        #         player.team = player.team.reverse()

        referee_idx = None
        for i, p in enumerate(expected_players):
            if p.team.is_referee():
                referee_idx = i
                break

        ## remove referee if present
        if referee_idx is not None:
            expected_players.pop(referee_idx)
            detected_players.pop(referee_idx)

        correctly_sorted_players = 0
        badly_sorted_players = 0

        for i, p in enumerate(expected_players):
            if p.team == detected_players[i].team:
                correctly_sorted_players += 1
            else:
                badly_sorted_players += 1

        return {
            "correctly_sorted_players": correctly_sorted_players,
            "badly_sorted_players": badly_sorted_players
        }

    def _point_inside_bounding_box(self, point, box):
        x, y = point
        point_1, point_2 = box

        if point_1[0] > point_2[0]:
            aux = point_1
            point_1 = point_2
            point_2 = aux

        if point_1[1] < point_2[1]:
            down_left = point_1
            upper_right = point_2

            return (down_left[0] <= x <= upper_right[0]) and (down_left[1] <= y <= upper_right[1])

        upper_left = point_1
        down_right = point_2

        return (upper_left[0] <= x <= down_right[0]) and (down_right[1] <= y <= upper_left[1])

    # Line slope given two points:
    def _slope(self, x1, y1, x2, y2):
        return (y2 - y1) / (x2 - x1)

    def _calculate_distance_in_meters(self, distance_pixels, distance_direction_vector, central_circle_radius):
        if distance_pixels == 0:
            return 0
        # the segment given by the distance between the expected vp and the actual vp, has a direction which can be
        # described by an angle. We use that angle to calculate the pixels:meters ratio in that specific direction
        direction_angle_radians = math_utils.calculate_angle_from_vector(distance_direction_vector)
        major_radius = central_circle_radius[0]
        minor_radius = central_circle_radius[1]
        ellipse_point = math_utils.get_ellipse_point_from_angle(major_radius, minor_radius, direction_angle_radians)
        ellipse_radius_on_point = math.dist(ellipse_point, (0, 0))

        # 9.15m is the radius of the central circle of a professional soccer field (according to FIFA rules)
        return distance_pixels * 9.15 / ellipse_radius_on_point


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
                comparison_results, detected_frame_data = self.comparison_strategy.detect_and_compare(
                    video, expected_frame_data
                )

                comparison_results["type"] = "detect_and_compare"
                comparison_results["time"] = detected_frame_data.get_time()
                comparison_results["frame_number"] = detected_frame_data.get_frame_number()

                print("Frame {}: {}".format(frame_number, comparison_results))
                results.append(comparison_results)

                # debug visualization of results
                if self.debug:
                    self.comparison_strategy.show_comparison_results(detected_frame_data, expected_frame_data,
                                                                     video.get_current_frame())

                if self.debug:
                    key_code = cv2.waitKey(0)

                    # ESC to exit comparison
                    if self.keyboard_manager.key_was_pressed(key_code, constants.ESC_KEY_CODE):
                        break
            else:
                # some of the sub-problems require to perform detection over all frames to work properly, given that
                # results for one frame depend on results from previous frames
                detected_frame_data = self.comparison_strategy.detect_only(video)
                results.append(
                    {
                        "frame_number": detected_frame_data.get_frame_number(),
                        "type": "detect_only",
                        "time": detected_frame_data.get_time(),
                    }
                )

        aggregations = self.comparison_strategy.calculate_aggregations(results)

        return {
            "frame_results": results,
            "aggregations": aggregations
        }


class IntertiaComparisonStrategy:
    def __init__(self, config):
        self.amount_of_frames = config.get('amount_of_frames', 1)
        self.analized_frames = 0

    def prepare_for_detection(self, video, expected_frame_data):
        return

    def detect_only(self, video):
        return

    def detect_and_compare(self, video, expected_frame_data):
        self.analized_frames += 1
        if self.analized_frames > self.amount_of_frames:
            return {}, {}

        inertias, k = calculate_optimal_k(video.get_current_frame())
        return {
            'inertias': inertias,
            'k': k
        }, {
            'inertias': inertias,
            'k': k
        }

    def show_comparison_results(self, detected_frame_data, expected_frame_data, current_frame):
        return

    def calculate_aggregations(self, results):
        return {}


class PlayerSorterComparisonStrategy:
    def __init__(self, config):
        self.frame_data_printer = FrameDataPrinter()
        self.frame_data_comparator = FrameDataComparator()
        self.screen_manager = ScreenManager.get_manager()
        self.player_sorter = PlayerSorter(None, **config['player_sorter'])
        self.players = []

    def prepare_for_detection(self, video, expected_frame_data):
        # apply detected field from dataset
        frame_with_field_detected = self.frame_data_printer.print(
            expected_frame_data, video.get_current_frame(), True, False, False, False, field_from_mask=True)
        video.set_frame(frame_with_field_detected)
        self.players = expected_frame_data.get_players()

    def detect_only(self, video):
        playersD = []
        for p in self.players:
            coordinate_1, coordinate_2 = p.position
            w = abs(coordinate_1[0] - coordinate_2[0])
            h = abs(coordinate_1[1] - coordinate_2[1])
            x = min(coordinate_1[0], coordinate_2[0])
            y = min(coordinate_1[1], coordinate_2[1])
            playersD.append(
                PlayerD(
                    contour=(None, (x, y, w, h)),
                    id=None
                ))

        sorted_players, elapsed_time = self.player_sorter.sort_players(video, playersD)
        detected_frame_data = self._build_frame_data(video, sorted_players, elapsed_time)
        return detected_frame_data

    def detect_and_compare(self, video, expected_frame_data):
        detected_frame_data = self.detect_only(video)
        return self.frame_data_comparator.compare_teams(expected_frame_data, detected_frame_data), detected_frame_data

    def show_comparison_results(self, detected_frame_data, expected_frame_data, current_frame):
        detected_frame = self.frame_data_printer.print(
            detected_frame_data,
            current_frame.copy(),
            False,
            True,
            False,
            False
        )
        self.screen_manager.show_frame(detected_frame, "Sorted players")

        expected_frame = self.frame_data_printer.print(
            expected_frame_data,
            current_frame.copy(),
            False,
            True,
            False,
            False
        )

        self.screen_manager.show_frame(expected_frame, "Expected players")

    def calculate_aggregations(self, results):
        # TODO: add calculation for aggregations of interest for this subproblem (e.g. mean, average, std. dev.)
        return {}

    def _build_frame_data(self, video, players, elapsed_time):
        height, width = video.get_current_frame().shape[:2]
        return FrameDataBuilder() \
            .set_frame_number(video.get_current_frame_number()) \
            .set_frame_height(height) \
            .set_frame_width(width) \
            .set_players_from_domain_players(players) \
            .set_time(elapsed_time) \
            .build()


class PlayerDetectorComparisonStrategy:

    def __init__(self, config):
        self.frame_data_printer = FrameDataPrinter()
        self.frame_data_comparator = FrameDataComparator()
        self.screen_manager = ScreenManager.get_manager()
        self.player_detector = PlayerDetector(None, **config['player_detector'])
        self.field_detector = FieldDetector(None, **config['field_detector'])
        self.player_tracker = PlayerTracker(None, **config['player_tracker'])

    def prepare_for_detection(self, video, expected_frame_data):
        # apply detected field from dataset
        frame_with_field_detected = self.frame_data_printer.print(
            expected_frame_data, video.get_current_frame(), True, False, False, False, field_from_mask=True)

        video.set_frame(frame_with_field_detected)

    def detect_and_compare(self, video, expected_frame_data):
        detected_frame_data = self.detect_only(video, detect_field=False)

        return self.frame_data_comparator.compare_players(expected_frame_data, detected_frame_data), detected_frame_data

    def detect_only(self, video, detect_field=True):
        if detect_field:
            video, _, _ = self.field_detector.detect_field(video)

        players, elapsed_time_players = self.player_detector.detect_players(video)
        players, elapsed_time_tracker = self.player_tracker.track_players(video, players=players)

        if self.player_tracker.method.__class__.__name__ == 'OffTracker':
            elapsed_time = elapsed_time_players
        else:
            elapsed_time = elapsed_time_tracker

        # filter players whose pixels are all black because tracking failed because of bad field detection in the middle frames
        players = [
            player for player in players if
            not is_area_black(video.get_current_frame(), player.get_box(), percentage=0.5)
        ]

        detected_frame_data = self._build_frame_data(video, players, elapsed_time)
        return detected_frame_data

    def show_comparison_results(self, detected_frame_data, expected_frame_data, current_frame):
        detected_frame = self.frame_data_printer.print(detected_frame_data, current_frame.copy(), False, True, False,
                                                       False)
        self.screen_manager.show_frame(detected_frame, "Detected players")
        expected_frame = self.frame_data_printer.print(expected_frame_data, current_frame.copy(), False, True, False,
                                                       False)
        self.screen_manager.show_frame(expected_frame, "Expected players")

    def calculate_aggregations(self, results):
        # TODO: add calculation for aggregations of interest for this subproblem (e.g. mean, average, std. dev.)
        return {}

    def _build_frame_data(self, video, players, elapsed_time):
        height, width = video.get_current_frame().shape[:2]
        return FrameDataBuilder() \
            .set_frame_number(video.get_current_frame_number()) \
            .set_frame_height(height) \
            .set_frame_width(width) \
            .set_players_from_domain_players(players) \
            .set_time(elapsed_time) \
            .build()


class FieldDetectorComparisonStrategy:

    def __init__(self, config):
        self.frame_data_printer = FrameDataPrinter()
        self.frame_data_comparator = FrameDataComparator()
        self.screen_manager = ScreenManager.get_manager()
        self.field_detector = FieldDetector(None, **config['field_detector'])

    def prepare_for_detection(self, video, expected_frame_data):
        # nothing to do here
        return

    def detect_and_compare(self, video, expected_frame_data):
        detected_frame_data = self.detect_only(video)
        return self.frame_data_comparator.compare_field(expected_frame_data, detected_frame_data), detected_frame_data

    def detect_only(self, video):
        video, field_mask, elapsed_time = self.field_detector.detect_field(video)
        detected_frame_data = self._build_frame_data(video, field_mask, elapsed_time)
        return detected_frame_data

    def show_comparison_results(self, detected_frame_data, expected_frame_data, current_frame):
        detected_frame = self.frame_data_printer.print(expected_frame_data, current_frame.copy(), True, False, False,
                                                       False)
        self.screen_manager.show_frame(detected_frame, "Detected (mask) vs Expected (lines)")

    def calculate_aggregations(self, results):
        average = {}
        for frame_result in results:
            for metric, value in frame_result.items():
                if value.__class__.__name__ != 'str':
                    average[metric + "_avg"] = average.get(metric + "_avg", 0) + value

        for avg_metric in average:
            average[avg_metric] = average[avg_metric] / len(results)

        return average

    def _build_frame_data(self, video, field_mask, elapsed_time):
        height, width = video.get_current_frame().shape[:2]
        return FrameDataBuilder() \
            .set_frame_number(video.get_current_frame_number()) \
            .set_frame_height(height) \
            .set_frame_width(width) \
            .set_field_mask(field_mask) \
            .set_time(elapsed_time) \
            .build()


class VanishingPointFinderComparisonStrategy:

    def __init__(self, config):
        self.frame_data_printer = FrameDataPrinter()
        self.frame_data_comparator = FrameDataComparator()
        self.screen_manager = ScreenManager.get_manager()
        self.field_detector = FieldDetector(None, **config['field_detector'])
        self.vanishing_point_finder = VanishingPointFinder(None, **config['vanishing_point_finder'])
        self.major_radius, self.minor_radius = self._calculate_central_circle_radius(
            config['vanishing_point_finder']['central_circle_axis'])

    def prepare_for_detection(self, video, expected_frame_data):
        frame_with_field_detected = self.frame_data_printer.print(expected_frame_data, video.get_current_frame(), True,
                                                                  False, False, False, field_from_mask=True)
        video.set_frame(frame_with_field_detected)

    def detect_and_compare(self, video, expected_frame_data):
        detected_frame_data = self.detect_only(video, detect_field=False)
        return self.frame_data_comparator.compare_vanishing_point(expected_frame_data, detected_frame_data,
                                                                  [self.major_radius,
                                                                   self.minor_radius]), detected_frame_data

    def detect_only(self, video, detect_field=True):
        if detect_field:
            video, _, _ = self.field_detector.detect_field(video)

        vanishing_point, vanishing_point_segments, elapsed_time = self.vanishing_point_finder.find_vanishing_point(
            video)
        return self._build_frame_data(video, vanishing_point, vanishing_point_segments, elapsed_time)

    def show_comparison_results(self, detected_frame_data, expected_frame_data, current_frame):
        expected_frame = self.frame_data_printer.print(expected_frame_data, current_frame.copy(), False, False, True,
                                                       False)
        detected_frame = self.frame_data_printer.print(detected_frame_data, current_frame.copy(), False, False, True,
                                                       False)
        self.screen_manager.show_frame(expected_frame, "Expected vanishing point")
        self.screen_manager.show_frame(detected_frame, "Detected vanishing point")

    def calculate_aggregations(self, results):
        return {}

    def _build_frame_data(self, video, vanishing_point, vanishing_point_segments, elapsed_time):
        height, width = video.get_current_frame().shape[:2]
        return FrameDataBuilder() \
            .set_frame_number(video.get_current_frame_number()) \
            .set_frame_height(height) \
            .set_frame_width(width) \
            .set_vanishing_point(vanishing_point) \
            .set_vanishing_point_segments(vanishing_point_segments) \
            .set_time(elapsed_time) \
            .build()

    def _calculate_central_circle_radius(self, central_circle_axis):
        # central_circle_axis is a list of two segments (each segment given by two points)
        central_circle_x_axis_points = central_circle_axis[0]
        central_circle_y_axis_points = central_circle_axis[1]

        major_radius = math.dist(central_circle_x_axis_points[0], central_circle_x_axis_points[1])
        minor_radius = math.dist(central_circle_y_axis_points[0], central_circle_y_axis_points[1])

        return major_radius, minor_radius
