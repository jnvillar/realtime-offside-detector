from domain.orientation import *
from utils.frame_utils import *
from domain.player import *
from domain.line import *
from timer.timer import *
from log.log import *
import cv2


class OffsideLineDrawer:

    def __init__(self, **kwargs):
        self.log = Log(self, LoggingPackage.offside_line_drawer)
        self.args = kwargs

    def draw_offside_line(self, frame, players: [Player], orientation: Orientation, vanishing_point):
        self.log.log("drawing offside line")
        Timer.start()
        offside_line = self._draw_offside_line(frame, players, orientation, vanishing_point)
        elapsed_time = Timer.stop()
        self.log.log("offside line draw", {"cost": elapsed_time, "offside_line": str(offside_line)})
        return offside_line

    def _get_player_point(self, last_defending_player: Player, orientation: Orientation):
        player_box = last_defending_player.get_box()
        if orientation is Orientation.right:
            player_point = player_box.upper_right
        else:
            player_point = player_box.upper_left

        self.log.log('player point', {'point': player_point}) if self.args['debug'] else None

        return player_point

    def _get_offside_line(self, frame, player_point, vanishing_point):
        offside_line = (player_point, vanishing_point)

        self.log.log('offside line', {'offside line': offside_line}) if self.args['debug'] else None

        intersections_with_frame = get_line_intersection_with_frame(frame, offside_line)

        self.log.log('offside line intersection with frame', {'points': intersections_with_frame}) if self.args['debug'] else None

        if len(intersections_with_frame) != 2:
            self.log.log('offside line cant be drawn') if self.args['debug'] else None
            return

        offside_line = Line(
            (int(intersections_with_frame[0][0]), int(intersections_with_frame[0][1])),
            (int(intersections_with_frame[1][0]), int(intersections_with_frame[1][1]))
        )

        return offside_line

    def _draw_offside_line(self, frame, players: [Player], orientation: Orientation, vanishing_point):
        last_defending_player = get_last_defending_player(players)
        if last_defending_player is None:
            return

        player_point = self._get_player_point(last_defending_player, orientation)
        offside_line = self._get_offside_line(frame, player_point, vanishing_point)
        offside_line = self._adjust_offside_line(frame, players, orientation, offside_line, vanishing_point)

        self.log.log('offside line points', {'points': offside_line}) if self.args['debug'] else None

        cv2.line(frame, offside_line.p0, offside_line.p1, (255, 255, 0), 2)

        return offside_line

    #  checks if any defending player is above offside line
    #  If the line equation is y = ax + b and the coordinates of a point is (x0, y0)
    #  then compare y0 and ax0 + b, for example if y0 > ax0 + b then the point is above the line
    def _adjust_offside_line(self, frame, players: [Player], orientation: Orientation, offside_line: Line, vanishing_point):
        defending_players = get_defending_players(players)
        self.log.log('checking if players are above offside line', {'players': defending_players})
        for player in defending_players:
            player_point = self._get_player_point(player, orientation)
            if is_point_above_line(player_point, offside_line):
                self.log.log('player is above offside line re-calculating', {'players': player, 'offside_line': str(offside_line)})
                offside_line = self._get_offside_line(frame, player_point, vanishing_point)
                cv2.line(frame, offside_line.p0, offside_line.p1, (255, 255, 0), 2)

        return offside_line
