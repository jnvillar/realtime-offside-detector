from player_detector.imp_background_subtraction import *
from player_detector.imp_by_color import *
from player_detector.imp_edges import *
from player_detector.imp_adhoc import *
from player_detector.impl_otsu import *
from player_detector.impl_kmeans import *
from player_detector.impl_tophat import *
from domain.player import *
from domain.video import *
from timer.timer import *
from log.logger import *


class PlayerDetector:

    def __init__(self, analytics, **kwargs):
        self.analytics = analytics
        self.log = Logger(self, LoggingPackage.player_detector)

        methods = {
            'background_subtraction': BackgroundSubtractionPlayerDetector(**kwargs['background_subtraction']),
            'edges': EdgesPlayerDetector(**kwargs['edges']),
            'adhoc': AdHoc(**kwargs['adhoc']),
            'by_color': ByColor(**kwargs['by_color']),
            'otsu': OtsuPlayerDetector(**kwargs['otsu']),
            'tophat': TopHatPlayerDetector(**kwargs['tophat']),
            'kmeans': KmeansPlayerDetector(**kwargs['kmeans'])
        }

        self.method = methods[kwargs['method']]
        self.params = kwargs

    def detect_players(self, video: Video) -> [Player]:
        self.log.log("finding players", {"frame": video.get_current_frame_number()})
        Timer.start('finding players')
        detect_every_amount_of_frames = self.params.get('detect_every_amount_of_frames', 1)
        if (
                video.get_current_frame_number() % detect_every_amount_of_frames == 0) or video.get_current_frame_number() < 3:
            players = self.method.find_players(video.get_current_frame())
        else:
            players = []
        elapsed_time = Timer.stop('finding players')
        self.log.log("detected players", {"cost": Timer.format_time(elapsed_time), "amount": len(players), "players": players})
        return players, elapsed_time
