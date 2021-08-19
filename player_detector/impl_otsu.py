from player_detector.step import *
from utils.frame_utils import *
from log.logger import *


class OtsuPlayerDetector:

    def __init__(self, **kwargs):
        self.debug = kwargs.get('debug', False)
        self.log = Logger(self, LoggingPackage.player_detector)
        self.params = kwargs

    def find_players(self, original_frame):
        pipeline: [Step] = self.enhance_contrast()

        enhanced_contrast = original_frame
        for idx, step in enumerate(pipeline):
            enhanced_contrast = step.apply(idx, enhanced_contrast)

        pipeline = self.otsu("low", 0, 125)
        low_greys_frame = enhanced_contrast
        for idx, step in enumerate(pipeline):
            low_greys_frame = step.apply(idx, enhanced_contrast)

        pipeline = self.otsu("high", 125, 255)
        high_greys_frame = enhanced_contrast
        for idx, step in enumerate(pipeline):
            high_greys_frame = step.apply(idx, enhanced_contrast)

        players_1 = detect_contours(low_greys_frame, params=self.params)
        players_2 = detect_contours(high_greys_frame, params=self.params)

        return players_from_contours(players_1 + players_2, self.debug)

    def otsu(self, name, low, high):
        return [
            Step(
                "otsu {}".format(name),
                apply_otsu, {"low": low, "high": high},
                debug=self.debug),
            Step(
                "dilate {}".format(name),
                apply_dilatation, {'iterations': 1},
                debug=self.debug),
        ]

    def enhance_contrast(self):
        return [
            Step(
                "grey scale",
                gray_scale, {},
                debug=self.debug
            ),
            Step(
                "contrast stretching scale",
                contrast_stretching, {},
                debug=self.debug
            ),
        ]

    def get_otsu_threshold(self, image):
        # Set total number of bins in the histogram
        bins_num = 256

        # Get the image histogram
        hist, bin_edges = np.histogram(image, bins=bins_num)

        # Get normalized histogram if it is required
        if self.params.get('normalized', False):
            hist = np.divide(hist.ravel(), hist.max())

        # Calculate centers of bins
        bin_mids = (bin_edges[:-1] + bin_edges[1:]) / 2.

        # Iterate over all thresholds (indices) and get the probabilities w1(t), w2(t)
        weight1 = np.cumsum(hist)
        weight2 = np.cumsum(hist[::-1])[::-1]

        # Get the class means mu0(t)
        mean1 = np.cumsum(hist * bin_mids) / weight1
        # Get the class means mu1(t)
        mean2 = (np.cumsum((hist * bin_mids)[::-1]) / weight2[::-1])[::-1]

        inter_class_variance = weight1[:-1] * weight2[1:] * (mean1[:-1] - mean2[1:]) ** 2

        # Maximize the inter_class_variance function val
        index_of_max_val = np.argmax(inter_class_variance)

        threshold = bin_mids[:-1][index_of_max_val]
        print("Otsu's algorithm implementation thresholding result: ", threshold)
        return threshold
