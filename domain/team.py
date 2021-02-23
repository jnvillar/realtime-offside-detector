from enum import Enum


class Team(Enum):
    def __init__(self, id, color, label, isAttacking):
        self.id = id
        self.color = color
        self.label = label
        self.isAttacking = isAttacking

    unclassified = "*️⃣", (0, 0, 0), "?", False
    team_one = "1️⃣", (255, 0, 0), "1", False
    team_two = "2️⃣", (0, 0, 255), "2", False
    team_other = "🔟", (0, 255, 0), "3", False

    team_boca = "boca", (255, 0, 0), "boca", False
    team_river = "river", (0, 0, 255), "river", False

    def get_color(self):
        return self.color

    def get_label(self):
        attitude = 'atk' if self.isAttacking else 'def'
        return self.label + ' ' + attitude


def set_attacking_team(attackingTeam):
    for team in Team:
        if attackingTeam.id == team.id:
            team.isAttacking = True
        else:
            team.isAttacking = False
