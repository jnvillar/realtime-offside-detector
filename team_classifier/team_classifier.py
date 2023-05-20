from team_classifier.imp_by_parameter import *
from domain.video import *
from timer.timer import *
from log.logger import *


class TeamClassifier:

    def __init__(self, analytics, **kwargs):
        self.analytics = analytics
        self.log = Logger(self, LoggingPackage.team_classifier)
        methods = {
            'by_parameter': ByParameter(**kwargs['by_parameter']),
            'by_ball_detection': ByBallDetection(**kwargs['by_ball_detection'])
        }
        self.method = methods[kwargs["method"]]

    def classify_teams(self, video: Video, players: [Player]):
        self.log.log("classifying teams")
        Timer.start('classifying teams')
        self.method.classify_teams(video, players)
        elapsed_time = Timer.stop('classifying teams')
        self.log.log("teams classified", {'cost': elapsed_time})
        return players
