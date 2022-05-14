from enum import Enum


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

    def __init__(self, frame_number, players, field, referees, defending_team):
        self.frame_number = self._validate_frame_number(frame_number)
        self.players = players
        self.field = field
        self.referees = referees
        self.defending_team = defending_team

    def get_frame_number(self):
        return self.frame_number

    def get_field(self):
        return self.field

    def get_players(self):
        return self.players

    def get_referees(self):
        return self.referees

    def get_defending_team(self):
        return self.defending_team

    def _validate_frame_number(self, frame_number):
        if frame_number < 1:
            raise ValueError("Frame number must be a positive integer")
        return frame_number

#######################################################################################################################


class FrameDataBuilder:

    def __init__(self):
        self.frame_number = None
        self.players = None
        self.field = None
        self.referees = None
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

    def set_referees(self, referees):
        self.referees = referees
        return self

    def set_defending_team(self, defending_team):
        self.defending_team = defending_team
        return self

    def build(self):
        return FrameData(self.frame_number, self.players, self.field, self.referees, self.defending_team)

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
