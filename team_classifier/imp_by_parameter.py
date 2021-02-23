from domain.player import *
from domain.team import *


class ByParameter:
    def __init__(self, **kwargs):
        self.args = kwargs['team_classifier']['by_parameter']

    def classify_teams(self, frame, players: [Player]):
        team = self.args['attacking_team']
        set_attacking_team(team)
