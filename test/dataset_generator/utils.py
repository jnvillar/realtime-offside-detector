import cv2
import numpy

from test.dataset_generator import colors
from test.dataset_generator.domain import FrameDataBuilder
from utils import utils, constants


class FrameDataMerger:

    @staticmethod
    def merge(new_frame_data_list, old_frame_data_list):
        # first sort both lists
        old_frame_data_list.sort(key=lambda frame_data: frame_data.get_frame_number())
        new_frame_data_list.sort(key=lambda frame_data: frame_data.get_frame_number())
        index_old_list = 0
        index_new_list = 0
        size_old_list = len(old_frame_data_list)
        size_new_list = len(new_frame_data_list)
        result_list = []
        # iterate lists and merge them until at least one of them is completed
        while index_new_list < size_new_list and index_old_list < size_old_list:
            new_frame_data = new_frame_data_list[index_new_list]
            old_frame_data = old_frame_data_list[index_old_list]
            new_frame_number = new_frame_data.get_frame_number()
            old_frame_number = old_frame_data.get_frame_number()
            if new_frame_number < old_frame_number:
                result_list.append(new_frame_data)
                index_new_list += 1
            elif new_frame_number > old_frame_number:
                result_list.append(old_frame_data)
                index_old_list += 1
            else:
                result_list.append(FrameDataMerger._merge_frame_data_objects(new_frame_data, old_frame_data))
                index_old_list += 1
                index_new_list += 1

        # include remaining frame data objects from new_frame_data_list
        if index_new_list < size_new_list:
            result_list = result_list + new_frame_data_list[index_new_list:]

        # include remaining frame data objects from old_frame_data_list
        if index_old_list < size_old_list:
            result_list = result_list + old_frame_data_list[index_old_list:]

        return result_list

    @staticmethod
    def _merge_frame_data_objects(new_frame_data, old_frame_data):
        if new_frame_data.get_frame_number() != old_frame_data.get_frame_number():
            raise Exception("Should not merge data from different frames")
        # data from the new frame data object has priority over the old one
        field = old_frame_data.get_field() if new_frame_data.get_field() is None else new_frame_data.get_field()
        players = old_frame_data.get_players() if new_frame_data.get_players() is None else new_frame_data.get_players()
        last_defense_player_index = old_frame_data.get_last_defense_player_index() if new_frame_data.get_last_defense_player_index() is None else new_frame_data.get_last_defense_player_index()
        vanishing_point_segments = old_frame_data.get_vanishing_point_segments() if new_frame_data.get_vanishing_point_segments() is None else new_frame_data.get_vanishing_point_segments()

        return FrameDataBuilder() \
            .set_frame_number(new_frame_data.get_frame_number()) \
            .set_field(field) \
            .set_players(players) \
            .set_last_defense_player_index(last_defense_player_index) \
            .set_vanishing_point_segments(vanishing_point_segments) \
            .build()


class FrameDataPrinter:

    def __init__(self):
        self.frame_printer = utils.FramePrinter()

    def print(self, frame_data, frame, print_field, print_players_and_referees, print_vanishing_point_segments):
        frame_number = frame_data.get_frame_number()
        field = frame_data.get_field()
        players_and_referees = frame_data.get_players()
        last_defense_player_index = frame_data.get_last_defense_player_index()
        vanishing_point_segments = frame_data.get_vanishing_point_segments()
        vanishing_point = frame_data.get_vanishing_point()

        self.frame_printer.print_text(frame, "Frame: {}".format(frame_number), (5, 30), constants.BGR_WHITE)

        if print_field and field is not None:
            vertices = numpy.array(field.get_vertices())
            cv2.polylines(frame, [vertices], True, colors.FIELD_BOX_COLOR, thickness=2)

        if print_players_and_referees and players_and_referees is not None:
            player_index = 0
            for player in players_and_referees:
                position = player.get_position()
                cv2.rectangle(frame, position[0], position[1], self._get_player_box_color(player, player_index == last_defense_player_index), 2)
                player_index += 1

        if print_vanishing_point_segments and vanishing_point_segments is not None:
            cv2.line(frame, vanishing_point_segments[0][0], vanishing_point_segments[0][1], colors.VP_SEGMENTS_COLOR, thickness=2)
            cv2.line(frame, vanishing_point_segments[1][0], vanishing_point_segments[1][1], colors.VP_SEGMENTS_COLOR, thickness=2)
            self.frame_printer.print_text(frame, "Vanishing point: {}".format(vanishing_point), (230, 30), constants.BGR_WHITE)

        if vanishing_point is not None and players_and_referees is not None and last_defense_player_index is not None:
            cv2.line(frame, vanishing_point, players_and_referees[last_defense_player_index].get_position()[1], colors.OFFSIDE_LINE_COLOR, thickness=2)

    def _get_player_box_color(self, player, last_defense_player):
        if last_defense_player:
            return colors.TEAM_BOX_COLOR_LAST_DEFENSE.get(player.get_team())
        return colors.TEAM_BOX_COLOR.get(player.get_team()).get(player.get_type())