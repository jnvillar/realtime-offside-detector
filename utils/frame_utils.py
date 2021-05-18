from domain.aspec_ratio import *
from domain.player import *
from domain.color import *
from domain.box import *
from utils.math import *
import log.log as log
import cv2

log = log.Log(None, log.LoggingPackage.player_sorter)


def get_h_component(original_frame, params):
    hsv_img = cv2.cvtColor(original_frame, cv2.COLOR_RGB2HSV)
    frame = hsv_img[:, :, 0]
    return frame


def percentage_of_frame(frame, area):
    width, height = len(frame), len(frame[0])
    total_pixels = width * height
    return (area / total_pixels) * 100


def to_hsv(original_frame):
    hsv = cv2.cvtColor(original_frame, cv2.COLOR_BGR2HSV)
    return hsv


def remove_color(frame, colors: [Color]):
    # convert to hsv color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    for color in colors:
        mask = cv2.inRange(hsv, color.lower, color.upper)
        ## mask shows where the green pixels are, so we negate it
        frame = cv2.bitwise_and(frame, frame, mask=~mask)

    return frame


def get_player_histograms(original_frame, players: [Player]):
    player_histograms = []
    for player in players:
        player_histograms.append(get_histogram_one_d(original_frame, player.get_box()))
    return player_histograms


def draw_offside_line(original_frame, offside_line: Line):
    if offside_line is None:
        return original_frame
    cv2.line(original_frame, offside_line.p0, offside_line.p1, (255, 255, 0), 2)
    return original_frame


def draw_players(original_frame, players: [Player]):
    for idx, player in enumerate(players):
        player_box = player.get_box()
        cv2.rectangle(original_frame, player_box.down_left, player_box.upper_right, player.get_color(), 2)
        player_box = player.get_box(focused=True)
        cv2.rectangle(original_frame, player_box.down_left, player_box.upper_right, player.get_color(), 2)
        cv2.putText(original_frame, str(player.get_name()), player_box.down_left, cv2.FONT_HERSHEY_SIMPLEX, 0.5, player.get_label_color(), 2, cv2.LINE_AA)

    return original_frame


def remove_boca(original_frame):
    frame = remove_color(original_frame, ColorRange.green.color_range)
    frame = remove_color(frame, ColorRange.blue.color_range)
    frame = remove_color(frame, ColorRange.yellow.color_range)
    return frame


def get_histogram(frame, box: Box):
    blue_h = [0] * 256
    green_h = [0] * 256
    red_h = [0] * 256

    res = (blue_h, green_h, red_h)

    for x in range(box.x, box.x + box.w):
        for y in range(box.y, box.y + box.h):
            pixel = frame[y][x]
            for idx, color in enumerate(pixel):
                res[idx][color] += 1

    return res


def get_histogram_one_d(frame, box: Box):
    histogram = get_histogram(frame, box)
    return histogram[0] + histogram[1] + histogram[2]


def get_predominant_color(frame, box: Box, colors: [ColorRange]):
    pixels_by_color = {}

    for x in range(box.x, box.x + box.w):
        for y in range(box.y, box.y + box.h):
            pixel_color = get_pixel_color(frame[y][x], colors)
            if pixel_color in pixels_by_color:
                pixels_by_color[pixel_color] += 1
            else:
                pixels_by_color[pixel_color] = 1

    return find_predominant_color(pixels_by_color)


def get_box_mean_color(original_frame, box: Box):
    box_mask = np.zeros(original_frame.shape[:2], np.uint8)
    x, y, w, h = box.x, box.y, box.w, box.h
    box_mask = cv2.rectangle(box_mask, (x, y), (x + w, y + h), (255, 255, 255), -1)
    box_mean_color = cv2.mean(original_frame, mask=box_mask)
    return box_mean_color


def get_pixel_color(pixel, colors_range: [ColorRange]) -> ColorRange:
    distances = {}

    for color_range in colors_range:
        for color in color_range.color_range:
            color_distance = euclidean_distance(pixel[0:3], color.hsv)
            current_distance = distances.get(color_range, None)
            if current_distance is None or current_distance > color_distance:
                distances[color_range] = color_distance

    color_range = None
    value = None
    for k, v in distances.items():
        if color_range is None:
            color_range = k
            value = v
        elif v < value:
            color_range = k
            value = v

    return color_range.color


def find_predominant_color(pixels_by_color) -> Color:
    most_predominant_color = None
    color_amount = 0

    for color, amount in pixels_by_color.items():
        if amount > color_amount:
            most_predominant_color = color
            color_amount = amount

    return most_predominant_color


def sum_black_pixels(frame, box: Box):
    black_pixels = 0

    for x in range(box.x, box.x + box.w):
        for y in range(box.y, box.y + box.h):
            if is_pixel_black(frame[y][x]):
                black_pixels += 1

    return black_pixels


def is_area_black(frame, box: Box):
    black_pixels = sum_black_pixels(frame, box)
    box_pixels = box.w * box.h

    if black_pixels > (box_pixels * 0.48):
        return True
    return False


def paint_boxes(frame, box: [Box]):
    for box in box:
        frame = paint_box(frame, box)
    return frame


def paint_box(frame, box: Box):
    for x in range(box.x, box.x + box.w):
        for y in range(box.y, box.y + box.h):
            frame[y][x] = [0, 0, 0]

    return frame


