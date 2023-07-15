from utils.utils import ScreenManager
from player_detector.step import *
from domain.video import *
from timer.timer import *
import numpy as np
import cv2 as cv2

COLOR_MIN = np.array([0, int(0.12 * 255), int(0.27 * 255)])
COLOR_MAX = np.array([int(0.5 * 255), 255, 255])


class FieldDetector:

    def __init__(self, analytics, **kwargs):
        self.analytics = analytics
        self.video = None
        self.debug = kwargs['debug']
        self.method = kwargs['method']
        self.method_implementations = {
            'green_detection': self.by_green_detection,
            'lines_detection': self.by_lines_detection,
            'ground_pixels_detection': self.by_ground_pixels_detection
        }
        self.screen_manager = ScreenManager.get_manager()
        self.log = Logger(self, LoggingPackage.field_detector)

    def print_line(self, rho, theta, color):
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        x1 = int(x0 + 1000 * (-b))
        y1 = int(y0 + 1000 * (a))
        x2 = int(x0 - 1000 * (-b))
        y2 = int(y0 - 1000 * (a))

        cv2.line(self.img, (x1, y1), (x2, y2), color, 1)
        cv2.imshow('img', self.img)
        cv2.waitKey(0)

    def detect_field(self, video: Video):
        Timer.start('detecting field')
        self.video = video
        res = self.method_implementations[self.method]()
        elapsed_time = Timer.stop('detecting field')
        self.log.log("detecting field", {"cost": elapsed_time})
        return res, elapsed_time

    def by_green_detection(self):
        return self.run_steps_pipeline(self.by_green_detection_pipeline())

    def by_ground_pixels_detection(self):
        return self.run_steps_pipeline(self.by_ground_pixels_detection_pipeline())

    def run_steps_pipeline(self, pipeline):
        mask = self.video.get_current_frame()
        for idx, step in enumerate(pipeline):
            mask = step.apply(idx, mask)

        # apply the mask over the frame
        final = cv2.bitwise_and(self.video.get_current_frame(), self.video.get_current_frame(), mask=mask)

        if self.debug:
            self.screen_manager.show_frame(final, "Post field detection")

        self.video.set_frame(final)
        return self.video, mask

    def by_green_detection_pipeline(self):
        return [
            Step(
                "to hsv",
                to_hsv, {},
                debug=self.debug
            ),
            Step(
                "remove green",
                color_mask, {'min': COLOR_MIN, 'max': COLOR_MAX},
                debug=self.debug
            ),
            Step(
                "biggest component mask (1st time)",
                get_biggest_component_mask, {'connectivity': 4},
                debug=self.debug
            ),
            Step(
                "erosion",
                apply_erosion, {'element': cv2.MORPH_RECT, 'element_size': (50, 50)},
                debug=self.debug
            ),
            Step(
                "biggest component mask (2nd time)",
                get_biggest_component_mask, {'connectivity': 8},
                debug=self.debug
            ),
            Step(
                "closing on field",
                morphological_closing, {'element_size': (50, 50), 'element': cv2.MORPH_RECT, 'iterations': 3},
                debug=self.debug
            ),
            Step(
                "dilate on field",
                apply_dilatation, {'element_size': (50, 50), 'element': cv2.MORPH_RECT, 'iterations': 1},
                debug=self.debug
            ),
        ]

    def by_ground_pixels_detection_pipeline(self):
        return [
            # ground pixels detection by using G > R > B rule
            Step(
                "G > R > B mask",
                g_greater_than_r_greater_than_b_mask, {},
                debug=self.debug
            ),
            # dilate with a small structure to remove most of the players black figures
            Step(
                "Minor dilatation",
                apply_dilatation, {'element_size': (15, 15), 'element': cv2.MORPH_RECT},
                debug=self.debug
            ),
            # fill remaining black spots from players over the field, by flooding image
            Step(
                "Fill black spots",
                self.fill_black_spots, {},
                debug=self.debug
            ),
            # erode to remove white holes from the areas out of the field, generated with the first dilatation
            Step(
                "Erode (4 iterations)",
                apply_erosion, {'element_size': (40, 40), 'element': cv2.MORPH_RECT, 'iterations': 4},
                debug=self.debug
            ),
            # dilate again to undo the prior erosion but now we do not have the white holes
            Step(
                "Dilate (3 iterations)",
                apply_dilatation, {'element_size': (50, 50), 'element': cv2.MORPH_RECT, 'iterations': 3},
                debug=self.debug
            )
        ]

    def fill_black_spots(self, original_frame, params):
        # Copy the thresholded image.
        im_floodfill = original_frame.copy()

        # Mask used to flood filling. Notice the size needs to be 2 pixels than the image.
        h, w = im_floodfill.shape[:2]
        mask = np.zeros((h + 2, w + 2), np.uint8)

        # Floodfill from point (0, 0) or the first point from the first column that is black
        x = 0
        y = 0
        while im_floodfill[y][x] != 0 and y < h - 1:
            y = y + 1

        _, _, _, rect = cv2.floodFill(im_floodfill, mask, (x, y), 255)

        # rect return value is the minimum bounding rectangle of the repainted domain
        if rect[2] < w * 0.7:
            # if the repainted domain was too small (width lower than 70% of image width), means that we painted
            # an isolated component from the top left, so we flood again
            while im_floodfill[y][x] != 0 and y < h - 1:
                y = y + 1
            cv2.floodFill(im_floodfill, mask, (x, y), 255)

        # Invert floodfilled image
        im_floodfill_inv = cv2.bitwise_not(im_floodfill)

        # Combine the two images to get the foreground
        im_out = original_frame | im_floodfill_inv

        return im_out

    def by_lines_detection(self):
        img = self.video.get_current_frame()
        hsv_img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        kernel = np.ones((5, 5), np.uint8)
        if self.debug:
            self.screen_manager.show_frame(hsv_img[:, :, 2], "V channel")
        open_img_v = cv2.morphologyEx(hsv_img[:, :, 2], cv2.MORPH_DILATE, kernel)
        # if self.debug:
        #     self.screen_manager.show_frame(open_img_v, "Dilated img V")
        edges_v = cv2.Canny(open_img_v, 10, 30, apertureSize=3)
        edges_v_non_dilated = cv2.Canny(hsv_img[:, :, 2], 10, 30, apertureSize=3)
        if self.debug:
            self.screen_manager.show_frame(edges_v, "Canny V")
            self.screen_manager.show_frame(edges_v_non_dilated, "Canny V non dilated")

        lines = cv2.HoughLines(edges_v_non_dilated, 1, np.pi / 180, 450, min_theta=math.radians(85), max_theta=math.radians(95))
        max_rho = -1
        theta_to_draw = -1
        if lines is not None:
            for line in lines:
                for rho, theta in line:
                    if img.shape[0] / 2 > rho > max_rho:
                        max_rho = rho
                        theta_to_draw = theta

            if max_rho != -1:

                a = np.cos(theta_to_draw)
                b = np.sin(theta_to_draw)
                x0 = a * max_rho
                y0 = b * max_rho
                line_length = 1500
                x1 = int(x0 + line_length * (-b))
                y1 = int(y0 + line_length * (a))
                x2 = int(x0 - line_length * (-b))
                y2 = int(y0 - line_length * (a))

                if self.debug:
                    cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

                offset = 30
                height, width = img.shape[:2]
                int_rho = int(max_rho)
                img_tmp = img[(int_rho - offset):height, :]
                # img = np.zeros((height, width, 3), np.uint8)
                # img[:(int_rho - offset), :] = np.zeros(((int_rho - offset), width, 3), np.uint8)
                # img[(int_rho - offset):height, :] = img_tmp
                img[0:(int_rho - offset), :] = np.zeros(((int_rho - offset), width, 1), np.uint8)

        if self.debug:
            self.screen_manager.show_frame(img, "Field detection")

        self.video.set_frame(img)
        return self.video, img

    #deprecated
    def by_green_detection2(self):
        # green color range in HSV
        COLOR_MIN = np.array([0, int(0.12 * 255), int(0.27 * 255)])
        COLOR_MAX = np.array([int(0.5 * 255), 255, 255])

        # frame converted to hsv
        frame_hsv = cv2.cvtColor(self.video.get_current_frame(), cv2.COLOR_BGR2HSV)

        # create mask which will set as white only pixels that are included in the color range
        green_mask = cv2.inRange(frame_hsv, COLOR_MIN, COLOR_MAX)

        if self.debug:
            self.screen_manager.show_frame(green_mask, "Green mask")

        # search connected components over the mask, and get the biggest one
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(green_mask, connectivity=4)
        biggest_component_label = stats.argmax(axis=0)[cv2.CC_STAT_AREA]

        # get a mask which includes only the biggest component
        biggest_component_mask = np.zeros_like(labels, np.uint8)
        biggest_component_mask[labels == biggest_component_label] = 255

        if self.debug:
            self.screen_manager.show_frame(biggest_component_mask, "Biggest green component mask")

        eroded_label_mask = cv2.morphologyEx(biggest_component_mask, cv2.MORPH_ERODE, cv2.getStructuringElement(cv2.MORPH_RECT, (50, 50)))

        if self.debug:
            self.screen_manager.show_frame(eroded_label_mask, "After erosion")

        # search again for the biggest connected component over the eroded mask
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(eroded_label_mask, connectivity=8)
        biggest_component_label = stats.argmax(axis=0)[cv2.CC_STAT_AREA]

        # get a mask which includes only the biggest component over the eroded mask
        biggest_component_mask = np.zeros_like(labels, np.uint8)
        biggest_component_mask[labels == biggest_component_label] = 255

        if self.debug:
            self.screen_manager.show_frame(biggest_component_mask, "Biggest green component after erosion")

        # apply close operation to remove players from the mask, and then dilate to avoid covering players
        # which are near the field borders
        closed_label_mask = cv2.morphologyEx(biggest_component_mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (50, 50)), iterations=3)
        dilated_label_mask = cv2.morphologyEx(closed_label_mask, cv2.MORPH_DILATE, cv2.getStructuringElement(cv2.MORPH_RECT, (50, 50)), iterations=3)

        if self.debug:
            self.screen_manager.show_frame(dilated_label_mask, "After closing and then dilatation")

        # apply the mask over the frame
        final = cv2.bitwise_and(self.video.get_current_frame(), self.video.get_current_frame(), mask=dilated_label_mask)

        if self.debug:
            self.screen_manager.show_frame(final, "Final")

        self.video.set_frame(final)
        return self.video, dilated_label_mask
