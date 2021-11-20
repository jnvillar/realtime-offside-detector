from matplotlib import pyplot as plt
from player_detector.step import *
from utils.frame_utils import *
from log.logger import *


class OtsuPlayerDetector:

    def __init__(self, **kwargs):
        self.debug = kwargs.get('debug', True)
        self.log = Logger(self, LoggingPackage.player_detector)
        self.params = kwargs

    def find_players(self, original_frame):
        mask = self.compute_otsu_mask_shadows(original_frame)
        self.show_mask(mask, original_frame, title='Otsu thresholding on the hue channel with shadow removal')
        ScreenManager.get_manager().show_frame(original_frame, "original")
        cv2.waitKey(0)
        return []

    def compute_otsu_mask_shadows(self, original_frame, shadow_percentile=5):
        image_hls = cv2.cvtColor(original_frame, cv2.COLOR_BGR2HLS)

        hue, lightness, saturation = np.split(image_hls, 3, axis=2)
        hue = hue.reshape((hue.shape[0], hue.shape[1]))

        otsu = cv2.threshold(hue, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        otsu_mask = otsu != 255

        image_lab = cv2.cvtColor(original_frame, cv2.COLOR_BGR2LAB)
        l, a, b = np.split(image_lab, 3, axis=2)
        l = l.reshape((l.shape[0], l.shape[1]))

        shadow_threshold = np.percentile(l.ravel(), q=shadow_percentile)
        shadows_mask = l < shadow_threshold

        mask = otsu_mask ^ shadows_mask

        return mask

    def show_mask(self, mask, image, title='', mask_color=(255, 0, 0)):
        display_image = image.copy()
        display_image[mask != 0] = mask_color
        plt.imshow(display_image)
        plt.title(title)
        plt.axis('off')
        plt.show()

    def find_players2(self, original_frame):
        pipeline: [Step] = self.enhance_contrast()

        enhanced_contrast = original_frame
        for idx, step in enumerate(pipeline):
            enhanced_contrast = step.apply(idx, enhanced_contrast)
            plt.hist(enhanced_contrast.ravel(), 256, [0, 256])
            plt.show()

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
