from domain.player import *
import random


def random_classifier(frame, players: [Player]):
    for player in players:
        rand_number = random.randint(1, 2)
        if rand_number == 1:
            player.team = Team.team_one
        else:
            player.team = Team.team_two
    return players
