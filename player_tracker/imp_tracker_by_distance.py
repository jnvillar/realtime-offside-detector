from domain.player import *
from utils.math import *
from log.log import *


def is_new_player(min_distance, player: Player):
    if min_distance > player.get_box().get_width() * 1.5:
        return True
    return False


def find_closest_player(player: Player, players: [Player]):
    min_distance = None
    possible_previous_player = None
    player_center = player.get_box().get_center()
    for previous_player in players:
        previous_player_center = previous_player.get_box().get_center()
        distance = distance_between_points(player_center, previous_player_center)
        if min_distance is None:
            min_distance = distance
            possible_previous_player = previous_player
        elif distance < min_distance:
            min_distance = distance
            possible_previous_player = previous_player
    return min_distance, possible_previous_player


class DistanceTracker:

    def __init__(self, **kwargs):
        self.log = Log(self, LoggingPackage.player_tracker)
        self.previous_players = []
        self.initialized = False
        self.debug = kwargs.get('debug', False)

    def lost_players(self, players: [Player]):
        lost_players = []
        for player in self.previous_players:
            if player.tracking_process_iteration > 1:
                continue

            distance, closest_player = find_closest_player(player, players)
            if is_new_player(distance, player):
                player.tracking_process_iteration += 1
                lost_players.append(player)

        return lost_players

    def track_players(self, frame, players: [Player]):
        # if there are too few players, do not start tracker
        if len(players) > 2 and not self.initialized:
            self.initialized = True
            self.previous_players = players
            return players

        # add lost players first
        tracked_players = players + self.lost_players(players)

        # try to find closest previous player bounding box
        for player in tracked_players:
            distance, closest_player = find_closest_player(player, self.previous_players)

            # if distance is low, previous bb was found, retain player number
            if not is_new_player(distance, player):
                player.number = closest_player.number

        # save info
        self.previous_players = tracked_players

        # return info
        return self.previous_players
