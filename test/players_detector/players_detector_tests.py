import test.test_utils.test_utils as test_utils
import player_detector.player_detector as players_detector
import video_repository.video_repository as video_repository
import log.log as log


class PlayerDetectorTests:

    def __init__(self):
        self.test_utils = test_utils.TestUtils("../data.json")
        self.videos_repository = video_repository.VideoRepository("../videos")
        self.log = log.Log(self, log.LoggingPackage.test)

    def test_detect_player(self):
        detector_one = players_detector.PlayerDetector()
        detector_two = players_detector.PlayerDetector()

        for video_name, video in self.videos_repository.list_videos():
            frame = video.get_next_frame()
            detector_one.detect_players(frame)
            detector_two.detect_players_in_frame_2(frame)

            frame = video.get_next_frame()

            players = detector_one.detect_players(frame)
            self.check_players("detect players in frame", video_name, 0, players)

            players = detector_two.detect_players_in_frame_2(frame)
            self.check_players("detect players in frame 2", video_name, 0, players)

    def check_players(self, method, video_name, frame, players_detected):
        players_info = self.test_utils.players_info(video_name, frame)
        self.log.log("result", {
            'video_name': video_name,
            'method': method,
            'amount': players_info['amount'],
            'amount_detected': len(players_detected)
        })


if __name__ == '__main__':
    players_detector_tests = PlayerDetectorTests()
    players_detector_tests.test_detect_player()
