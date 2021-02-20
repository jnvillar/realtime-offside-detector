from log.log import *
from team_classifier.imp_by_parameter import *


class TeamClassifier:

    def __init__(self, debug: bool = False, **kwargs):
        self.log = Log(self, LoggingPackage.player_sorter)
        self.debug = debug
        self.methods = {
            'by_parameter': ByParameter(**kwargs),
        }

    def classify_teams(self, frame, players: [Player], method='by_parameter'):
        self.methods[method].classify_teams(frame, players)
        return players
