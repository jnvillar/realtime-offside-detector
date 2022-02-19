from player_detector.step import *
from utils.frame_utils import *
from timer.timer import *


class OtsuPlayerDetector:

    def __init__(self, **kwargs):
        self.debug = kwargs.get('debug', True)
        self.log = Logger(self, LoggingPackage.player_detector)
        self.params = kwargs

    def find_players(self, original_frame):
        Timer.start('otsu gray scale')
        image_grayscale = gray_scale(original_frame)
        Timer.stop_and_log('otsu gray scale')

        Timer.start('otsu gray in range')
        low_gray_scale, high_gray_scale = grey_in_range(
            image_grayscale,
            {
                'low': 0,
                'high': 130,
                'blacks_defaults_to_high': True,
                'negated_result': True
            }
        )
        Timer.stop_and_log('otsu gray in range')

        Timer.start('otsu stretch gray')
        low_gray_scale_stretched = transform_matrix_gray_range(
            low_gray_scale,
            params={'old_min': 0, 'old_max': 130}
        )

        high_gray_scale_stretched = transform_matrix_gray_range(
            high_gray_scale,
            params={'old_min': 130, 'old_max': 255}
        )
        Timer.stop_and_log('otsu stretch gray')

        Timer.start('apply otsu')
        o_low = apply_otsu(low_gray_scale_stretched)
        o_high = apply_otsu(high_gray_scale_stretched)
        Timer.stop_and_log('apply otsu')

        Timer.start('otsu opening')
        open_gray_scale = morphological_opening(image_grayscale, {"element_size": (3, 3)})
        Timer.stop_and_log('otsu opening')

        Timer.start('otsu substraction')
        subtraction = image_grayscale - open_gray_scale
        Timer.stop_and_log('otsu substraction')

        Timer.start('otsu_lines_high')
        detected_lines, _ = grey_in_range_to_mask(
            subtraction,
            {
                'max_gray_value': 40,
                'to_value': 255
            }
        )
        Timer.stop_and_log('otsu_lines_high')

        Timer.start('otsu morph')
        remove_lines = remove_mask(o_high, {"mask": detected_lines})
        remove_lines = morphological_opening(remove_lines, {'element_size': (5, 5)})
        add_both_otsu = add_mask(negate(o_low), params={'mask': remove_lines})
        add_both_otsu = apply_dilatation(add_both_otsu)
        Timer.stop_and_log('otsu morph')

        players = detect_contours(add_both_otsu, params=self.params)
        return players_from_contours(players, self.debug)
