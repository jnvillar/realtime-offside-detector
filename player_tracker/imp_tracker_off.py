from domain.player import *

class OffTracker:

    def track_players(self, frame, players: [Player]):
        # if there are too few players, do not start tracker
        return players
