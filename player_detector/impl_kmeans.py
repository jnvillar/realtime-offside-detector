from sklearn.cluster import KMeans
from player_detector.step import *
from timer.timer import *


class KmeansPlayerDetector:

    def __init__(self, **kwargs):
        self.debug = kwargs.get('debug', True)
        self.log = Logger(self, LoggingPackage.player_detector)
        self.params = kwargs
        self.cluster_centers = None
        self.k_means = KMeans(
            n_clusters=self.params.get('klusters', 3),
            random_state=0
        )

    def find_players(self, original_frame):

        image = apply_blur(original_frame)
        ScreenManager.get_manager().show_frame(image, 'blured') if self.debug else None

        image = change_contrast(image)
        ScreenManager.get_manager().show_frame(image, 'contrast') if self.debug else None

        # to rgb
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # reshape
        vectorized = image.reshape((-1, 3))

        # classify pixels
        pixel_labels = self.get_pixel_labels(vectorized)

        # centers (main_colors) are floats, convert back to int
        main_colors = np.uint8(self.cluster_centers)

        if self.debug:
            # show colors
            segmented_data = main_colors[pixel_labels.flatten()]
            segmented_image = segmented_data.reshape(image.shape)
            ScreenManager.get_manager().show_frame(segmented_image, 'all')

        first_team_main_color, second_team_main_color = self.get_teams_main_colors(main_colors, pixel_labels)

        segmented_data = first_team_main_color[pixel_labels.flatten()]
        team_one = segmented_data.reshape(image.shape)

        segmented_data = second_team_main_color[pixel_labels.flatten()]
        team_two = segmented_data.reshape(image.shape)

        if self.debug:
            # show colors
            ScreenManager.get_manager().show_frame(team_one, 'team_one')
            ScreenManager.get_manager().show_frame(team_two, 'team_two')

        pipeline: [Step] = self.step('team_two')
        for idx, step in enumerate(pipeline):
            team_two = step.apply(idx, team_two)

        pipeline: [Step] = self.step('team_one')
        for idx, step in enumerate(pipeline):
            team_one = step.apply(idx, team_one)

        players_team_one = detect_contours(team_one, params=self.params)
        players_team_two = detect_contours(team_two, params=self.params)
        return players_from_contours(players_team_one + players_team_two, self.debug)

    def step(self, name):
        return [
            Step(
                "gray scale {}".format(name),
                gray_scale,
                debug=self.debug
            ),
            Step(
                "top hat {}".format(name),
                morphological_top_hat, {
                    'element_size': (5, 5),
                    'remove': True
                },
                debug=self.debug
            ),

        ]

    def get_teams_main_colors(self, main_colors, pixel_labels):
        unique, counts = numpy.unique(pixel_labels, return_counts=True)
        label_count = dict(zip(unique, counts))

        fist_team_idx = min(label_count, key=label_count.get)
        label_count.pop(fist_team_idx, None)

        second_team_idx = min(label_count, key=label_count.get)

        return self.get_team_color(main_colors, fist_team_idx), self.get_team_color(main_colors, second_team_idx)

    def get_team_color(self, list, index):
        res = np.zeros((len(list), 3), np.uint8)
        res[index] = list[index]
        return res

    def get_pixel_labels(self, image):
        if self.cluster_centers is None:
            k_means_result = self.k_means.fit(image)
            self.cluster_centers = k_means_result.cluster_centers_
            return k_means_result.labels_
        else:
            return self.k_means.predict(image)
