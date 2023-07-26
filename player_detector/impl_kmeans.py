from sklearn.cluster import KMeans, MiniBatchKMeans
from player_detector.step import *
from timer.timer import *
import matplotlib
import matplotlib.pyplot as plt


class KmeansPlayerDetector:

    def __init__(self, **kwargs):
        self.debug = kwargs.get('debug', False)
        self.log = Logger(self, LoggingPackage.player_detector)
        self.params = kwargs
        self.main_colors = None
        self.k_means = KMeans(
            random_state=0,
            n_clusters=self.params.get('klusters', 3)
        )

    def find_players(self, original_frame):
        # get (i, j) positions of all RGB pixels that are black (i.e. [0, 0, 0])

        if self.params.get('green_background', False):
            black_pixels = np.where(
                (original_frame[:, :, 0] == 0) &
                (original_frame[:, :, 1] == 0) &
                (original_frame[:, :, 2] == 0)
            )

            # set those pixels to white
            original_frame[black_pixels] = [17, 92, 71]

        image = original_frame

        if self.params.get('blur', True):
            image = apply_blur(original_frame, params={'element_size': (5, 5)})

        ScreenManager.get_manager().show_frame(image, 'original') if self.debug else None

        lines = get_lines_lsd(image, self.params)
        ScreenManager.get_manager().show_frame(lines, 'lines') if self.debug else None

        image = remove_mask_2(image, params={"mask": lines})

        # classify pixels
        pixel_labels = self.get_pixel_labels(image)
        self.show_pixels_classification(image, pixel_labels) if self.debug else None

        least_predominant_colors, result = self.get_least_predominant_colors(image, pixel_labels)
        if not result:
            return []

        players_mask = rgb_to_mask(least_predominant_colors.reshape(image.shape))

        ScreenManager.get_manager().show_frame(players_mask, 'players_mask') if self.debug else None

        players = detect_contours(players_mask, params=self.params)

        return players_from_contours(players, self.debug)

    def find_players_3(self, original_frame):
        image = original_frame
        lines = get_lines_lsd(image, {'debug': self.params.get('debug_lines', False)})

        ScreenManager.get_manager().show_frame(lines, 'lines') if self.debug else None

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

    def show_pixels_classification(self, image, pixels):
        # show colors
        segmented_data = self.main_colors[pixels]
        segmented_image = segmented_data.reshape(image.shape)
        ScreenManager.get_manager().show_frame(segmented_image, 'pixels_classification')
        return segmented_image

    def get_least_predominant_colors(self, image, pixel_labels):
        unique, counts = numpy.unique(pixel_labels, return_counts=True)
        label_count = dict(zip(unique, counts))
        pixels = pixel_labels.flatten()

        colors = np.zeros((len(self.main_colors), 3), np.uint8)
        h, w = image.shape[:2]
        amount_of_pixels = h * w

        # keep colors that uses less % of pixels
        for idx, colour_count in label_count.items():
            if colour_count < (amount_of_pixels * self.params.get('color_percentage', None)):
                colors[idx] = self.main_colors[idx]

        if self.debug:
            segmented_data = colors[pixels]
            segmented_data = segmented_data.reshape(image.shape)
            ScreenManager.get_manager().show_frame(segmented_data, 'least_predominant') if self.debug else None

        res = None

        for i, color in enumerate(colors):
            if not color.any():
                continue

            only_that_color = np.zeros((len(self.main_colors), 3), np.uint8)
            only_that_color[i] = color

            image_only_that_color = only_that_color[pixels]
            image_only_that_color = image_only_that_color.reshape(image.shape)

            ScreenManager.get_manager().show_frame(
                image_only_that_color,
                'color {}'.format(color)
            ) if self.debug else None

            image_only_that_color = morphological_closing(image_only_that_color, {'element_size': (1, 20)})
            image_only_that_color = apply_erosion(image_only_that_color, {'element_size': (5, 5)})

            if res is None:
                res = image_only_that_color
            else:
                res = res + image_only_that_color

        if res is None:
            return res, False

        ScreenManager.get_manager().show_frame(res, 'res') if self.debug else None

        return res, True

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
