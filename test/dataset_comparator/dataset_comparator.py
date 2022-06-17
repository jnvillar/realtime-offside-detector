import cv2

from test.dataset_generator.domain import *
import utils.math as math


class FrameDataComparator:

    def compare(self, expected_frame_data: FrameData, actual_frame_data: FrameData):
        height, width, _ = expected_frame_data.get_field_mask().shape
        comparison_results = {}

        false_negative_percentage, false_positive_percentage = self.compare_field(expected_frame_data, expected_frame_data)
        comparison_results['field'] = {
            'missing_field_percentage': false_negative_percentage,
            'extra_field_percentage': false_positive_percentage
        }

        distance, x_axis_distance_percentage, y_axis_distance_percentage = self.compare_vanishing_point(expected_frame_data, actual_frame_data)
        comparison_results['vanishing_point'] = {
            'distance': distance,
            'x_axis_distance_percentage': x_axis_distance_percentage,
            'y_axis_distance_percentage': y_axis_distance_percentage
        }

        defending_team_match = self.compare_defending_team(expected_frame_data, actual_frame_data)
        comparison_results['defending_team'] = "Correct" if defending_team_match else "Incorrect"

        self.compare_players(expected_frame_data, actual_frame_data)

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

        return false_negative_percentage, false_positives_percentage

    def compare_vanishing_point(self, expected_frame_data: FrameData, actual_frame_data: FrameData):
        distance = math.distance_between_points(expected_frame_data.get_vanishing_point(), actual_frame_data.get_vanishing_point())
        x_axis_distance_percentage = distance / actual_frame_data.get_frame_width()
        y_axis_distance_percentage = distance / actual_frame_data.get_frame_height()

        return distance, x_axis_distance_percentage, y_axis_distance_percentage

    def compare_defending_team(self, expected_frame_data: FrameData, actual_frame_data: FrameData):
        expected_defending_team = expected_frame_data.get_players()[expected_frame_data.get_last_defense_player_index()].get_team()
        actual_defending_team = actual_frame_data.get_players()[actual_frame_data.get_last_defense_player_index()].get_team()

        return expected_defending_team == actual_defending_team

    def compare_offside_line(self, expected_frame_data: FrameData, actual_frame_data: FrameData):
        # TODO: add logic
        return None

    def compare_players(self, expected_frame_data: FrameData, actual_frame_data: FrameData):
        # TODO: add logic
        return None


