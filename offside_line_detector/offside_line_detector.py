from field_detector.field_detector import FieldDetector
from vanishing_point_finder.vanishing_point_finder import *
from orientation_detector.orientation_detector import *
from offside_line_drawer.offside_line import *
from player_detector.player_detector import *
from team_classifier.team_classifier import *
from player_tracker.player_tracker import *
from player_sorter.player_sorter import *
from player_finder.player_finder import *
import utils.frame_utils as frame_utils
from utils.utils import *
from domain.video import *
import cv2


class OffsideLineDetector:
    def __init__(self, analytics, **kwargs):
        self.analytics = analytics
        self.player_detector = PlayerDetector(analytics, **kwargs['player_detector'])
        self.player_sorter = PlayerSorter(analytics, **kwargs['player_sorter'])
        self.team_classifier = TeamClassifier(analytics, **kwargs['team_classifier'])
        self.orientation_detector = OrientationDetector(analytics, **kwargs['orientation_detector'])
        self.player_tracker = PlayerTracker(analytics, **kwargs['player_tracker'])
        self.player_finder = PlayerFinder(analytics, **kwargs['player_finder'])
        self.vanishing_point_finder = VanishingPointFinder(analytics, **kwargs['vanishing_point_finder'])
        self.offside_line_drawer = OffsideLineDrawer(analytics, **kwargs['offside_line_drawer'])
        self.field_detector = FieldDetector(analytics, **kwargs['field_detector'])
        self.params = kwargs['app']
        self.players = []
        self.screen_manager = ScreenManager(max_windows=1, rows=1)
        self.log = Log(self, LoggingPackage.offside_detector)

    def pre_process(self, original_frame):
        if self.params['resize']['apply']:
            resize_params = self.params['resize']
            frame = cv2.resize(original_frame, (resize_params['size_h'], resize_params['size_w']))
            return frame

        return original_frame

    def detect_offside_line(self, soccer_video: Video):
        # get vanishing point
        vanishing_point = self.vanishing_point_finder.find_vanishing_point(soccer_video)
        # detect field
        soccer_video = self.field_detector.detect_field(soccer_video)
        # find players
        players = self.player_detector.detect_players_in_frame(soccer_video)
        # track players
        players = self.player_tracker.track_players(soccer_video, players)
        # classify players in teams
        players = self.player_sorter.sort_players(soccer_video, players)
        # detect and attacking team
        players = self.team_classifier.classify_teams(soccer_video, players)
        # detect orientation
        orientation = self.orientation_detector.detect_orientation(soccer_video, vanishing_point)
        # mark last defending player
        self.player_finder.find_last_defending_player(players, orientation)
        # draw offside line
        offside_line = self.offside_line_drawer.get_offside_line(soccer_video, players, orientation, vanishing_point)

        soccer_video = frame_utils.draw_offside_line(soccer_video, offside_line)
        soccer_video = frame_utils.draw_players(soccer_video, players)

        return soccer_video

    def detect_and_draw_offside_line(self, soccer_video: Video):
        play = True
        last_frame = False

        while True and not last_frame:
            while play:
                frame = soccer_video.get_next_frame()
                if frame is None:
                    last_frame = True
                    break

                Timer.start()
                soccer_video = self.detect_offside_line(soccer_video)
                elapsed_time = Timer.stop()
                self.log.log('offside line detected', {'cost': elapsed_time})

                if self.params['show_result']:
                    self.screen_manager.show_frame(soccer_video.get_current_frame(), 'final result')

                if self.params['stop_in_frame']:
                    if self.params['stop_in_frame'] == soccer_video.get_current_frame_number():
                        play = not play

                if cv2.waitKey(30) & 0xFF == ord('q'):
                    play = not play

            if cv2.waitKey(30) & 0xFF == ord('q'):
                play = not play
