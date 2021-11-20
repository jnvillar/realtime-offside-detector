import sys

from player_detector.step import *
from utils import constants
from utils.frame_utils import *
from domain.video import *
from utils.math import *
from log.logger import *
import cv2

from utils.utils import FramePrinter


class ByHough:

    def __init__(self, **kwargs):
        self.log = Logger(self, LoggingPackage.vanishing_point)
        self.args = kwargs
        self.frame_printer = FramePrinter()
        self.vanishing_point = None
        self.vanishing_point_lines = None
        self.lines = None

    def steps(self):
        return [
            Step(
                "gray scale",
                gray_scale, {},
                debug=self.args.get('debug', False)
            ),
            Step(
                "blur",
                apply_blur, {'blur': (5, 5)},
                debug=self.args.get('debug', False)
            ),
            Step(
                "sobel",
                sobel,
                debug=self.args.get('debug', False)
            ),
            Step(
                "find candidate lines",
                self._find_lines,
                debug=self.args.get('debug', False),
                print_frame_on_debug=False
            ),
            Step(
                "find vp lines",
                self._find_vp_lines,
                debug=self.args.get('debug', False),
                print_frame_on_debug=False
            )
        ]

    def _find_lines(self, frame, params):
        rho = 1
        theta = np.pi / 180
        threshold = 500

        lines = []
        width = frame.shape[1]
        if self.vanishing_point[0] < width * (1 / 3):
            lines = cv2.HoughLines(frame, rho, theta, threshold, min_theta=math.radians(110),
                                   max_theta=math.radians(180))
        elif width * (1 / 3) <= self.vanishing_point[0] < width * (2 / 3):
            part1 = cv2.HoughLines(frame, rho, theta, threshold, min_theta=math.radians(135),
                                   max_theta=math.radians(180))
            part2 = cv2.HoughLines(frame, rho, theta, threshold, min_theta=math.radians(0), max_theta=math.radians(45))
            if part1 is None:
                lines = part2

            if part2 is None:
                lines = part1

            if part1 is not None and part2 is not None:
                lines = np.concatenate([part1, part2])

        else:  # self.vanishing_point[0] >= width * (2/3):
            lines = cv2.HoughLines(frame, rho, theta, threshold, min_theta=math.radians(0), max_theta=math.radians(70))

        if lines is None:
            lines = []

        self.log.log('Found lines', {'lines': len(lines)}) if self.args['debug'] else None
        self.lines = lines

        # to honor the Step contract for the apply method we need to return a frame as result
        return frame

    def _find_vp_lines(self, frame, params):
        # if we don't even find 2 lines, we directly use the previous VP
        frame_width = frame.shape[1]
        total_detected_lines = len(self.lines)
        if total_detected_lines >= 2:
            candidate_vanishing_points = []
            candidate_lines = []
            for line1_idx in range(0, total_detected_lines):
                line1_rho = self.lines[line1_idx][0][0]
                line1_theta = self.lines[line1_idx][0][1]
                line1_p1, line1_p2 = get_line_points(line1_rho, line1_theta)

                # curr = video.get_current_frame()
                # cv2.line(curr, line1_p1, line1_p2, (0, 0, 255), 3)
                # screen_manager.show_frame(curr, "line detected")

                # discard line if it is in the border
                if self._is_border_line(line1_p1, line1_p2, frame_width):
                    continue

                for line2_idx in range(line1_idx + 1, total_detected_lines):
                    line2_rho = self.lines[line2_idx][0][0]
                    line2_theta = self.lines[line2_idx][0][1]
                    line2_p1, line2_p2 = get_line_points(line2_rho, line2_theta)
                    # discard line if it is in the border
                    if self._is_border_line(line2_p1, line2_p2, frame_width):
                        continue

                    # curr = video.get_current_frame()
                    # cv2.line(curr, p1, p2, (0, 0, 255), 3)
                    # screen_manager.show_frame(curr, "line detected")

                    if same_lines((line1_rho, line1_theta), (line2_rho, line2_theta)):
                        continue

                    line1 = Line(line1_p1, line1_p2)
                    line2 = Line(line2_p1, line2_p2)
                    intersection = get_lines_intersection(line1, line2)

                    if intersection is None or intersection[1] > 0:
                        continue

                    candidate_vanishing_points.append(intersection)
                    candidate_lines.append((line1, line2))

            if len(candidate_vanishing_points) == 0:
                self.log.log('Could not find two parallel lines')
            else:
                max_neighbour_distance = 10000
                min_distance = sys.maxsize
                new_vanishing_point = None
                new_vanishing_point_lines = None
                for candidate_idx, candidate in enumerate(candidate_vanishing_points):
                    candidate_distance = math.dist([candidate[0], candidate[1]],
                                                   [self.vanishing_point[0], self.vanishing_point[1]])
                    if candidate_distance < max_neighbour_distance and candidate_distance < min_distance:
                        new_vanishing_point = candidate
                        new_vanishing_point_lines = candidate_lines[candidate_idx]
                        min_distance = candidate_distance

                # if any of the candidates VPs is near enough to the previous VP, then we keep the previous one
                if new_vanishing_point is not None:
                    self.vanishing_point = new_vanishing_point
                    self.vanishing_point_lines = new_vanishing_point_lines

        # to honor the Step contract for the apply method we need to return a frame as result
        return frame

    def find_vanishing_point(self, video: Video):
        # for the first frame, the vanishing point is manually selected
        if self.vanishing_point is None:
            self._manually_select_vanishing_point()
            return self.vanishing_point

        if video.get_current_frame_number() % self.args['calculate_every_x_amount_of_frames'] != 0:
            if self.args['debug']:
                self.log.log('Returning previous vanishing point', {'vanishing_point': self.vanishing_point})

            return self.vanishing_point

        pipeline: [Step] = self.steps()

        frame = video.get_current_frame()
        for idx, step in enumerate(pipeline):
            frame = step.apply(idx, frame)

        if self.args['debug']:
            frame = video.get_current_frame()
            line1 = self.vanishing_point_lines[0]
            line2 = self.vanishing_point_lines[1]
            x1, y1 = line1.p0
            x2, y2 = line1.p1
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
            x1, y1 = line2.p0
            x2, y2 = line2.p1
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
            video.set_frame(frame)
            ScreenManager.get_manager().show_frame(frame, "Lines used for VP calculation")

        return self.vanishing_point

    def _manually_select_vanishing_point(self):
        # temporary hardcode
        line1 = Line((17, 208), (67, 194))
        line2 = Line((318, 509), (455, 451))
        self.vanishing_point = get_lines_intersection(line1, line2)
        self.vanishing_point_lines = (line1, line2)
        return self.vanishing_point

        window_name = "Select field lines"
        frame = video.get_current_frame()
        captured_clicks = []
        arguments = {
            'captured_clicks': captured_clicks,
            'frame': frame,
            'window_name': window_name
        }
        self.frame_printer.print_text(frame, "Select two parallel lines from the field", (5, 30), constants.BGR_WHITE)
        cv2.imshow(window_name, frame)
        cv2.setMouseCallback(window_name, self._click_event, arguments)

        while len(captured_clicks) < 4:
            cv2.waitKey(0)
        cv2.destroyWindow(window_name)

        line1 = Line(captured_clicks[0], captured_clicks[1])
        line2 = Line(captured_clicks[2], captured_clicks[3])
        self.vanishing_point = get_lines_intersection(line1, line2)
        self.vanishing_point_lines = (line1, line2)

    def _click_event(self, event, x, y, flags, arguments):
        if event == cv2.EVENT_LBUTTONUP:
            click_coordinates = (x, y)
            frame = arguments['frame']
            arguments['captured_clicks'].append(click_coordinates)
            self.frame_printer.print_point(frame, click_coordinates, constants.BGR_RED)
            cv2.imshow(arguments['window_name'], frame)

    def _is_border_line(self, p0, p1, frame_width):
        return (p0[0] < 50 and p1[0] < 50) or (p0[0] > frame_width - 50 and p1[0] > frame_width - 50)