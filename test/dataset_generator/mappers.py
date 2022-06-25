from test.dataset_generator.domain import Field, Player, PlayerType, Team, FrameDataBuilder, Orientation


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

        return frame_data_dictionary

    def from_dictionary(self, dictionary, frame_width, frame_height, play_orientation):
        self._validate_structure(dictionary)
        frame_number = dictionary.get(self.FRAME_FIELD)
        field_vertices = dictionary.get(self.FIELD_FIELD, None)
        players_as_dictionary = dictionary.get(self.PLAYERS_FIELD, None)
        last_defense_player_index = dictionary.get(self.LAST_DEFENSE_PLAYER_INDEX_FIELD, None)
        vanishing_point_segments = dictionary.get(self.VANISHING_POINT_FIELD, None)

        frame_data_builder = FrameDataBuilder().set_frame_number(frame_number)
        if field_vertices is not None:
            # convert points into tuples (they are parsed as lists)
            frame_data_builder.set_field(Field([tuple(vertex) for vertex in field_vertices]))

        if players_as_dictionary is not None:
            frame_data_builder.set_players([self.player_mapper.from_dictionary(player_as_dictionary) for player_as_dictionary in players_as_dictionary])

        if last_defense_player_index is not None:
            frame_data_builder.set_last_defense_player_index(last_defense_player_index)

        if vanishing_point_segments is not None:
            # convert points into tuples (they are parsed as lists)
            frame_data_builder.set_vanishing_point_segments([[tuple(vanishing_point_segments[0][0]), tuple(vanishing_point_segments[0][1])], [tuple(vanishing_point_segments[1][0]), tuple(vanishing_point_segments[1][1])]])

        # width, height and play orientation are given as extra arguments since they are globally (and not per frame) defined on json serialization
        if frame_width is not None:
            frame_data_builder.set_frame_width(frame_width)

        if frame_height is not None:
            frame_data_builder.set_frame_height(frame_height)

        if play_orientation is not None:
            frame_data_builder.set_play_orientation(play_orientation)

        return frame_data_builder.build()

    def _validate_structure(self, dictionary):
        if self.FRAME_FIELD not in dictionary:
            raise ValueError("The given dictionary cannot be mapped to a FrameData object")

#######################################################################################################################


class FrameDatasetDictionaryMapper:

    FRAME_WIDTH_FIELD = "frame_width"
    FRAME_HEIGHT_FIELD = "frame_height"
    PLAY_ORIENTATION_FIELD = "play_orientation"
    FRAMES_FIELD = "frames"

    def __init__(self):
        self.frame_data_mapper = FrameDataDictionaryMapper()

    def to_dictionary(self, frame_data_list):
        frame_width = None if len(frame_data_list) == 0 else frame_data_list[0].get_frame_width()
        frame_height = None if len(frame_data_list) == 0 else frame_data_list[0].get_frame_height()
        play_orientation = None if len(frame_data_list) == 0 else frame_data_list[0].get_play_orientation().name
        frame_data_dictionary_list = [self.frame_data_mapper.to_dictionary(frame_data) for frame_data in frame_data_list]

        frame_dataset_dictionary = {
            self.FRAME_WIDTH_FIELD: frame_width,
            self.FRAME_HEIGHT_FIELD: frame_height,
            self.PLAY_ORIENTATION_FIELD: play_orientation,
            self.FRAMES_FIELD: frame_data_dictionary_list
        }

        return frame_dataset_dictionary

    def from_dictionary(self, dictionary):
        self._validate_structure(dictionary)

        frame_width = dictionary.get(self.FRAME_WIDTH_FIELD)
        frame_height = dictionary.get(self.FRAME_HEIGHT_FIELD)
        play_orientation = Orientation[dictionary.get(self.PLAY_ORIENTATION_FIELD)]
        frame_data_dictionary_list = dictionary.get(self.FRAMES_FIELD)

        return [self.frame_data_mapper.from_dictionary(frame_data_dictionary, frame_width, frame_height, play_orientation) for frame_data_dictionary in frame_data_dictionary_list]

    def _validate_structure(self, dictionary):
        if len(dictionary) != 0 and self._has_missing_key(dictionary):
            raise ValueError("The given dictionary cannot be mapped to a list of FrameData objects")

    def _has_missing_key(self, dictionary):
        return self.FRAME_WIDTH_FIELD not in dictionary or \
               self.FRAME_HEIGHT_FIELD not in dictionary or \
               self.PLAY_ORIENTATION_FIELD not in dictionary or \
               self.FRAMES_FIELD not in dictionary
