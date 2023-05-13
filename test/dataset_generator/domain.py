import cv2
import numpy as np

from domain.player import Player as PlayerD
from domain.orientation import Orientation as OrientationD
from enum import Enum
from domain.line import Line
from utils import math, constants


class Player:

    def __init__(self, player_type, team, position):
        self.player_type = player_type
        self.team: Team = team
        self.position = position

    def __str__(self):
        return self._to_string()

    def __repr__(self):
        return self._to_string()

    def get_type(self):
        return self.player_type

    def get_team(self):
        return self.team

    def get_position(self):
        return self.position

    def get_center(self):
        upper_left, down_right = self.position
        width = down_right[0] - upper_left[0]
        height = upper_left[1] - down_right[1]
        center = (upper_left[0] + int(width / 2), upper_left[1] - int(height / 2))
        return center

    def _to_string(self):
        return "Player(type: {}, team: {}, position: {})".format(self.player_type, self.team, self.position)


#######################################################################################################################

class Team(Enum):
    TEAM_ONE = 1
    TEAM_TWO = 2
    REFEREE = 3

    def is_referee(self):
        return self == Team.REFEREE

#######################################################################################################################


class PlayerType(Enum):
    FIELD_PLAYER = 1
    GOALKEEPER = 2


#######################################################################################################################


class Orientation(Enum):
    LEFT = 1
    RIGHT = 2


#######################################################################################################################

class FrameData:

    def __init__(
            self,
            frame_number,
            frame_width,
            frame_height,
            play_orientation,
            players: [Player],
            field,
            field_mask,
            last_defense_player_index,
            vanishing_point_segments=None,
            vanishing_point=None
    ):
        self.frame_number = self._validate_frame_number(frame_number)
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.play_orientation = play_orientation
        self.players: [Player] = players
        self.field = field
        self.field_mask = field_mask
        self.last_defense_player_index = last_defense_player_index
        self.vanishing_point_segments = vanishing_point_segments
        self.vanishing_point = vanishing_point

    def get_frame_number(self):
        return self.frame_number

    def get_field(self):
        return self.field

    def get_field_mask(self):
        if self.field_mask is None:
            # if field is not set, then it's not possible to calculate field mask
            if self.field is not None:
                # if field mask is not defined, calculate it from field vertices
                mask = np.zeros((self.frame_height, self.frame_width), np.uint8)
                vertices = np.array(self.field.get_vertices())
                cv2.fillPoly(mask, [vertices], constants.BGR_WHITE)
                self.field_mask = mask
        return self.field_mask

    def get_defending_team(self):
        return self.players[self.last_defense_player_index].team

    def get_players(self) -> [Player]:
        return self.players

    def get_last_defense_player_index(self):
        return self.last_defense_player_index

    def get_vanishing_point_segments(self):
        return self.vanishing_point_segments

    def get_vanishing_point(self):
        # Lazy calculation of vp from segments
        if self.vanishing_point is None:
            self.vanishing_point = self._calculate_vanishing_point_from_segments()
        return self.vanishing_point

    def get_offside_line(self):
        if self.get_vanishing_point() is not None and self.players is not None and self.last_defense_player_index is not None and self.get_play_orientation is not None:
            last_defense_player_position = self.players[self.last_defense_player_index].get_position()
            # Based on the play orientation use the bottom right or left vertex from the player bounding box as second
            # point of the offside line
            top_left = last_defense_player_position[0]
            bottom_right = last_defense_player_position[1]
            if self.play_orientation == Orientation.RIGHT:
                player_box_vertex = bottom_right
            else:
                bottom_left_x = top_left[0]
                bottom_left_y = bottom_right[1]
                player_box_vertex = (bottom_left_x, bottom_left_y)

            return [self.get_vanishing_point(), player_box_vertex]

    def get_play_orientation(self):
        return self.play_orientation

    def get_frame_width(self):
        return self.frame_width

    def get_frame_height(self):
        return self.frame_height

    def _validate_frame_number(self, frame_number):
        if frame_number < 1:
            raise ValueError("Frame number must be a positive integer")
        return frame_number

    def _calculate_vanishing_point_from_segments(self):
        if self.vanishing_point_segments is None:
            return None
        return math.get_lines_intersection(self.vanishing_point_segments[0], self.vanishing_point_segments[1])


