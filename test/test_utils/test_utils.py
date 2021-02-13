import video_repository.video_repository as video_repository
import json

data_key = "videos_data"
video_name_key = 'name'
video_data_key = 'data'
video_players_key = 'players'


class TestUtils:

    def __init__(self, config_path):
        with open(config_path) as outfile:
            self.config = json.load(outfile)

    def video_info(self, video_name):
        return next((x for x in self.config[data_key] if x[video_name_key] == video_name), None)

    def players_info(self, video_name, frame):
        video_info = self.video_info(video_name)
        if video_info is None:
            raise Exception("video not found")
        return video_info[video_data_key][frame][video_players_key]

    def load_video(self, video_path):
        videos_repo = video_repository.VideoRepository()
        video = videos_repo.get_video(video_path)
        return video