def is_pixel_black(pixel):
    if sum(pixel) == 0:
        return True
    return False


def mark_contours(original_frame, params):
    contours = detect_contours(original_frame, params)

    for idx, player in enumerate(players_from_contours(contours)):
        player_box = player.get_box()
        cv2.rectangle(original_frame, player_box.down_left, player_box.upper_right, (255, 255, 255), 2)

    return original_frame


def detect_contours(original_frame, params):
    #  cv2.RETR_TREE tells if one contour it's inside other
    #  cv2.RETR_EXTERNAL keeps only parent contours
    (contours, hierarchy) = cv2.findContours(original_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    detected_contours = []
    for idx, c in enumerate(contours):

        x, y, w, h = cv2.boundingRect(c)
        valid_contour = True

        if 'filter_contour_inside_other' in params:
            # If hierarchy[0, idx, 3] is different from -1, then your contour is inside another.
            if params['filter_contour_inside_other'] and hierarchy[0, idx, 3] != -1:
                valid_contour = False

        if 'ignore_contours_smaller_than' in params:
            area = cv2.contourArea(c)
            contour_percentage_of_frame = percentage_of_frame(original_frame, area)
            if contour_percentage_of_frame < params['ignore_contours_smaller_than']:
                valid_contour = False

        if 'ignore_contours_bigger_than' in params:
            area = cv2.contourArea(c)
            contour_percentage_of_frame = percentage_of_frame(original_frame, area)

            if contour_percentage_of_frame > params['ignore_contours_bigger_than']:
                valid_contour = False

        if 'keep_contours_by_aspect_ratio' in params:
            # Assume player must be more tall than narrow, so, filter the ones that has more width than height

            if params['keep_contours_by_aspect_ratio'] == AspectRatio.taller:
                aspect_ratio = h / w
                # keep taller contours h / w >> 1. We dont want boxes that are too thin
                if aspect_ratio < 1.51 or aspect_ratio > 6:
                    valid_contour = False

            if params['keep_contours_by_aspect_ratio'] == AspectRatio.wider:
                aspect_ratio = w / h
                # keep wider contours w / h >> 1. Obs: we dont want boxes that are too wide
                if aspect_ratio < 1.51 or aspect_ratio > 6:
                    valid_contour = False

        if valid_contour:
            detected_contours.append((c, [x, y, w, h]))

    return detected_contours


def remove_green(original_frame, params):
    frame = remove_color(original_frame, ColorRange.green.color_range)
    return frame


def apply_dilatation(frame, params):
    dilated_frame = cv2.dilate(frame, None, iterations=params.get('iterations', 1))
    return dilated_frame


def apply_erosion(frame, params):
    eroded_frame = cv2.erode(frame, None, iterations=params.get('iterations', 1))
    return eroded_frame


def apply_blur(frame, params):
    blurred_frame = cv2.GaussianBlur(frame, params.get('blur', (3, 3)), 0)
    return blurred_frame


def fill_contours(frame, params):
    (contours, hierarchy) = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for pic, contour in enumerate(contours):
        cv2.fillPoly(frame, pts=[contour], color=255)

    return frame


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
    (contours, hierarchy) = cv2.findContours(frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

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


def morphological_opening(original_frame, params):
    frame = cv2.morphologyEx(original_frame, cv2.MORPH_OPEN, cv2.getStructuringElement(
        params.get('element', cv2.MORPH_ELLIPSE),
        params.get('element_size', (6, 6))))
    return frame


# Use "close" morphological operation to close the gaps between contours
# https://stackoverflow.com/questions/18339988/implementing-imcloseim-se-in-opencv
def morphological_closing(original_frame, params):
    frame = cv2.morphologyEx(original_frame, cv2.MORPH_CLOSE, cv2.getStructuringElement(
        params.get('element', cv2.MORPH_ELLIPSE),
        params.get('element_size', (6, 6))))
    return frame


def is_point_in_image(frame, point):
    img_h, img_w = frame.shape[:2]
    return 0 <= point[0] < img_w and 0 <= point[1] < img_h


def get_line_intersection_with_frame(frame, line: Line):
    img_h, img_w = frame.shape[:2]
    intersections_with_frame = []

    frame_limits = [
        Line((0, 0), (0, img_h - 1)),
        Line((0, 0), (img_w - 1, 0)),
        Line((0, img_h - 1), (img_w - 1, img_h - 1)),
        Line((img_w - 1, 0), (img_w - 1, img_h - 1))
    ]

    for image_limit in frame_limits:
        intersection = get_lines_intersection(line, image_limit)
        if is_point_in_image(frame, intersection):
            intersections_with_frame.append(intersection)

    return intersections_with_frame


def show(frame, window_name, window_number):
    frame = cv2.resize(frame, (500, 500))

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


def detect_edges(original_frame, params):
    return cv2.Canny(original_frame, params["threshold1"], params["threshold2"], apertureSize=3)


def gray_scale(original_frame, params):
    frame = cv2.cvtColor(original_frame, cv2.COLOR_BGR2GRAY)
    return frame


def sobel(original_frame, params):
    frame = cv2.Sobel(original_frame, cv2.CV_8U, 1, 0, ksize=-1)
    return frame