#######################################################################################################################


class FrameDataBuilder:

    def __init__(self):
        self.frame_number = None
        self.frame_width = None
        self.frame_height = None
        self.play_orientation = None
        self.players = None
        self.field = None
        self.field_mask = None
        self.last_defense_player_index = None
        self.vanishing_point_segments = None
        self.vanishing_point = None

    def set_frame_number(self, frame_number):
        self.frame_number = frame_number
        return self

    def set_frame_width(self, frame_width):
        self.frame_width = frame_width
        return self

    def set_frame_height(self, frame_height):
        self.frame_height = frame_height
        return self

    def set_play_orientation(self, play_orientation):
        self.play_orientation = play_orientation
        return self

    def set_play_orientation_from_domain_play_orientation(self, play_orientation: OrientationD):
        if play_orientation == OrientationD.right:
            self.play_orientation = Orientation.RIGHT
        else:
            self.play_orientation = Orientation.LEFT
        return self

    def set_players(self, players):
        self.players = players
        return self

    def set_players_from_domain_players(self, players: [PlayerD]):
        res = []

        for idx, player in enumerate(players):
            if player.is_last_defending_player:
                self.last_defense_player_index = idx

            team = Team.REFEREE
            if player.team.label == "1":
                team = Team.TEAM_ONE
            if player.team.label == "2":
                team = Team.TEAM_TWO

            res.append(
                Player(
                    player_type=PlayerType.FIELD_PLAYER,
                    team=team,
                    position=(
                        player.get_upper_left(),
                        player.get_down_right()
                    )
                )
            )

        self.players = res
        return self

    def set_field(self, field):
        self.field = field
        return self

    def set_field_mask(self, field_mask):
        self.field_mask = field_mask
        return self

    def set_last_defense_player_index(self, last_defense_player_index):
        self.last_defense_player_index = last_defense_player_index
        return self

    def set_vanishing_point_segments(self, vanishing_point_segments):
        self.vanishing_point_segments = vanishing_point_segments
        return self

    def set_vanishing_point(self, vanishing_point):
        self.vanishing_point = vanishing_point
        return self

    def build(self, all_parameters_set=False):
        if all_parameters_set:
            if self.frame_number is None:
                raise Exception("frame number not set")

            if self.frame_width is None:
                raise Exception("frame width not set")

            if self.frame_height is None:
                raise Exception("frame height not set")

            if self.play_orientation is None:
                raise Exception("play orientation not set")

            if self.players is None:
                raise Exception("players not set")

            if self.field is None and self.field_mask is None:
                raise Exception("field or field_mask not set")

            if self.last_defense_player_index is None:
                raise Exception("last_defense_player_index not set")

            if self.vanishing_point_segments is None and self.vanishing_point is None:
                raise Exception("vanishing_point_segments not set")

        return FrameData(
            frame_number=self.frame_number,
            frame_width=self.frame_width,
            frame_height=self.frame_height,
            play_orientation=self.play_orientation,
            players=self.players,
            field=self.field,
            field_mask=self.field_mask,
            last_defense_player_index=self.last_defense_player_index,
            vanishing_point=self.vanishing_point,
            vanishing_point_segments=self.vanishing_point_segments
        )


#######################################################################################################################


class Field:
    MIN_FIELD_VERTICES = 4

    def __init__(self, field_vertices):
        self._validate_min_vertices_number(field_vertices)
        self.field_vertices = field_vertices

    def __str__(self):
        return "Field({})".format(self.field_vertices)

    def get_vertices(self):
        return self.field_vertices

    def _validate_min_vertices_number(self, field_vertices):
        if len(field_vertices) < self.MIN_FIELD_VERTICES:
            raise ValueError("A field requires at least {} vertices".format(self.MIN_FIELD_VERTICES))
