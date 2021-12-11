from utils.frame_utils import *
from timer.timer import *


def transform_gray_scale(x1, x2, y1, y2, pixel):
    pixel_in_0_255 = pixel / 255
    if pixel_in_0_255 < x1:
        return 255 * x1
    if pixel_in_0_255 > x2:
        return 255 * x2
    return (((y2 - y1) / (x2 - x1)) * (pixel_in_0_255 - x1) * 255) + 255 * y1


def filter_grays(min, max, pixel):
    if min <= pixel <= max:
        return pixel
    else:
        if min == 0:
            return 255
        if max == 255:
            return 0


def full_gray(pixel):
    return transform_gray_scale(0, 1, 0, 1, pixel)


def stretch_gray(pixel, low, high):
    pixel = filter_grays(low, high, pixel)
    return transform_pixel_range(pixel, low, high, 0, 255)


def stretch_low(pixel):
    return stretch_gray(pixel, 0, 125)


def stretch_high(pixel):
    return stretch_gray(pixel, 126, 255)


def transform_matrix_range(original_frame, old_min, old_max, new_min=0, new_max=255):
    scale = (new_max - new_min) / (old_max - old_min)
    res = (original_frame - old_min) * scale
    return res.astype(np.uint8)


def transform_pixel_range(value_in_r1, r1_min, r1_max, r2_min, r2_max):
    scale = (r2_max - r2_min) / (r1_max - r1_min)
    return min((value_in_r1 - r1_min) * scale, 255)


class OtsuPlayerDetector:

    def __init__(self, **kwargs):
        self.debug = kwargs.get('debug', True)
        self.log = Logger(self, LoggingPackage.player_detector)
        self.params = kwargs

    def find_players(self, original_frame):
        image_grayscale = cv2.cvtColor(original_frame, cv2.COLOR_BGR2GRAY)

        log_gray_scale = grey_in_range(image_grayscale, {'low': 0, 'high': 130, 'default_values': True})
        low_gray_scale_stretched = transform_matrix_range(log_gray_scale, 0, 130)

        # old_low = apply_linear_function(image_grayscale, {'fn':stretch_low})

        high_gray_scale = grey_in_range(image_grayscale, {'low': 130, 'high': 255})
        high_gray_scale_stretched = transform_matrix_range(high_gray_scale, 130, 255)

        o_low = apply_otsu(low_gray_scale_stretched)
        o_high = apply_otsu(high_gray_scale_stretched)

        open_gray_scale = morphological_opening(image_grayscale, {"element_size": (3, 3)})
        subtraction = image_grayscale - open_gray_scale
        detected_lines = apply_linear_function(subtraction, {'fn': to_mask})
        remove_lines = remove_mask(o_high, {"mask": detected_lines})

        remove_lines = morphological_opening(remove_lines, {'element_size': (5, 5)})

        add_both_otsu = add_mask(negate(o_low), params={'mask': remove_lines})
        add_both_otsu = apply_dilatation(add_both_otsu)
        players = detect_contours(add_both_otsu, params=self.params)

        return players_from_contours(players, self.debug)
