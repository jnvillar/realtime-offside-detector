from player_detector.step import *
from utils.frame_utils import *
from log.logger import *

COLOR_MIN = np.array([20, 0, 0])
COLOR_MAX = np.array([80, 255, 255])


def on_click(event, x, y, flags, arguments):
    if event == cv2.EVENT_LBUTTONDOWN:
        arguments.append((x, y))


class ByColor:

    def __init__(self, **kwargs):
        self.debug = kwargs['debug']
        self.log = Logger(self, LoggingPackage.player_detector)
        self.params = kwargs
        self.init = False
        self.color_one = None
        self.color_two = None

    def get_team_colors(self, original_frame):
        image_name = "choose colors"
        clicks = []
        while len(clicks) < 2:
            cv2.imshow(image_name, original_frame)
            cv2.setMouseCallback(image_name, on_click, clicks)
            cv2.waitKey(0)
        cv2.destroyWindow(image_name)

        clicks = clicks[-2:]

        pixel_one = original_frame[(clicks[0][1], clicks[0][0])]
        pixel_two = original_frame[(clicks[1][1], clicks[1][0])]

        self.color_one = Color('first team color', tuple(pixel_one))
        self.color_two = Color('second team color', tuple(pixel_two))

    def set_team_colors(self):
        team_one.color = tuple([int(v) for v in self.color_one.bgr])
        team_two.color = tuple([int(v) for v in self.color_two.bgr])

    def find_players(self, original_frame):
        if not self.init:
            self.get_team_colors(original_frame)
            self.set_team_colors()
            self.init = True

        blur_image = original_frame
        pipeline: [Step] = self.steps_pre_process()
        for idx, step in enumerate(pipeline):
            blur_image = step.apply(idx, original_frame)

        first_team_mask = blur_image
        pipeline: [Step] = self.steps_players("first team")
        for idx, step in enumerate(pipeline):
            first_team_mask = step.apply(idx, first_team_mask, {
                'color': self.color_one,
            })

        second_team_mask = blur_image
        pipeline: [Step] = self.steps_players("second team")
        for idx, step in enumerate(pipeline):
            second_team_mask = step.apply(idx, second_team_mask, {
                'color': self.color_two,
            })

        contours_players_first_team = detect_contours(first_team_mask, params=self.params)
        contours_players_second_team = detect_contours(second_team_mask, params=self.params)

        fist_team_players = players_from_contours(contours_players_first_team, self.debug, team=team_one)
        second_team_players = players_from_contours(contours_players_second_team, self.debug, team=team_two)
        return fist_team_players + second_team_players

    def step_detection(self, name="detection"):
        return [
            Step(
                "join {}".format(name),
                join_masks, {'label': 'mask'},
                debug=self.debug
            ),
        ]

    def steps_field(self):
        return [
            Step(
                "get green mask",
                color_mask, {'min': COLOR_MIN, 'max': COLOR_MAX},
                debug=self.debug
            ),
            Step(
                "erosion on green mask",
                apply_erosion, {'iterations': 2},
                debug=self.debug
            ),
            Step(
                "closing on green mask",
                morphological_closing, {'percentage_of_frame': 6, 'iterations': 1},
                debug=self.debug
            ),
            Step(
                "fill on green mask",
                fill_contours, {},
                debug=self.debug
            ),
            Step(
                "erosion on green mask again",
                apply_erosion, {'iterations': 2},
                debug=self.debug
            ),
        ]

    def steps_pre_process(self, name="pre-process"):
        return [
            Step(
                "blur {}".format(name),
                apply_blur, {'blur': (5, 5)},
                debug=self.debug
            ),
        ]

    def steps_players(self, name):
        return [
            Step(
                "get color {}".format(name),
                color_mask_hsv, {'label': 'color'},
                debug=self.debug
            ),
            Step(
                "dilatation {}".format(name),
                apply_dilatation, {'iterations': 2},
                debug=self.debug
            ),
            Step(
                "close {}".format(name),
                morphological_closing, {'percentage_of_frame': 3, 'iterations': 1},
                debug=self.debug
            ),
        ]
