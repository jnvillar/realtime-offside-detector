from enum import Enum


class Team:
    def __init__(self, id, color, label, is_defending=False):
        self.id = id
        self.color = color
        self.label = label
        self.is_defending = is_defending

    def get_color(self):
        return self.color

    def get_label(self):
        attitude = 'def' if self.is_defending else 'atk'
        return self.label + ' ' + attitude

    def __repr__(self):
        return {'name': self.label}


def set_defending_team(defending_team):
    for team in all_teams:
        if defending_team.id == team.id:
            team.is_defending = True
        else:
            team.is_defending = False


def set_attacking_team(attacking_team):
    for team in all_teams:
        if attacking_team.id == team.id:
            team.is_defending = False
        else:
            team.is_defending = True


# blue team
team_one = Team("1️⃣", (255, 0, 0), "1")
# red team
team_two = Team("2️⃣", (0, 0, 255), "2")
# green team
team_three = Team("3️⃣", (0, 255, 0), "3")
team_unclassified = Team("❓", (0, 0, 255), "?")

all_teams = [team_one, team_two, team_unclassified]
