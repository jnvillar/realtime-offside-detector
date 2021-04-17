from domain.orientation import *
from utils.frame_utils import *
from domain.player import *
from timer.timer import *
from log.log import *
import cv2


class OffsideLineDrawer:

    def __init__(self, **kwargs):
        self.log = Log(self, LoggingPackage.offside_line_drawer)
        self.args = kwargs

    def draw_offside_line(self, frame, last_defending_player: Player, orientation: Orientation, vanishing_point):

        self.log.log("drawing offside line")
        Timer.start()
        self._draw_offside_line(frame, last_defending_player, orientation, vanishing_point)
        elapsed_time = Timer.stop()
        self.log.log("offside line draw", {"cost": elapsed_time})

    def _get_player_point(self, last_defending_player: Player, orientation: Orientation):
        player_box = last_defending_player.get_box()
        if orientation is Orientation.right:
            player_point = player_box.upper_right
        else:
            player_point = player_box.upper_left

        if self.args['debug']:
            self.log.log('player point', {'point': player_point})

        return player_point

    def _draw_offside_line(self, frame, last_defending_player: Player, orientation: Orientation, vanishing_point):
        if last_defending_player is None:
            return

        player_point = self._get_player_point(last_defending_player, orientation)
        offside_line = (player_point, vanishing_point)

        self.log.log('offside line', {'offside line': offside_line}) if self.args['debug'] else None

        intersections_with_frame = get_line_intersection_with_frame(frame, offside_line)

        self.log.log('offside line intersection with frame', {'points': intersections_with_frame}) if self.args['debug'] else None

        if len(intersections_with_frame) != 2:
            self.log.log('offside line cant be drawn') if self.args['debug'] else None
            return

        offside_line = (
            (int(intersections_with_frame[0][0]), int(intersections_with_frame[0][1])),
            (int(intersections_with_frame[1][0]), int(intersections_with_frame[1][1]))
        )

        self.log.log('offside line points', {'points': offside_line}) if self.args['debug'] else None

        cv2.line(frame, offside_line[0], offside_line[1], (255, 255, 0), 2)
