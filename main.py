from player_detector.player_detector import *
from player_sorter.player_sorter import *
from domain.video import *
from domain.orientation import *
from orientation_detector.orientation_detector import *
from team_classifier.team_classifier import *
import video_repository.video_repository as video_repository
import utils.constants as constants
import cv2
import utils.frame_utils as frame_utils


class OffsideLineDetector:
    def __init__(self, **kwargs):
        self.player_detector = PlayerDetector(debug=False, **kwargs)
        self.player_sorter = PlayerSorter(**kwargs)
        self.team_detector = TeamClassifier(**kwargs)
        self.orientation_detector = OrientationDetector(**kwargs)

    def detect_offside_line(self, frame, soccer_video):
        frame = cv2.resize(frame, (500, 500))
        # find players
        players = self.player_detector.detect_players_in_frame(frame, soccer_video.get_current_frame_number())
        # classify players
        players = self.player_sorter.sort_players(frame, players)
        # detect and attacking team
        players = self.team_detector.classify_teams(frame, players)
        # detect orientation
        orientation = self.orientation_detector.detect_orientation(frame, players)
        self.player_detector.mark_last_defending_player(players, orientation)
        frame = frame_utils.mark_players(frame, players)
        return frame

    def mark_offside_line(self, soccer_video: Video, stop_in_frame: int = None):
        play = True
        last_frame = False

        while True and not last_frame:
            while play:
                frame = soccer_video.get_next_frame()
                if frame is None:
                    last_frame = True
                    break

                frame = self.detect_offside_line(frame, soccer_video)
                cv2.imshow('final result', frame)

                if stop_in_frame is not None and stop_in_frame == soccer_video.get_current_frame_number():
                    play = not play

                if cv2.waitKey(30) & 0xFF == ord('q'):
                    play = not play

            if cv2.waitKey(30) & 0xFF == ord('q'):
                play = not play


if __name__ == '__main__':

    params = {
        'team_classifier': {  # params for team classifier
            'method': 'by_parameter',
            'by_parameter': {  # params used in by parameter method
                'attacking_team': Team.team_river
            }
        },
        'orientation_detector': {
            'method': 'by_parameter',
            'by_parameter': {  # params used in by parameter method
                'orientation': Orientation.left
            }
        }
    }

    video_path = './test/videos'
    offside_line_detector = OffsideLineDetector(**params)

    while True:
        video = video_repository.VideoRepository.get_video(video_path + '/' + constants.VideoConstants.video_1_from_8_to_12)
        offside_line_detector.mark_offside_line(video, stop_in_frame=65)
