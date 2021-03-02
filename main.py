import video_repository.video_repository as video_repository
from orientation_detector.orientation_detector import *
from player_detector.player_detector import *
from team_classifier.team_classifier import *
from player_tracker.player_tracker import *
from player_sorter.player_sorter import *
from player_finder.player_finder import *
import utils.frame_utils as frame_utils
import utils.constants as constants
from domain.video import *
import cv2


class OffsideLineDetector:
    def __init__(self, **kwargs):
        self.player_detector = PlayerDetector(debug=False, **kwargs['player_detector'])
        self.player_sorter = PlayerSorter(**kwargs['player_sorter'])
        self.team_classifier = TeamClassifier(**kwargs['team_classifier'])
        self.orientation_detector = OrientationDetector(**kwargs['orientation_detector'])
        self.player_tracker = PlayerTracker(**kwargs['player_tracker'])
        self.player_finder = PlayerFinder()
        self.params = kwargs['app']
        self.players = []

    def track_players(self, frame, frame_number):
        frame = cv2.resize(frame, (self.params['size_h'], self.params['size_w']))

        if frame_number < 3 or frame_number % 5 == 0:
            players = self.player_detector.detect_players_in_frame(frame, frame_number)
            self.players = players
            frame = frame_utils.mark_players(frame, players)
            return frame
        else:
            frame = self.player_tracker.track_players(frame, self.players)

        return frame

    def detect_offside_line(self, frame, frame_number):
        frame = cv2.resize(frame, (self.params['size_h'], self.params['size_w']))
        # find players
        players = self.player_detector.detect_players_in_frame(frame, frame_number)
        # classify players
        players = self.player_sorter.sort_players(frame, players)
        # detect and attacking team
        players = self.team_classifier.classify_teams(frame, players)
        # detect orientation
        orientation = self.orientation_detector.detect_orientation(frame, players)

        self.player_finder.mark_last_defending_player(players, orientation)

        frame = frame_utils.mark_players(frame, players)
        return frame

    def mark_offside_line(self, soccer_video: Video):
        play = True
        last_frame = False

        while True and not last_frame:
            while play:
                frame = soccer_video.get_next_frame()
                if frame is None:
                    last_frame = True
                    break

                frame = self.detect_offside_line(frame, soccer_video.get_current_frame_number())
                cv2.imshow('final result', frame)

                stop_in_frame = self.params['stop_in_frame']
                if stop_in_frame is not None and stop_in_frame == soccer_video.get_current_frame_number():
                    play = not play

                if cv2.waitKey(30) & 0xFF == ord('q'):
                    play = not play

            if cv2.waitKey(30) & 0xFF == ord('q'):
                play = not play


if __name__ == '__main__':

    params = {
        'app': {
            'stop_in_frame': 65,
            'size_h': 500,
            'size_w': 500,
        },
        'team_classifier': {  # params for team classifier
            'method': 'by_parameter',
            'by_parameter': {  # params used in by parameter method
                'attacking_team': Team.team_river
            }
        },
        'player_sorter': {
            'method': 'bsas',
        },
        'player_detector': {
            # background_subtraction, edges
            'method': 'edges',
            'background_subtraction': {
                'history': 100,
                'detect_shadows': False,
                'var_threshold': 50,
                'ignore_contours_smaller_than': 0.02,
                'keep_contours_by_aspect_ratio': AspectRatio.taller
            },
            'edges': {
                'threshold1': 50,
                'threshold2': 70,
                'ignore_contours_smaller_than': 0.02,
                'keep_contours_by_aspect_ratio': AspectRatio.taller,
                'filter_contour_inside_other': True
            }
        },
        'orientation_detector': {
            'method': 'by_parameter',
            'by_parameter': {  # params used in by parameter method
                'orientation': Orientation.left
            }
        },
        'player_tracker': {
            'method': 'opencv',
            'opencv': {  # params used in by opencv method
                'tracker': 'kcf'
            }
        }
    }

    video_path = './test/videos'
    offside_line_detector = OffsideLineDetector(**params)

    while True:
        video = video_repository.VideoRepository.get_video(video_path + '/' + constants.VideoConstants.video_1_from_8_to_12)
        offside_line_detector.mark_offside_line(video)
