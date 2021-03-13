import math

import cv2
import screeninfo


class FramePrinter:

    def print_text(self, frame, text, bottom_left_point, color):
        font = cv2.FONT_HERSHEY_DUPLEX
        font_scale = 1
        line_type = 1
        cv2.putText(frame, text, bottom_left_point, font, font_scale, color, line_type)

    def print_multiline_text(self, frame, text_lines, bottom_left_point_first_line, color):
        font = cv2.FONT_HERSHEY_DUPLEX
        font_scale = 0.6
        line_type = 1
        offset = 0
        for line in text_lines:
            cv2.putText(frame, line, (bottom_left_point_first_line[0], bottom_left_point_first_line[1] + offset), font, font_scale, color, line_type)
            offset += 20


class KeyboardManager:

    def key_was_pressed(self, key_code_to_check, expected_key_code):
        return key_code_to_check & 0xFF == expected_key_code

    def is_lowercase_alphabet_char_code(self, key_code):
        return 97 <= key_code <= 122


class ScreenManager:

    INSTANCE = None

    @staticmethod
    def initialize(screen_number=0, max_windows=6, rows=2, show_previous_frame=False):
        if ScreenManager.INSTANCE is not None:
            raise Exception("You can initialize the screen manager only once. If you want multiple instances consider using the class constructor")
        ScreenManager.INSTANCE = ScreenManager(screen_number=screen_number, max_windows=max_windows, rows=rows, show_previous_frame=show_previous_frame)
        return ScreenManager.INSTANCE

    @staticmethod
    def get_manager():
        # if the screen manager wasn't initialized yet, then we do it with the default arguments
        if ScreenManager is None:
            ScreenManager.initialize()
        return ScreenManager.INSTANCE

    def __init__(self, screen_number=0, max_windows=6, rows=2, show_previous_frame=False):
        """
        Constructor.
        :param screen_number: screen number where images should be printed (default = 0)
        :param max_windows: maximum number of windows that we are going to print (default = 6)
        :param rows: rows to use to print all the windows (default = 2)
        :param show_previous_frame: shows the previous frame
        """
        self.nextWindow = 0
        self.screen = self._get_screen_to_use(screen_number)
        self.x_offset, self.y_offset = self._calculate_screen_offsets(screen_number)
        self.max_windows = max_windows
        self.rows = rows
        self.window_height, self.window_width = self._calculate_window_dimensions()
        self.window_names = []
        self.last_frame = None
        self.show_previous_frame = show_previous_frame

    def show_frame(self, frame, window_name, is_previous_frame=False):
        if self.show_previous_frame and \
                self.last_frame is not None \
                and not is_previous_frame:
            self.last_frame = frame
            self.show_frame(self.last_frame, 'last frame', True)

        if self.last_frame is None:
            self.last_frame = frame

        frame = cv2.resize(frame, (self.window_width, self.window_height - 100))

        # existing window
        if window_name in self.window_names:
            cv2.imshow(window_name, frame)
            return

        if len(self.window_names) >= self.max_windows:
            raise Exception("You are trying to print more windows than the predefined number ({}). Increase the max_windows value".format(self.max_windows))

        windows_per_row = math.ceil(self.max_windows / self.rows)
        window_row = math.floor(self.nextWindow / windows_per_row)
        window_column = self.nextWindow % windows_per_row

        x = window_column * self.window_width + self.x_offset
        y = window_row * self.window_height - self.y_offset

        cv2.imshow(window_name, frame)
        cv2.moveWindow(window_name, x, y)
        self.window_names.append(window_name)
        self.nextWindow += 1

    def _get_screen_to_use(self, screen_number):
        available_screens = screeninfo.get_monitors()
        if len(available_screens) <= screen_number:
            available_screens_string = ""
            for screen_id, screen in enumerate(available_screens):
                available_screens_string += "{} : {}\n".format(screen_id, screen.__repr__())
            raise Exception("Screen number {} is not available. Available screens are:\n{}".format(screen_number, available_screens_string))
        return available_screens[screen_number]

    def _calculate_window_dimensions(self):
        # starting values for window width and height (probably will not be printed in this size, unless the
        # resolution is really big)
        current_width = 1280
        current_height = 1100
        # percent by which the image is resized, on each step
        decrement_step_pct = 3

        while self.screen.width < current_width * math.ceil(self.max_windows / self.rows) or self.screen.height < current_height * self.rows:
            # calculate the (100 - decrement_step_pct) percent of current dimensions (we keep ratio of the initial values)
            current_width = int(current_width * (100 - decrement_step_pct) / 100)
            current_height = int(current_height * (100 - decrement_step_pct) / 100)

        return current_height, current_width

    def _calculate_screen_offsets(self, screen_to_use):
        screens = screeninfo.get_monitors()
        screen = screens[screen_to_use]
        # screen that has x = 0 and y = 0
        zero_screen = list(filter(lambda screen: screen.x == 0 and screen.y == 0, screens))[0]
        x_offset = screen.x
        y_offset = screen.height - (zero_screen.height - screen.y)

        return x_offset, y_offset
