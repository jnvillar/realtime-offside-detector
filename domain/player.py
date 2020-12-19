from domain.team import *


class Player:
    def __init__(self, coordinates, team: Team = Team.unclassified):
        self.coordinates = coordinates
        self.team = team
