from domain.color import *
from domain.player import *
from domain.aspec_ratio import *
from domain.box import *
import log.log as log
import cv2

log = log.Log(None, log.LoggingPackage.player_sorter)


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


def mark_players(original_frame, players: [Player]):
    for idx, player in enumerate(players):
        player_box = player.box()
        cv2.rectangle(original_frame, player_box.down_left, player_box.upper_right, player.team.get_color(), 2)
        cv2.putText(original_frame, str(player_box.get_label()), player_box.down_left, cv2.FONT_HERSHEY_SIMPLEX, 0.8, player.team.get_color(), 2, cv2.LINE_AA)

    return original_frame


def is_area_black(frame, box: Box):
    black_pixels = 0

    for x in range(box.x, box.x + box.w):
        for y in range(box.y, box.y + box.h):
            frame[x][y] = [0, 0, 0]

            if is_pixel_black(frame[x][y]):
                black_pixels += 1

    box_pixels = box.w * box.h

    log.log("black pixels of box", {'black_pixels': black_pixels, 'box_pixels': box_pixels, 'box_label': box.label})

    if black_pixels > (box_pixels * 0.4):
        return True
    return False


def is_pixel_black(pixel):
    if sum(pixel) == 0:
        return True
    return False


def detect_contours_with_params(original_frame, params):
    (contours, hierarchy) = cv2.findContours(original_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    detected_contours = []
    for pic, c in enumerate(contours):

        x, y, w, h = cv2.boundingRect(c)

        if params['percentage_of_frame'] is not None:
            area = cv2.contourArea(c)
            contour_percentage_of_frame = percentage_of_frame(original_frame, area)
            if contour_percentage_of_frame < params['percentage_of_frame']:
                continue

        if params['aspect_ratio'] is not None:
            # Assume player must be more tall than narrow, so, filter the ones that has more width than height
            aspect_ratio = h / w

            if params['aspect_ratio'] == AspectRatio.taller:
                if aspect_ratio < 1:
                    continue

            if params['aspect_ratio'] == AspectRatio.wider:
                if aspect_ratio > 1:
                    continue

            # Assume player bb must be a rectangle, so, the division of larger side / shorter side must be more than 1
            # aspect_ratio = max(w, h) / max(min(w, h), 1)
            # if aspect_ratio < 0.9:
            #     continue

        detected_contours.append([x, y, w, h])

    return detected_contours


def remove_green(original_frame, params):
    frame = remove_color(original_frame, Colors.green.colors)
    return frame


def apply_dilatation(frame, params):
    dilated_frame = cv2.dilate(frame, None, iterations=1)
    return dilated_frame


def apply_erosion(frame, params):
    eroded_frame = cv2.erode(frame, None, iterations=2)
    return eroded_frame


def delete_small_contours(frame, params):
    (contours, hierarchy) = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for pic, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        contour_percentage_of_frame = percentage_of_frame(frame, area)
        if contour_percentage_of_frame < params['percentage_of_frame']:
            cv2.fillPoly(frame, pts=[contour], color=0)
            continue

    return frame


# https://stackoverflow.com/questions/52247821/find-width-and-height-of-rotatedrect
def filter_contours_by_aspect_ratio(frame, params):
    (contours, hierarchy) = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    for pic, c in enumerate(contours):
        rect = cv2.minAreaRect(c)
        (x, y), (w, h), angle = rect
        # Assume player must be more tall than narrow, so, filter the ones that has more width than height

        if w > h:
            cv2.fillPoly(frame, pts=[c], color=0)

        # Assume player bb must be a rectangle, so, the division of larger side / shorter side must be more than 1

        aspect_ratio = max(w, h) / max(min(w, h), 1)
        if aspect_ratio < 0.9:
            cv2.fillPoly(frame, pts=[c], color=0)
            continue

    return frame


# Use "close" morphological operation to close the gaps between contours
# https://stackoverflow.com/questions/18339988/implementing-imcloseim-se-in-opencv
def join_close_contours(original_frame, params):
    frame = cv2.morphologyEx(original_frame, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (6, 6)))
    return frame


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
