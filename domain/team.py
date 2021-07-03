from enum import Enum


class Team:
    def __init__(self, id, color, label, isAttacking=False):
        self.id = id
        self.color = color
        self.label = label
        self.isAttacking = isAttacking

    def get_color(self):
        return self.color

    def get_label(self):
        attitude = 'atk' if self.isAttacking else 'def'
        return self.label + ' ' + attitude

    def __repr__(self):
        return {'name': self.label}


def set_attacking_team(attackingTeam):
    for team in all_teams:
        if attackingTeam.id == team.id:
            team.isAttacking = True
        else:
            team.isAttacking = False


team_one = Team("1️⃣", (255, 0, 0), "1")
team_two = Team("2️⃣", (0, 0, 255), "2")
team_unclassified = Team("❓", (0, 0, 255), "?")

all_teams = [team_one, team_two, team_unclassified]
