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
        if not players or len(players) == 0:
            self.log.log("no players to mark", {}) if self.args['debug'] else None
            return

        if orientation is None:
            self.log.log("orientation is None", {}) if self.args['debug'] else None
            return

        defending_players = get_defending_players(players)

        if len(defending_players) == 0:
            self.log.log("no defending players", {}) if self.args['debug'] else None
            return

        res = defending_players[0]
        if orientation == Orientation.left:
            for player in defending_players:
                if player.get_box().x < res.get_box().x:
                    res = player
        else:
            for player in defending_players:
                if player.get_box().x + player.get_box().w > res.get_box().x + res.get_box().w:
                    res = player

        res.is_last_defending_player = True
        return res
