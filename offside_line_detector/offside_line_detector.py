from vanishing_point_finder.vanishing_point_finder import *
from orientation_detector.orientation_detector import *
from test.dataset_generator.dataset_generator import *
from test.dataset_generator.domain import *
from field_detector.field_detector import FieldDetector
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


class OffsideLineDetectorResult:
    def __init__(self, video: Video, players: [Player], vanishing_point, field_mask):
        self.video: Video = video
        self.players: [Player] = players
        self.vanishing_point = vanishing_point
        self.field_mask = field_mask


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
        self.screen_manager = ScreenManager.get_manager()
        self.keyboard_manager = KeyboardManager()
        self.log = Logger(self, LoggingPackage.offside_detector)
        self.frame_data_dictionary_mapper = FrameDataDictionaryMapper()
        self.set_teams(kwargs['app']['team_names'])

    def set_teams(self, params):
        team_one.label = params.get(team_one.id, team_one.label)
        team_two.label = params.get(team_two.id, team_two.label)

    def detect_offside_line(self, soccer_video: Video):
        # detect field
        soccer_video, field_mask = self.field_detector.detect_field(soccer_video)
        # get vanishing point
        vanishing_point = self.vanishing_point_finder.find_vanishing_point(soccer_video)
        # find players
        players = self.player_detector.detect_players(soccer_video)
        # track players
        players = self.player_tracker.track_players(soccer_video, players)
        # classify players in teams
        players = self.player_sorter.sort_players(soccer_video, players)
        # detect and attacking team
        players = self.team_classifier.classify_teams(soccer_video, players)
        # detect orientation
        orientation = self.orientation_detector.detect_orientation(soccer_video, vanishing_point)
        # # mark last defending player
        self.player_finder.find_last_defending_player(players, orientation)
        # detect offside line
        offside_line = self.offside_line_drawer.get_offside_line(soccer_video, players, orientation, vanishing_point)
        # dray offside line
        soccer_video = frame_utils.draw_offside_line(soccer_video, offside_line)

        if self.params.get('show_players', False):
            # draw players
            soccer_video = frame_utils.draw_players(soccer_video, players)

        return OffsideLineDetectorResult(
            video=soccer_video,
            players=players,
            vanishing_point=vanishing_point,
            field_mask=field_mask
        )

    def get_video_frame_data(self, video_data_path) -> [FrameData]:
        if self.params.get('compare', False):
            with open(video_data_path, 'r') as file:
                json_data = json.load(file)
                return [
                    self.frame_data_dictionary_mapper
                        .from_dictionary(frame_data_dictionary) for frame_data_dictionary in json_data
                ]
        return []

    def detect_and_draw_offside_line(self, soccer_video: Video, video_data_path):
        video_data = self.get_video_frame_data(video_data_path)
        pause = True

        while True:
            frame = soccer_video.get_next_frame()
            if frame is None:
                break

            if self.params.get('show_original', False):
                self.screen_manager.show_frame(soccer_video.get_current_frame(), 'original')

            Timer.start('detect_offside_line')
            result = self.detect_offside_line(soccer_video)
            elapsed_time = Timer.stop('detect_offside_line')
            self.log.log('offside line detected', {'cost': elapsed_time})

            if self.params.get('show_result', False):
                self.screen_manager.show_frame(result.video.get_current_frame(), 'final result')

            if self.params.get('stop_in_frame', False):
                if self.params['stop_in_frame'] == result.video.get_current_frame_number():
                    pause = True

            if self.params.get('compare', False):
                self.compare(result, video_data)

            pause = self.parse_keyboard_action(pause)

    def compare(self, result: OffsideLineDetectorResult, video_data: [FrameData]):
        detected_frame_data = self.build_frame_data(result)
        real_frame_data = None
        for frame_data in video_data:
            if detected_frame_data.frame_number == frame_data.frame_number:
                real_frame_data = frame_data

        if real_frame_data is None:
            return

        # Todo: Compare
        return

    def build_frame_data(self, result: OffsideLineDetectorResult) -> FrameData:
        builder = FrameDataBuilder()
        builder.set_frame_number(result.video.get_current_frame_number())
        builder.set_players_from_domain_players(result.players)
        builder.set_field_mask(result.field_mask)
        builder.set_vanishing_point(result.vanishing_point)
        return builder.build(all_parameters_set=True)

    def parse_keyboard_action(self, pause):
        if pause:
            key_code = cv2.waitKey(0)
        else:
            key_code = cv2.waitKey(30)

        if self.keyboard_manager.key_was_pressed(key_code, ord('q')):
            # Q key to pause / restart
            pause = not pause
        elif self.keyboard_manager.key_was_pressed(key_code, constants.SPACE_KEY_CODE):
            # SPACE key to move to the next frame and stop
            pause = True
        elif self.keyboard_manager.key_was_pressed(key_code, constants.ESC_KEY_CODE):
            # ESC key to exit
            exit(0)

        return pause
