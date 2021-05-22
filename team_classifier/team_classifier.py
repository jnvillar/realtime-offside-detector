from team_classifier.imp_by_parameter import *
from timer.timer import *
from log.log import *


class TeamClassifier:

    def __init__(self, analytics, **kwargs):
        self.analytics = analytics
        self.log = Log(self, LoggingPackage.team_classifier)
        methods = {
            'by_parameter': ByParameter(**kwargs['by_parameter']),
        }
        self.method = methods['by_parameter']

    def classify_teams(self, frame, players: [Player]):
        self.log.log("classifying teams")
        Timer.start()
        self.method.classify_teams(frame, players)
        elapsed_time = Timer.stop()
        self.log.log("teams classified", {'cost': elapsed_time})
        return players
