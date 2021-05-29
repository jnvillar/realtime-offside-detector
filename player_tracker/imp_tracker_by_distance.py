from domain.player import *
from utils.math import *
from log.logger import *


def has_no_player_close(distance, player: Player):
    if distance > player.get_box().get_width() * 1.2:
        return True
    return False


def has_player_close(distance, player: Player):
    return not has_no_player_close(distance, player)


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
        self.log = Logger(self, LoggingPackage.player_tracker)
        self.previous_players = []
        self.initialized = False
        self.debug = kwargs.get('debug', False)
        self.params = kwargs

    def lost_players(self, players: [Player]):
        lost_players = []
        for player in self.previous_players:
            if player.tracking_process_iteration > self.params.get('history', 3):
                continue

            distance, _ = find_closest_player(player, players)
            # is new player means that nobody is close to him
            if distance is not None and has_no_player_close(distance, player):
                player.tracking_process_iteration += 1
                lost_players.append(player)

        return lost_players

    def restore_player_info(self, detected_player, previous_player):
        detected_player.number = previous_player.number
        detected_player.living_time = previous_player.living_time + 1
        if detected_player.living_time <= self.params.get('team_history', 5):
            detected_player.team = previous_player.team
        else:
            detected_player.living_time = 0

    def track_players(self, frame, players: [Player]):
        # if there are too few players, do not start tracker
        if len(players) > 2 and not self.initialized:
            self.initialized = True
            self.previous_players = players
            return players

        # add lost players first
        current_detected_players = players + self.lost_players(players)
        previous_players = self.previous_players

        # try to find closest previous player bounding box
        for player in current_detected_players:
            distance, closest_player = find_closest_player(player, previous_players)

            # if distance is low, previous bb was found, retain player number and team
            if distance is not None and has_player_close(distance, player):
                self.restore_player_info(player, closest_player)

                new_previous_players = []
                for previous_player in previous_players:
                    if previous_player.number != closest_player.number:
                        new_previous_players.append(previous_player)
                previous_players = new_previous_players

        # save info
        self.previous_players = current_detected_players

        # return info
        return self.previous_players
