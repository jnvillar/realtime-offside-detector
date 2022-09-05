from sklearn.cluster import KMeans
from player_detector.step import *
from timer.timer import *


class KmeansPlayerDetector:

    def __init__(self, **kwargs):
        self.debug = kwargs.get('debug', True)
        self.log = Logger(self, LoggingPackage.player_detector)
        self.params = kwargs
        self.main_colors = None
        self.k_means = KMeans(
            n_clusters=self.params.get('klusters', 3),
            random_state=0
        )

    def find_players(self, original_frame):
        image = original_frame

        lines = get_lines_lsd(image, {'debug': self.debug})
        ScreenManager.get_manager().show_frame(lines, 'lines') if self.debug else None

        image = apply_blur(original_frame, params={'element_size': (5, 5)})
        ScreenManager.get_manager().show_frame(image, 'blured') if self.debug else None

        # image = change_contrast(image)
        # ScreenManager.get_manager().show_frame(image, 'contrast') if self.debug else None

        # classify pixels
        pixel_labels = self.get_pixel_labels(image)
        pixels = pixel_labels.flatten()

        self.show_pixels_classification(image, pixels) if self.debug else None

        first_team_main_color, second_team_main_color = self.get_teams_main_colors(pixel_labels)

        segmented_data = first_team_main_color[pixels]
        team_one = rgb_to_mask(segmented_data.reshape(image.shape))
        ScreenManager.get_manager().show_frame(team_one, 'team_one') if self.debug else None

        ScreenManager.get_manager().show_frame(remove_mask(team_one, params={"mask": lines}),
                                               'team_one_no_lines_bad') if self.debug else None

        team_one = remove_mask_2(team_one, params={"mask": lines})
        ScreenManager.get_manager().show_frame(team_one, 'team_one_no_lines') if self.debug else None

        segmented_data = second_team_main_color[pixels]
        team_two = rgb_to_mask(segmented_data.reshape(image.shape))
        ScreenManager.get_manager().show_frame(team_two, 'team_two') if self.debug else None
        team_two = remove_mask_2(team_two, params={"mask": lines})
        ScreenManager.get_manager().show_frame(team_two, 'team_two_no_lines') if self.debug else None

        pipeline: [Step] = self.step('team_one')
        for idx, step in enumerate(pipeline):
            team_one = step.apply(idx, team_one)

        pipeline: [Step] = self.step('team_two')
        for idx, step in enumerate(pipeline):
            team_two = step.apply(idx, team_two)

        players_team_one = detect_contours(team_one, params=self.params)
        players_team_two = detect_contours(team_two, params=self.params)
        return players_from_contours(players_team_one + players_team_two, self.debug)

    def show_pixels_classification(self, image, pixels):
        # show colors
        segmented_data = self.main_colors[pixels]
        segmented_image = segmented_data.reshape(image.shape)
        ScreenManager.get_manager().show_frame(segmented_image, 'pixels_classification')

    def step(self, name):
        return [
            Step(
                "open 1 {}".format(name),
                morphological_opening, {
                    'percentage_of_frame': 0.5,
                    'iterations': 1
                },
                debug=self.debug
            ),
            Step(
                "close {}".format(name),
                morphological_closing, {
                    'element_size': (5, 30)
                },
                debug=self.debug
            )
        ]

    def get_teams_main_colors(self, pixel_labels):
        unique, counts = numpy.unique(pixel_labels, return_counts=True)
        label_count = dict(zip(unique, counts))

        fist_team_idx = min(label_count, key=label_count.get)
        label_count.pop(fist_team_idx, None)

        second_team_idx = min(label_count, key=label_count.get)

        return self.get_team_color(fist_team_idx), self.get_team_color(second_team_idx)

    def get_team_color(self, index):
        res = np.zeros((len(self.main_colors), 3), np.uint8)
        res[index] = self.main_colors[index]
        return res

    def get_pixel_labels(self, image):
        # to rgb
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # reshape
        image = image.reshape((-1, 3))

        if self.main_colors is None:
            k_means_result = self.k_means.fit(image)

            # cluster_centers are floats, convert back to int
            self.main_colors = np.uint8(k_means_result.cluster_centers_)
            return k_means_result.labels_
        else:
            return self.k_means.predict(image)
