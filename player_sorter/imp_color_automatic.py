from domain.player import *
from domain.color import *
from log.log import *
import utils.frame_utils as frame_utils


class PlayerSorterByColorAutomatic:
    def __init__(self):
        self.log = Log(self, LoggingPackage.player_sorter)

    def sort_players(self, original_frame, players: [Player]):
        player_by_color = {}

        for color in ColorRange:

            if color.name == ColorRange.green.name:
                continue

            frame = frame_utils.remove_color(original_frame, color.color_range)

            for player in players:
                count_of_colors = player_by_color.get(player, {})
                count_of_colors[color] = frame_utils.sum_black_pixels(frame, player.get_box())
                player_by_color[player] = count_of_colors

        for player, player_colors in player_by_color.items():
            player.color = predominant_color(player_colors)

        return players


def predominant_color(player_by_color):
    player_color = None
    player_color_amount = -1

    for color, amount in player_by_color.items():
        if amount > player_color_amount:
            player_color = color
            player_color_amount = amount

    return player_color
