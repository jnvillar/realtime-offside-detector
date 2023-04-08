from player_detector.step import *
from utils.frame_utils import *
from timer.timer import *


class OtsuPlayerDetector:

    def __init__(self, **kwargs):
        self.debug = kwargs.get('debug', True)
        self.log = Logger(self, LoggingPackage.player_detector)
        self.params = kwargs

    def fill_with_original(self, streched_with_gaps, mask, original):
        gaps = cv2.bitwise_and(original, negate(mask))
        return streched_with_gaps + gaps

    def find_players(self, original_frame):
        lines = get_lines_lsd(original_frame, self.params | {'dilatation': (10, 10)})
        ScreenManager.get_manager().show_frame(lines, "lines") if self.debug else None

        image_grayscale = gray_scale(original_frame)

        ScreenManager.get_manager().show_frame(image_grayscale, "original") if self.debug else None

        low_gray_scale, low_mask, high_gray_scale, high_mask = grey_in_range(
            image_grayscale,
            {
                'low': 0,
                'high': 125,
                'blacks_defaults_to_high': True,
                'negated_result': True
            }
        )

        ScreenManager.get_manager().show_frame(low_gray_scale, "low") if self.debug else None
        ScreenManager.get_manager().show_frame(high_gray_scale, "high") if self.debug else None

        low_gray_scale_stretched = transform_matrix_gray_range(
            low_gray_scale,
            params={'old_min': 0, 'old_max': 125, 'replace_0': None}
        )

        ## aca habria que llevar los valores que quedaron en 0 a 125

        high_gray_scale_stretched = transform_matrix_gray_range(
            high_gray_scale,
            params={'old_min': 125, 'old_max': 255, 'replace_0': None}
        )

        ## aca habria que llevar los valores que quedaron en 0 a 125

        ScreenManager.get_manager().show_frame(low_gray_scale_stretched, "low stretched") if self.debug else None
        ScreenManager.get_manager().show_frame(high_gray_scale_stretched, "high stretched") if self.debug else None

        # low_gray_scale_stretched = self.fill_with_original(low_gray_scale_stretched, low_mask, image_grayscale)
        # high_gray_scale_stretched = self.fill_with_original(high_gray_scale_stretched, high_mask, image_grayscale)
        #
        # ScreenManager.get_manager().show_frame(low_gray_scale_stretched, "low stretched filled") if self.debug else None
        # ScreenManager.get_manager().show_frame(high_gray_scale_stretched,
        #                                        "high stretched filled") if self.debug else None

        o_low = apply_otsu(low_gray_scale_stretched)
        o_high = apply_otsu(high_gray_scale_stretched)

        ScreenManager.get_manager().show_frame(negate(o_low), "o_low") if self.debug else None
        ScreenManager.get_manager().show_frame(o_high, "o_high") if self.debug else None

        add_both_otsu = add_mask(negate(o_low), params={'mask': o_high})

        add_both_otsu = remove_mask_2(add_both_otsu, params={"mask": lines})
        ScreenManager.get_manager().show_frame(add_both_otsu, "add no lines") if self.debug else None

        add_both_otsu = apply_dilatation(add_both_otsu)

        players = detect_contours(add_both_otsu, params=self.params)
        return players_from_contours(players, self.debug)

    def remove_lines_old(self, o_high, image_grayscale):
        open_gray_scale = morphological_opening(image_grayscale, {"element_size": (3, 3)})
        subtraction = image_grayscale - open_gray_scale
        detected_lines, _ = grey_in_range_to_mask(
            subtraction,
            {
                'max_gray_value': 40,
                'to_value': 255
            }
        )

        remove_lines = remove_mask(o_high, {"mask": detected_lines})
        remove_lines = morphological_opening(remove_lines, {'element_size': (5, 5)})
