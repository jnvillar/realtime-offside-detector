from sklearn.cluster import KMeans
from player_detector.step import *
from timer.timer import *
import matplotlib.pyplot as plt


class KmeansPlayerDetector:

    def __init__(self, **kwargs):
        self.debug = kwargs.get('debug', True)
        self.log = Logger(self, LoggingPackage.player_detector)
        self.params = kwargs
        self.main_colors = None
        self.k_means = KMeans(
            random_state=0,
            n_clusters=self.params.get('klusters', 3)
        )

        self.main_colors_2 = None
        self.k_means_2 = KMeans(
            random_state=0,
            n_clusters=3
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
        self.show_pixels_classification(image, pixel_labels) if self.debug else None

        least_predominant_colors = self.get_least_predominant_colors(image, pixel_labels)

        players_mask = rgb_to_mask(least_predominant_colors.reshape(image.shape))

        ScreenManager.get_manager().show_frame(players_mask, 'players_mask') if self.debug else None

        players_no_lines = remove_mask_2(players_mask, params={"mask": lines})
        ScreenManager.get_manager().show_frame(players_no_lines, 'players_no_lines') if self.debug else None

        pipeline: [Step] = self.step('team_one')
        for idx, step in enumerate(pipeline):
            players_no_lines = step.apply(idx, players_no_lines)

        players = detect_contours(players_no_lines, params=self.params)

        return players_from_contours(players, self.debug)

    def find_players_2(self, original_frame):
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

        team_one = remove_mask_2(team_one, params={"mask": lines})
        ScreenManager.get_manager().show_frame(team_one, "team_one_no_lines") if self.debug else None

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
        return segmented_image

    def step(self, name):
        return [
            Step(
                "open 1 {}".format(name),
                morphological_opening, {
                    'percentage_of_frame': 0.6,
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

    def get_least_predominant_colors(self, image, pixel_labels):
        unique, counts = numpy.unique(pixel_labels, return_counts=True)
        label_count = dict(zip(unique, counts))
        pixels = pixel_labels.flatten()

        colors = np.zeros((len(self.main_colors), 3), np.uint8)

        for i in range(0, self.params.get('least_predominant_colors', 5)):
            least_predominant_color_idx = min(label_count, key=label_count.get)
            label_count.pop(least_predominant_color_idx, None)
            colors[least_predominant_color_idx] = self.main_colors[least_predominant_color_idx]

        segmented_data = colors[pixels]
        segmented_data = segmented_data.reshape(image.shape)
        ScreenManager.get_manager().show_frame(segmented_data, 'least_predominant') if self.debug else None
        return segmented_data

    def get_teams_main_colors(self, pixel_labels):
        unique, counts = numpy.unique(pixel_labels, return_counts=True)
        label_count = dict(zip(unique, counts))

        fist_team_idx = min(label_count, key=label_count.get)
        label_count.pop(fist_team_idx, None)

        second_team_idx = min(label_count, key=label_count.get)
        label_count.pop(second_team_idx, None)

        return self.get_color(fist_team_idx), self.get_color(second_team_idx)

    def get_teams_main_colors(self, pixel_labels):
        unique, counts = numpy.unique(pixel_labels, return_counts=True)
        label_count = dict(zip(unique, counts))

        fist_team_idx = min(label_count, key=label_count.get)
        label_count.pop(fist_team_idx, None)

        second_team_idx = min(label_count, key=label_count.get)
        label_count.pop(second_team_idx, None)

        second_team_idx = min(label_count, key=label_count.get)

        return self.get_color(fist_team_idx), self.get_color(second_team_idx)

    def get_color(self, index):
        res = np.zeros((len(self.main_colors), 3), np.uint8)
        res[index] = self.main_colors[index]
        return res

    def get_pixel_labels(self, image):
        # reshape
        image = image.reshape((-1, 3))

        if self.main_colors is None:
            k_means_result = self.k_means.fit(image)

            # cluster_centers are floats, convert back to int
            self.main_colors = np.uint8(k_means_result.cluster_centers_)
            return k_means_result.labels_
        else:
            return self.k_means.predict(image)

    def get_pixel_labels_2(self, image):
        # to rgb
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # reshape
        image = image.reshape((-1, 3))

        if self.main_colors_2 is None:
            k_means_result = self.k_means_2.fit(image)

            # cluster_centers are floats, convert back to int
            self.main_colors_2 = np.uint8(k_means_result.cluster_centers_)
            return k_means_result.labels_
        else:
            return self.k_means_2.predict(image)

    def calculate_optimal_k(self, image):
        md = []
        min_k = 5
        max_k = 15
        for i in range(min_k, max_k):
            kmeans = KMeans(n_clusters=i)
            kmeans.fit(image)
            o = kmeans.inertia_
            md.append(o)
            print(md)
        print(md)
        plt.plot(list(np.arange(min_k, max_k)), md)
        plt.show()
