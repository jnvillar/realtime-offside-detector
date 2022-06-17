from enum import Enum

from domain.line import Line
from utils import math


class Team(Enum):
    TEAM_ONE = 1
    TEAM_TWO = 2
    REFEREE = 3

#######################################################################################################################


class PlayerType(Enum):
    FIELD_PLAYER = 1
    GOALKEEPER = 2

#######################################################################################################################


class FrameData:

    def __init__(self, frame_number, players, field, field_mask, last_defense_player_index, vanishing_point_segments, defending_team):
        self.frame_number = self._validate_frame_number(frame_number)
        self.players = players
        self.field = field
        self.field_mask = field_mask
        self.last_defense_player_index = last_defense_player_index
        self.vanishing_point_segments = vanishing_point_segments
        self.vanishing_point = None
        self.defending_team = defending_team

    def get_frame_number(self):
        return self.frame_number

    def get_field(self):
        return self.field

    def get_field_mask(self):
        # TODO: add logic to calculate field mask from self.field
        return self.field_mask

    def get_players(self):
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

    def get_defending_team(self):
        return self.defending_team

    def _validate_frame_number(self, frame_number):
        if frame_number < 1:
            raise ValueError("Frame number must be a positive integer")
        return frame_number

    def _calculate_vanishing_point_from_segments(self):
        if self.vanishing_point_segments is None:
            return None
        p1 = self.vanishing_point_segments[0][0]
        p2 = self.vanishing_point_segments[0][1]
        p3 = self.vanishing_point_segments[1][0]
        p4 = self.vanishing_point_segments[1][1]
        return math.get_lines_intersection(Line(p1, p2), Line(p3, p4))

#######################################################################################################################


class FrameDataBuilder:

    def __init__(self):
        self.frame_number = None
        self.players = None
        self.field = None
        self.field_mask = None
        self.last_defense_player_index = None
        self.vanishing_point_segments = None
        self.defending_team = None

    def set_frame_number(self, frame_number):
        self.frame_number = frame_number
        return self

    def set_players(self, players):
        self.players = players
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

    def set_defending_team(self, defending_team):
        self.defending_team = defending_team
        return self

    def build(self):
        return FrameData(self.frame_number, self.players, self.field, self.last_defense_player_index, self.vanishing_point_segments, self.defending_team)

#######################################################################################################################


class Player:

    def __init__(self, player_type, team, position):
        self.player_type = player_type
        self.team = team
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

    def _to_string(self):
        return "Player(type: {}, team: {}, position: {})".format(self.player_type, self.team, self.position)

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
