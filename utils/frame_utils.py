from domain.color import Color
import cv2


def percentage_of_frame(frame, area):
    width, height = len(frame), len(frame[0])
    total_pixels = width * height
    return (area / total_pixels) * 100


def remove_color(frame, colors: [Color]):
    # convert to hsv color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    for color in colors:
        mask = cv2.inRange(hsv, color.lower, color.upper)
        ## mask shows where the green pixels are, so we negate it
        frame = cv2.bitwise_and(frame, frame, mask=~mask)

    return frame


def apply_dilatation(frame):
    dilated_frame = cv2.dilate(frame, None, iterations=1)
    return dilated_frame


def apply_erosion(frame):
    eroded_frame = cv2.erode(frame, None, iterations=2)
    return eroded_frame


def show(frame, window_name, window_number):
    min_number_to_show = 0
    if window_number < min_number_to_show:
        return

    window_number = window_number - min_number_to_show
    window_name = str(window_number) + " " + window_name
    cv2.imshow(window_name, frame)

    # adjust position of window
    max_windows_in_x_axis = 3
    window_max_x_position = len(frame) * max_windows_in_x_axis

    windows_x_position = window_number * len(frame)
    window_y_position = int(windows_x_position / window_max_x_position)

    if windows_x_position > window_max_x_position - len(frame):
        windows_x_position = windows_x_position - (window_max_x_position * window_y_position)

    cv2.moveWindow(window_name, windows_x_position, (window_y_position * 500))
