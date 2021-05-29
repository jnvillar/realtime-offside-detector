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
    MAX_WINDOWS = 50

    @staticmethod
    def initialize(config={}):
        if ScreenManager.INSTANCE is not None:
            raise Exception("You can initialize the screen manager only once. If you want multiple instances consider using the class constructor")
        ScreenManager.INSTANCE = ScreenManager(screen_number=config.get('debug_screen', 0))
        return ScreenManager.INSTANCE

    @staticmethod
    def get_manager():
        # if the screen manager wasn't initialized yet, then we do it with the default arguments
        if ScreenManager.INSTANCE is None:
            ScreenManager.initialize()
        return ScreenManager.INSTANCE

    def __init__(self, screen_number=0):
        """
        Constructor.
        :param screen_number: screen number where images should be printed (default = 0)
        """
        self.nextWindow = 0
        self.screen = self._get_screen_to_use(screen_number)
        self.x_offset, self.y_offset = self._calculate_screen_offsets(screen_number)
        self.window_names = []
        # starting values for window width and height (probably will not be printed in this size, unless the
        # resolution is really big, or if just 1 or 2 windows are printed)
        self.window_width = 1280
        self.window_height = 1100
        self.rows = 1
        # this represents a percentage that is subtracted during resize, to fit the image correctly into the window
        self.frame_height_resize_offset = 10

    def show_frame(self, frame, window_name):
        # existing window
        if window_name in self.window_names:
            frame = cv2.resize(frame, (self.window_width, int(self.window_height * (100 - self.frame_height_resize_offset) / 100)))
            cv2.imshow(window_name, frame)
            return

        # new window
        self.window_names.append(window_name)
        if len(self.window_names) >= self.MAX_WINDOWS:
            # just in case we set a hardcoded limit of windows
            raise Exception("You are trying to print more windows than the max number ({}). Increase the MAX_WINDOWS constant".format(self.MAX_WINDOWS))

        requires_resize = self._calculate_window_dimensions()

        if requires_resize:
            for i in range(0, self.nextWindow):
                x, y = self._get_coordinate_to_print_window(i)
                window_i_name = self.window_names[i]
                cv2.resizeWindow(window_i_name, self.window_width, self.window_height)
                cv2.moveWindow(window_i_name, x, y)

        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        x, y = self._get_coordinate_to_print_window(self.nextWindow)
        frame = cv2.resize(frame, (self.window_width, int(self.window_height * (100 - self.frame_height_resize_offset) / 100)))
        cv2.resizeWindow(window_name, self.window_width, self.window_height)
        cv2.moveWindow(window_name, x, y)
        cv2.imshow(window_name, frame)
        self.nextWindow += 1

    def _get_screen_to_use(self, screen_number):
        available_screens = screeninfo.get_monitors()
        if len(available_screens) <= screen_number:
            available_screens_string = ""
            for screen_id, screen in enumerate(available_screens):
                available_screens_string += "{} : {}\n".format(screen_id, screen.__repr__())
            raise Exception("Screen number {} is not available. Available screens are:\n{}".format(screen_number, available_screens_string))
        return available_screens[screen_number]

    def _get_coordinate_to_print_window(self, window_number):
        windows_per_row = math.floor(self.screen.width / self.window_width)
        window_row = math.floor(window_number / windows_per_row)
        window_column = window_number % windows_per_row
        x = window_column * self.window_width + self.x_offset
        y = window_row * self.window_height - self.y_offset
        return x, y

    def _calculate_window_dimensions(self):
        # percent by which the image is resized, on each step
        decrement_step_pct = 3
        total_windows = len(self.window_names)
        requires_resize = False

        while not self._all_windows_fit_on_screen(total_windows, self.window_width, self.window_height, self.rows):
            if self._all_windows_fit_on_screen(total_windows, self.window_width, self.window_height, self.rows + 1):
                # if adding one more row is enough, it is not necessary to resize the window
                self.rows += 1
            else:
                # calculate the (100 - decrement_step_pct) percent of current dimensions (we keep ratio of the initial values)
                self.window_width = int(self.window_width * (100 - decrement_step_pct) / 100)
                self.window_height = int(self.window_height * (100 - decrement_step_pct) / 100)
                requires_resize = True

        return requires_resize

    def _all_windows_fit_on_screen(self, total_windows, window_width, window_height, rows):
        return self.screen.width >= window_width * math.ceil(total_windows / rows) and self.screen.height >= window_height * rows

    def _calculate_screen_offsets(self, screen_to_use):
        screens = screeninfo.get_monitors()
        screen = screens[screen_to_use]
        # screen that has x = 0 and y = 0
        zero_screen = list(filter(lambda screen: screen.x == 0 and screen.y == 0, screens))[0]
        x_offset = screen.x
        y_offset = screen.height - (zero_screen.height - screen.y)

        return x_offset, y_offset
