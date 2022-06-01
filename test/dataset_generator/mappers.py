from test.dataset_generator.domain import Field, Player, PlayerType, Team, FrameDataBuilder


class FieldListMapper:

    def to_list(self, field):
        return field.get_vertices()

    def from_list(self, list):
        return Field(list)

#######################################################################################################################


class PlayerDictionaryMapper:

    TYPE_FIELD = "type"
    TEAM_FIELD = "team"
    POSITION_FIELD = "position"

    def to_dictionary(self, player):
        return {
            self.TYPE_FIELD: player.get_type().value,
            self.TEAM_FIELD: player.get_team().value,
            self.POSITION_FIELD: player.get_position()
        }

    def from_dictionary(self, dictionary):
        self._validate_structure(dictionary)
        # for position: convert points into tuples (they are parsed as lists)
        return Player(PlayerType(dictionary[self.TYPE_FIELD]), Team(dictionary[self.TEAM_FIELD]), [tuple(point) for point in dictionary[self.POSITION_FIELD]])

    def _validate_structure(self, dictionary):
        if self.TYPE_FIELD not in dictionary or self.TEAM_FIELD not in dictionary or self.POSITION_FIELD not in dictionary:
            raise ValueError("The given dictionary cannot be mapped to a Player object")

#######################################################################################################################


class FrameDataDictionaryMapper:

    FRAME_FIELD = "frame"
    FIELD_FIELD = "field"
    PLAYERS_FIELD = "players"
    LAST_DEFENSE_PLAYER_INDEX_FIELD = "last_defense_player_index"
    VANISHING_POINT_FIELD = "vanishing_point"
    DEFENDING_TEAM_FIELD = "defending_team"

    def __init__(self):
        self.field_mapper = FieldListMapper()
        self.player_mapper = PlayerDictionaryMapper()

    def to_dictionary(self, frame_data):
        frame_data_dictionary = {
            self.FRAME_FIELD: frame_data.get_frame_number()
        }

        if frame_data.get_field() is not None:
            frame_data_dictionary[self.FIELD_FIELD] = self.field_mapper.to_list(frame_data.get_field())

        if frame_data.get_players() is not None:
            players_list = []
            for player in frame_data.get_players():
                players_list.append(self.player_mapper.to_dictionary(player))
            frame_data_dictionary[self.PLAYERS_FIELD] = players_list

        if frame_data.get_last_defense_player_index() is not None:
            frame_data_dictionary[self.LAST_DEFENSE_PLAYER_INDEX_FIELD] = frame_data.get_last_defense_player_index()

        if frame_data.get_vanishing_point_segments() is not None:
            frame_data_dictionary[self.VANISHING_POINT_FIELD] = frame_data.get_vanishing_point_segments()

        if frame_data.get_defending_team() is not None:
            frame_data_dictionary[self.DEFENDING_TEAM_FIELD] = frame_data.get_defending_team().value

        return frame_data_dictionary

    def from_dictionary(self, dictionary):
        self._validate_structure(dictionary)
        frame_number = dictionary.get(self.FRAME_FIELD)
        field_vertices = dictionary.get(self.FIELD_FIELD, None)
        players_as_dictionary = dictionary.get(self.PLAYERS_FIELD, None)
        last_defense_player_index = dictionary.get(self.LAST_DEFENSE_PLAYER_INDEX_FIELD, None)
        vanishing_point_segments = dictionary.get(self.VANISHING_POINT_FIELD, None)
        defending_team = dictionary.get(self.DEFENDING_TEAM_FIELD, None)

        frame_data_builder = FrameDataBuilder().set_frame_number(frame_number)
        if field_vertices is not None:
            # convert points into tuples (they are parsed as lists)
            frame_data_builder.set_field(Field([tuple(vertex) for vertex in field_vertices]))

        if players_as_dictionary is not None:
            frame_data_builder.set_players([self.player_mapper.from_dictionary(player_as_dictionary) for player_as_dictionary in players_as_dictionary])

        if last_defense_player_index is not None:
            frame_data_builder.set_last_defense_player_index(last_defense_player_index)

        if defending_team is not None:
            frame_data_builder.set_defending_team(Team(defending_team))

        if vanishing_point_segments is not None:
            # convert points into tuples (they are parsed as lists)
            frame_data_builder.set_vanishing_point_segments([[tuple(vanishing_point_segments[0][0]), tuple(vanishing_point_segments[0][1])], [tuple(vanishing_point_segments[1][0]), tuple(vanishing_point_segments[1][1])]])

        return frame_data_builder.build()

    def _validate_structure(self, dictionary):
        if self.FRAME_FIELD not in dictionary:
            raise ValueError("The given dictionary cannot be mapped to a FrameData object")
