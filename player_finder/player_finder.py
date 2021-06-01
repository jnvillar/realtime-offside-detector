from domain.orientation import *
from domain.player import *
from timer.timer import *
from log.logger import *


class PlayerFinder:

    def __init__(self, analytics, **kwargs):
        self.analytics = analytics
        self.args = kwargs
        self.log = Logger(self, LoggingPackage.player_finder)

    def find_last_defending_player(self, players: [Player], orientation: Orientation):
        self.log.log("finding leftmost player", {"players": players})
        Timer.start('finding leftmost player')
        player = self._find_last_defending_player(players, orientation)
        elapsed_time = Timer.stop('finding leftmost player')
        self.log.log("player found", {"cost": elapsed_time, "player": players})
        return player

    def _find_last_defending_player(self, players: [Player], orientation: Orientation):
        if not players:
            self.log.log("no players to mark", {}) if self.args['debug'] else None
            return

        if orientation is None:
            self.log.log("orientation is None", {}) if self.args['debug'] else None
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

        player.is_last_defending_player = True
        return player
