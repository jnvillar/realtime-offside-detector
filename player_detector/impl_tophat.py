from utils.frame_utils import *
from log.logger import *


class TopHatPlayerDetector:

    def __init__(self, **kwargs):
        self.debug = kwargs.get('debug', True)
        self.log = Logger(self, LoggingPackage.player_detector)
        self.params = kwargs

    def find_players(self, original_frame):
        image_grayscale = cv2.cvtColor(original_frame, cv2.COLOR_BGR2GRAY)
        ScreenManager.get_manager().show_frame(image_grayscale, "original gray")

        filterSize = (9, 9)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, filterSize)

        top_hat_gray_scale = cv2.morphologyEx(image_grayscale, cv2.MORPH_TOPHAT, kernel)
        ScreenManager.get_manager().show_frame(top_hat_gray_scale, "top_hat_gray_scale")

        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 1))
        detected_lines = cv2.morphologyEx(top_hat_gray_scale, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)

        diag = np.fliplr(np.diag(np.full(5, 1)))
        vertical_kernel = np.array(diag, dtype=np.uint8)

        detected_vertical_lines = cv2.morphologyEx(top_hat_gray_scale, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
        ScreenManager.get_manager().show_frame(detected_vertical_lines, "detected vertical lines")

        detected_lines = apply_linear_function(detected_lines, {'fn': to_mask})
        mask = apply_linear_function(top_hat_gray_scale, {'fn': to_mask})

        ScreenManager.get_manager().show_frame(detected_lines, "detected_lines")
        ScreenManager.get_manager().show_frame(mask, "mask")

        remove_horizontal_lines = remove_mask(mask, {"mask": detected_lines})
        ScreenManager.get_manager().show_frame(remove_horizontal_lines, "remove detected horizontal lines")
        cv2.waitKey(0)

        ScreenManager.get_manager().show_frame(mask, "mask")

        top_hat_gray_scale = cv2.morphologyEx(original_frame, cv2.MORPH_TOPHAT, kernel, iterations=10)
        ScreenManager.get_manager().show_frame(
            cv2.bitwise_and(top_hat_gray_scale, top_hat_gray_scale, mask=negate(mask)), "magic")

        cv2.waitKey(0)
        return []
