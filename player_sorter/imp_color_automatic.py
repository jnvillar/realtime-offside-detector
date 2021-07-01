import utils.frame_utils as frame_utils
from domain.player import *
from domain.color import *
from log.logger import *
import cv2


class PlayerSorterByColorAutomatic:
    def __init__(self, **kwargs):
        self.log = Logger(self, LoggingPackage.player_sorter)
        self.debug = kwargs.get('debug', False)
        self.params = kwargs

    def get_team_by_color(self, color_name) -> Team:
        return self.params.get(color_name, Team.unclassified)

    def sort_players(self, original_frame, players: [Player]):
        hsv_img = cv2.cvtColor(original_frame, cv2.COLOR_RGB2HSV)
        colors = list(ColorRange)
        for itx, player in enumerate(players):
            player_box = player.get_box(focused=True)
            player_mean_color = frame_utils.get_box_mean_color(hsv_img, player_box)
            player_color = frame_utils.get_pixel_color(player_mean_color, colors)
            player.bgr = player_color
            player.team = self.get_team_by_color(player_color.color_name)

        return players

    def sort_players3(self, original_frame, players: [Player]):
        hsv_frame = frame_utils.to_hsv(original_frame)

        for player in players:
            player_box = player.get_box(focused=True)
            player_color = frame_utils.get_predominant_color(hsv_frame, player_box, list(ColorRange))
            player.bgr = player_color
            player.team = self.get_team_by_color(player_color.color_name)

        return players

    def sort_players2(self, original_frame, players: [Player]):
        player_by_color = {}

        for color in ColorRange:

            if color.name == ColorRange.green.name:
                continue

            frame = frame_utils.remove_color(original_frame, color.color_range)

            for idx, player in enumerate(players):
                if player.team == Team.unclassified:
                    count_of_colors = player_by_color.get(player, {})
                    count_of_colors[color] = frame_utils.sum_black_pixels(frame, player.get_box(focused=True))
                    player_by_color[player] = count_of_colors

        for player, player_colors in player_by_color.items():
            player_color = predominant_color(player_colors)
            player.team = self.get_team_by_color(player_color.color_name)

        return players


def predominant_color(player_by_color) -> Color:
    player_color = None
    player_color_amount = -1

    for color, amount in player_by_color.items():
        if amount > player_color_amount:
            player_color = color
            player_color_amount = amount

    return player_color
