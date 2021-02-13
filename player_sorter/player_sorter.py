from video_repository.video_repository import *
from domain.player import *
from domain.color import *
import utils.frame_utils as frame_utils
import random


def random_classifier(frame, players: [Player]):
    for player in players:
        rand_number = random.randint(1, 2)
        if rand_number == 1:
            player.team = Team.team_one
        else:
            player.team = Team.team_two
    return players


def remove_boca(original_frame):
    frame = frame_utils.remove_color(original_frame, Colors.green.colors)
    frame = frame_utils.remove_color(frame, Colors.blue.colors)
    frame = frame_utils.remove_color(frame, Colors.yellow.colors)
    return frame


def color_classifier(original_frame, players: [Player], colors: [Colors]):
    frame = remove_boca(original_frame)

    frame_utils.show(frame, 'remove team colors', 1)

    for player in players:
        if frame_utils.is_area_black(frame, player.box()):
            player.team = Team.team_boca
        else:
            player.team = Team.team_river

    return players


def predominant_color(player_by_color):
    player_color = None
    player_color_amount = -1

    for color, amount in player_by_color.items():
        if amount > player_color_amount:
            player_color = color
            player_color_amount = amount

    return player_color


class PlayerSorter:

    def __init__(self, debug: bool = False):
        self.log = log.Log(self, log.LoggingPackage.player_sorter)
        self.debug = debug

    def automatic_color_classifier(self, original_frame, players: [Player]):
        player_by_color = {}

        for color in Colors:

            if color.name == Colors.green.name:
                continue

            frame = frame_utils.remove_color(original_frame, color.color_range)

            for player in players:
                count_of_colors = player_by_color.get(player, {})
                count_of_colors[color] = frame_utils.sum_black_pixels(frame, player.box())
                player_by_color[player] = count_of_colors

        for player, player_colors in player_by_color.items():
            player.color = predominant_color(player_colors)

        self.log.log("count black", {"result": player_by_color})
        return players

    def sort_players(self, frame, players: [Player]):
        sorted_players = self.automatic_color_classifier(frame, players)

        # sorted_players = color_classifier(frame, players, [])
        self.log.log("sorted players", {"players": players})
        return sorted_players
