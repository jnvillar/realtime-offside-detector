import test.test_utils.test_utils as test_utils
import players_detector.players_detector as players_detector


class PlayerDetectorTests:

    def __init__(self):
        self.test_utils = test_utils.TestUtils("../data.json")

    def test_detect_player(self):
        video_path = "../videos/corto.mp4"
        video_name = "corto.mp4"

        video = self.test_utils.load_video(video_path)
        detector = players_detector.PlayerDetector()

        players = detector.detect_players_in_frame(video.get_next_frame())
        self.check_players(video_name, 0, players)

    def check_players(self, video_name, frame, players):
        players_info = self.test_utils.players_info(video_name, frame)
        print(players_info, len(players))


if __name__ == '__main__':
    players_detector_tests = PlayerDetectorTests()
    players_detector_tests.test_detect_player()