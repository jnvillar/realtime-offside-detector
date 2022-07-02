import cv2

from test.dataset_generator.domain import *
import utils.math as math_utils
import math


class FrameDataComparator:

    def compare(self, expected_frame_data: FrameData, actual_frame_data: FrameData):
        if expected_frame_data.get_frame_number() != actual_frame_data.get_frame_number():
            raise Exception("The frame data objects that you are trying to compare belong to different frames (expected: {}, actual {})".format(
                expected_frame_data.get_frame_number(), actual_frame_data.get_frame_number()))

        height, width, _ = expected_frame_data.get_field_mask().shape
        comparison_results = {
            'frame_number': actual_frame_data.get_frame_number(),
            'field': self.compare_field(expected_frame_data, actual_frame_data),
            'vanishing_point': self.compare_vanishing_point(expected_frame_data, actual_frame_data),
            'defending_team': self.compare_defending_team(expected_frame_data, actual_frame_data),
            'players': self.compare_players(expected_frame_data, actual_frame_data),
            'offside_line': self.compare_offside_line(expected_frame_data, actual_frame_data)
        }
        return comparison_results

    def compare_field(self, expected_frame_data: FrameData, actual_frame_data: FrameData):
        expected_field_mask = expected_frame_data.get_field_mask()
        actual_field_mask = actual_frame_data.get_field_mask()
        expected_field_mask_area = cv2.countNonZero(expected_field_mask)

        false_negatives_mask = expected_field_mask - actual_field_mask
        false_negatives_area = cv2.countNonZero(false_negatives_mask)
        false_negative_percentage = false_negatives_area / expected_field_mask_area

        false_positives_mask = actual_field_mask - expected_field_mask
        false_positives_area = cv2.countNonZero(false_positives_mask)
        false_positives_percentage = false_positives_area / expected_field_mask_area

        return {
            'missing_field_percentage': false_negative_percentage,
            'extra_field_percentage': false_positives_percentage
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

        slope1 = self._slope(expected_offside_line[0][0], expected_offside_line[0][1], expected_offside_line[1][0], expected_offside_line[1][1])
        slope2 = self._slope(actual_offside_line[0][0], actual_offside_line[0][1], actual_offside_line[1][0], actual_offside_line[1][1])

        return {'angle_difference': math.degrees(math.atan((slope2 - slope1) / (1 + (slope2 * slope1))))}

    def compare_players(self, expected_frame_data: FrameData, actual_frame_data: FrameData):
        detected_players: [Player] = actual_frame_data.get_players().copy()
        expected_players: [Player] = expected_frame_data.get_players().copy()

        defending_team_in_detected_frame_data = actual_frame_data.get_defending_team()
        defending_team_in_expected_frame_data = expected_frame_data.get_defending_team()

        # switch teams if defending teams are inverted
        if defending_team_in_detected_frame_data != defending_team_in_expected_frame_data:
            for detected_player in detected_players:
                if detected_player.team == Team.TEAM_ONE:
                    detected_player.team = Team.TEAM_TWO
                else:
                    detected_player.team = Team.TEAM_ONE

        correctly_detected_players_idx = []
        correctly_detected_players = []
        correctly_detected_teams = []
        badly_detected_teams = []
        extra_detected_players = []

        # for every detected player, check if center is inside any expected player
        for detected_player in detected_players:
            detected_center = detected_player.get_center()
            for idx, expected_player in enumerate(expected_players):
                if self.point_inside_bounding_box(detected_center, expected_player.get_position()):
                    correctly_detected_players.append(detected_player)
                    correctly_detected_players_idx.append(idx)
                    if detected_player.team == expected_player.team:
                        correctly_detected_teams.append(detected_player)
                    else:
                        badly_detected_teams.append(detected_player)
                    break
            extra_detected_players.append(detected_center)

        # copy expected players and remove detected ones
        not_detected_players = expected_players.copy()
        for idx in correctly_detected_players_idx:
            not_detected_players.pop(idx)

        return {
            'correctly_detected_players': len(correctly_detected_players),
            'extra_detected_players': len(extra_detected_players),
            'not_detected_players': len(not_detected_players),
            'badly_detected_teams': len(badly_detected_teams),
            'correctly_detected_teams': len(correctly_detected_players)
        }

    def point_inside_bounding_box(self, point, box):
        x, y = point
        upper_left, down_right = box

        if not (upper_left[0] <= x <= down_right[0]):
            return False

        if not (down_right[1] <= y <= upper_left[1]):
            return False

        return True

    # Line slope given two points:
    def _slope(self, x1, y1, x2, y2):
        return (y2 - y1) / (x2 - x1)
