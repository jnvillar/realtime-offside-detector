from log.log import *
from team_classifier.imp_by_parameter import *


class TeamClassifier:

    def __init__(self, debug: bool = False, **kwargs):
        self.log = Log(self, LoggingPackage.player_sorter)
        self.debug = debug
        methods = {
            'by_parameter': ByParameter(**kwargs['by_parameter']),
        }
        self.method = methods['by_parameter']

    def classify_teams(self, frame, players: [Player]):
        self.method.classify_teams(frame, players)
        return players
