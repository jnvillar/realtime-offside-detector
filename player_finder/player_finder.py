from domain.orientation import *
from domain.player import *
from log.log import *


class PlayerFinder:

    def __init__(self, debug: bool = False, **kwargs):
        self.log = Log(self, LoggingPackage.player_finder)
        self.debug = debug

    def find_last_defending_player(self, players: [Player], orientation: Orientation):
        self.log.log("finding leftmost player", {"players": players})

        if not players:
            self.log.log("no players to mark", {})
            return

        if orientation == Orientation.left:
            leftmost_player = None
            for player in players:
                if leftmost_player is None:
                    leftmost_player = player
                elif player.get_box().x < leftmost_player.get_box().x:
                    leftmost_player = player
            player = leftmost_player
        else:
            rightmost_player = None
            for player in players:
                if rightmost_player is None:
                    rightmost_player = player
                elif player.get_box().x + player.get_box().w > rightmost_player.get_box().x + rightmost_player.get_box().w:
                    rightmost_player = player
            player = rightmost_player

        self.log.log("player found", {"player": players})
        player.is_last_defending_player = True
        return player
