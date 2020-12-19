from enum import Enum


class Team(Enum):
    def __init__(self, id, color, label):
        self.id = id
        self.color = color
        self.label = label

    unclassified = "*️⃣", (0, 0, 0), "?"
    team_one = "1️⃣", (255, 0, 0), "1"
    team_two = "2️⃣", (0, 0, 255), "2"
    team_other = "🔟", (0, 255, 0), "3"

    def get_color(self):
        return self.color

    def get_label(self):
        return self.label
