import test.test_utils.test_utils as test_utils
import players_detector.players_detector as players_detector
import video_repository.video_repository as video_repository


class PlayerDetectorTests:

    def __init__(self):
        self.test_utils = test_utils.TestUtils("../data.json")
        self.videos_repository = video_repository.VideoRepository()
        self.videos_repository.load_videos("../videos")

    def test_detect_player(self):
        detector = players_detector.PlayerDetector()

        for video_name, video in self.videos_repository.list_videos():
            players = detector.detect_players_in_frame(video.get_next_frame())
            self.check_players(video_name, 0, players)

    def check_players(self, video_name, frame, players):
        players_info = self.test_utils.players_info(video_name, frame)
        print(players_info['amount'], len(players))


if __name__ == '__main__':
    players_detector_tests = PlayerDetectorTests()
    players_detector_tests.test_detect_player()
