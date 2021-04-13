from utils.frame_utils import *
from utils.math import *
from log.log import *
import cv2


class ByHough:
    def __init__(self, **kwargs):
        self.log = Log(self, LoggingPackage.vanishing_point)
        self.args = kwargs
        self.vanishing_point = None

    def find_vanishing_point(self, frame, frame_number):

        if self.vanishing_point is not None and frame_number % self.args['calculate_every_x_amount_of_frames'] != 0:
            return self.vanishing_point

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray_frame, (5, 5), 0)
        sobelx = cv2.Sobel(blur, cv2.CV_8U, 1, 0, ksize=-1)
        lines = cv2.HoughLines(sobelx, 1, np.pi / 180, 200)

        parallel_lines = []

        for line in lines:

            if len(parallel_lines) == 2:
                self.log.log('Found paralell lines', {'lines': parallel_lines})
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
            self.log.log('Could not found two parallel lines', {})
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
