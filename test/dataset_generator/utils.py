from test.dataset_generator.domain import FrameDataBuilder


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
        defending_team = old_frame_data.get_defending_team() if new_frame_data.get_defending_team() is None else new_frame_data.get_defending_team()

        return FrameDataBuilder() \
            .set_frame_number(new_frame_data.get_frame_number()) \
            .set_field(field) \
            .set_players(players) \
            .set_last_defense_player_index(last_defense_player_index) \
            .set_defending_team(defending_team) \
            .set_vanishing_point_segments(vanishing_point_segments) \
            .build()
