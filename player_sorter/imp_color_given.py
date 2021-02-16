from domain.player import *
from domain.color import *
import utils.frame_utils as frame_utils


def color_classifier(original_frame, players: [Player], colors: [ColorRange]):
    # these should use colors parameter
    frame = frame_utils.remove_boca(original_frame)

    frame_utils.show(frame, 'remove team colors', 1)

    for player in players:
        if frame_utils.is_area_black(frame, player.get_box()):
            player.team = Team.team_boca
        else:
            player.team = Team.team_river

    return players
