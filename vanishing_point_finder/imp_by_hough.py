from player_detector.step import *
from utils.frame_utils import *
from utils.math import *
from log.log import *
import cv2


class ByHough:
    def __init__(self, **kwargs):
        self.log = Log(self, LoggingPackage.vanishing_point)
        self.args = kwargs
        self.vanishing_point = None

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
                sobel, {},
                debug=self.args.get('debug', False)
            )
        ]

    def find_vanishing_point(self, frame, frame_number):

        if self.vanishing_point is not None and frame_number % self.args['calculate_every_x_amount_of_frames'] != 0:
            return self.vanishing_point

        pipeline: [Step] = self.steps()

        for idx, step in enumerate(pipeline):
            frame = step.apply(idx, frame)

        Timer.start()
        lines = cv2.HoughLines(frame, 1, np.pi / 180, 500)
        elapsed_time = Timer.stop()
        self.log.log('Found lines', {'cost': elapsed_time, 'lines': len(lines)}) if self.args['debug'] else None

        parallel_lines = []

        Timer.start()
        for idx, line in enumerate(lines):

            if len(parallel_lines) == 2:
                elapsed_time = Timer.stop()
                self.log.log('Found parallel lines', {'iteration': idx, 'cost': elapsed_time, 'lines': parallel_lines}) if self.args['debug'] else None
                break

            for line_args in line:
                rho, theta = line_args

                if not (len(parallel_lines) == 1 and same_lines((rho, theta), (first_rho, first_theta))):
                    p1, p2 = get_line_points(rho, theta)
                    first_rho, first_theta = rho, theta
                    parallel_lines.append({'p1': p1, 'p2': p2})

                    try:
                        if len(parallel_lines) == 2 and get_lines_intersection(parallel_lines[0], parallel_lines[1])[1] > 0:
                            parallel_lines.pop()
                    except:
                        ## lines are parallel
                        parallel_lines.pop()

        if len(parallel_lines) != 2:
            self.log.log('Could not found two parallel lines', {}) if self.args['debug'] else None
            return None

        if self.args['debug']:
            x1, y1 = parallel_lines[0]['p1']
            x2, y2 = parallel_lines[0]['p2']
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)

            x1, y1 = parallel_lines[1]['p1']
            x2, y2 = parallel_lines[1]['p2']
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)

        self.vanishing_point = get_lines_intersection(parallel_lines[0], parallel_lines[1])
        return self.vanishing_point
