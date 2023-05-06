from utils.utils import ScreenManager
from sklearn.cluster import KMeans
from PIL import Image, ImageOps
from random import random
from domain.aspec_ratio import *
from domain.player import *
from domain.video import *
from domain.color import *
from domain.box import *
from utils.math import *
import log.logger as log
import colour as cl
import statistics
import cv2

log = log.Logger(None, log.LoggingPackage.player_sorter)

hsv_components = {
    'h': 0,
    's': 1,
    'v': 2,
}


def apply_border(original_frame, params):
    width, height = len(original_frame), len(original_frame[0])
    return original_frame[height:height + 30, width:width + 30]


def get_hsv_component(original_frame, params):
    hsv_img = cv2.cvtColor(original_frame, cv2.COLOR_RGB2HSV)

    frame = hsv_img[:, :, hsv_components[params.get('component', 'h')]]
    return frame


def percentage_of_frame(frame, area):
    width, height = len(frame), len(frame[0])
    total_pixels = width * height
    return (area / total_pixels) * 100


def to_hls(original_frame, params=None):
    hls = cv2.cvtColor(original_frame, cv2.COLOR_BGR2HLS)
    return hls


def to_hsv(original_frame, params=None):
    hsv = cv2.cvtColor(original_frame, cv2.COLOR_BGR2HSV)
    return hsv


def remove_color(frame, colors: [Color]):
    # convert to hsv color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    for color in colors:
        mask = cv2.inRange(hsv, np.array(color.get_hsv_lower()), np.array(color.get_hsv_upper()))
        ## mask shows where the green pixels are, so we negate it
        frame = cv2.bitwise_and(frame, frame, mask=~mask)

    return frame


def get_player_histograms(original_frame, players: [Player]):
    player_histograms = []
    for player in players:
        player_histograms.append(get_histogram_one_d(original_frame, player.get_box()))
    return player_histograms


def draw_offside_line(video: Video, offside_line: Line):
    if offside_line is None:
        return video
    frame = video.get_current_frame()
    cv2.line(frame, offside_line.p0, offside_line.p1, (255, 255, 0), 2)
    return video.set_frame(frame)


def draw_players(video: Video, players: [Player]):
    frame = video.get_current_frame()
    for idx, player in enumerate(players):
        player_box = player.get_box()
        cv2.rectangle(frame, player_box.down_left, player_box.upper_right, player.get_color(), 2)

        ## focused box
        # player_box = player.get_box(focused=True)
        # cv2.rectangle(frame, player_box.down_left, player_box.upper_right, player.get_color(), 2)

        cv2.putText(frame, str(player.get_label()), player_box.down_left, cv2.FONT_HERSHEY_DUPLEX, 0.5,
                    player.get_label_color(), 2, cv2.LINE_AA)

    return video.set_frame(frame)


def calculate_optimal_k(image):
    image = image.reshape((-1, 3))

    inertias = []
    min_k = 2
    max_k = 15

    for i in range(min_k, max_k):
        kmeans = KMeans(n_clusters=i)
        kmeans.fit(image)
        intertia = kmeans.inertia_
        inertias.append(intertia)
        print(intertia)

    return inertias, list(np.arange(min_k, max_k))


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


def get_players_mean_colors(frame, players: [Player], params=None):
    green_mask = g_greater_than_r_greater_than_b_mask(frame, {})

    res = []
    for itx, player in enumerate(players):
        player_box = player.get_box(focused=params.get('focused', False))
        player_mean_color, player_box, player_box_no_green = get_box_mean_color(frame, player_box, green_mask)
        res.append(list(player_mean_color)[0:3])  # [0:3] do not include aplha

    return res


def get_players_median_colors(frame, players: [Player], params=None):
    if params is None:
        params = {}

    res = []
    for itx, player in enumerate(players):
        player_box = player.get_box(focused=params.get('focused', False))
        player_median_color = get_box_median_color(frame, player_box)
        res.append(list(player_median_color))
    return res


def get_box_median_color(original_frame, box: Box):
    a, b, c = [], [], []
    for x in range(box.x, box.x + box.w):
        for y in range(box.y, box.y + box.h):
            pixel = original_frame[y][x]
            a.append(pixel[0])
            b.append(pixel[1])
            c.append(pixel[2])

    return [statistics.median(a), statistics.median(b), statistics.median(c)]


def get_box_mean_color(original_frame, box: Box, green_mask):
    box_mask = np.zeros(original_frame.shape[:2], np.uint8)
    x, y, w, h = box.x, box.y, box.w, box.h
    box_mask = cv2.rectangle(box_mask, (x, y), (x + w, y + h), (255, 255, 255), -1)
    no_green_box = remove_mask_2(box_mask, {'mask': green_mask})
    box_mean_color = cv2.mean(original_frame, mask=no_green_box)
    return box_mean_color, box_mask, no_green_box


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


def crop(original_frame, params):
    height, width = original_frame.shape[:2]

    for x in range(width):
        for y in range(height - 40, height):
            original_frame[y][x] = [0, 0, 0]

    return original_frame


# https://stackoverflow.com/questions/23841852/filtering-lines-and-curves-in-background-subtraction-in-opencv
def get_blobs(thresh, maxblobs, maxmu03, iterations=1):
    """
    Return a 2-tuple list of the locations of large white blobs.
    `thresh` is a black and white threshold image.
    No more than `maxblobs` will be returned.
    Moments with a mu03 larger than `maxmu03` are ignored.
    Before sampling for blobs, the image will be eroded `iterations` times.
    """
    # Kernel specifies an erosion on direct pixel neighbours.
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    # Remove noise and thin lines by eroding/dilating blobs.
    thresh = cv2.erode(thresh, kernel, iterations=iterations)
    thresh = cv2.dilate(thresh, kernel, iterations=iterations - 1)
    ScreenManager.get_manager().show_frame(thresh, 'blob {}'.format(random()))

    # Calculate the centers of the contours.
    contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0]
    moments = map(cv2.moments, contours)

    # Filter out the moments that are too tall.
    moments = filter(lambda k: abs(k['mu03']) <= maxmu03, moments)
    # Select the largest moments.
    moments = sorted(moments, key=lambda k: k['m00'], reverse=True)[:maxblobs]
    # Return the centers of the moments.
    return [(m['m10'] / m['m00'], m['m01'] / m['m00']) for m in moments if m['m00'] != 0]


def find_if_close(cnt1, cnt2):
    row1, row2 = cnt1.shape[0], cnt2.shape[0]
    for i in range(row1):
        for j in range(row2):
            dist = np.linalg.norm(cnt1[i] - cnt2[j])
            if abs(dist) < 50:
                return True
            elif i == row1 - 1 and j == row2 - 1:
                return False


def join_close_contours(contours):
    LENGTH = len(contours)
    status = np.zeros((LENGTH, 1))

    for i, cnt1 in enumerate(contours):
        x = i
        if i != LENGTH - 1:
            for j, cnt2 in enumerate(contours[i + 1:]):
                x = x + 1
                dist = find_if_close(cnt1, cnt2)
                if dist == True:
                    val = min(status[i], status[x])
                    status[x] = status[i] = val
                else:
                    if status[x] == status[i]:
                        status[x] = i + 1

    unified = []
    maximum = int(status.max()) + 1
    for i in range(maximum):
        pos = np.where(status == i)[0]
        if pos.size != 0:
            cont = np.vstack(contours[i] for i in pos)
            hull = cv2.convexHull(cont)
            unified.append(hull)
    return unified


def detect_contours(original_frame, params):
    #  cv2.RETR_TREE tells if one contour it's inside other
    #  cv2.RETR_EXTERNAL keeps only parent contours
    (contours, hierarchy) = cv2.findContours(original_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    detected_contours = []

    if params.get('debug', False):
        height, width = original_frame.shape[:2]
        black_image = np.zeros((height, width), np.uint8)
        ScreenManager.get_manager().show_frame(
            cv2.drawContours(black_image, contours, -1, (255, 255, 0), 3), 'contours')

    for idx, c in enumerate(contours):

        x, y, w, h = cv2.boundingRect(c)
        valid_contour = True

        if 'filter_contour_inside_other' in params:
            # If hierarchy[0, idx, 3] is different from -1, then your contour is inside another.
            if params['filter_contour_inside_other'] and hierarchy[0, idx, 3] != -1:
                valid_contour = False

        contour_percentage_of_frame = None
        if 'ignore_contours_smaller_than' in params:
            if contour_percentage_of_frame is None:
                area = cv2.contourArea(c)
                contour_percentage_of_frame = percentage_of_frame(original_frame, area)

            if contour_percentage_of_frame < params['ignore_contours_smaller_than']:
                valid_contour = False

        if 'ignore_contours_bigger_than' in params:
            if contour_percentage_of_frame is None:
                area = cv2.contourArea(c)
                contour_percentage_of_frame = percentage_of_frame(original_frame, area)

            if contour_percentage_of_frame > params['ignore_contours_bigger_than']:
                valid_contour = False

        if 'keep_contours_by_aspect_ratio' in params:
            # Assume player must be more tall than narrow, so, filter the ones that has more width than height

            if params['keep_contours_by_aspect_ratio'] == AspectRatio.taller:
                aspect_ratio = h / w
                # keep taller (h/w > 1) or slightly wider ( h/w > 0.9) contours
                # h / w >> 1. We don't want boxes that are too thin
                if aspect_ratio < 0.9 or aspect_ratio > 5:
                    valid_contour = False

            if params['keep_contours_by_aspect_ratio'] == AspectRatio.wider:
                aspect_ratio = w / h
                # keep wider (w/h > 1) or slightly taller ( w/h > 0.9) contours
                # w / h >> 1. We dont want boxes that are too thin
                if aspect_ratio < 0.6 or aspect_ratio > 3:
                    valid_contour = False

        if valid_contour:
            detected_contours.append((c, [x, y, w, h]))

    return detected_contours


def rgb_to_lab(p):
    new = rgb_to_xyz(p)
    return cl.XYZ_to_Lab(new)


def rgb_to_xyz(p):
    RGB_to_XYZ_matrix = np.array(
        [[0.41240000, 0.35760000, 0.18050000],
         [0.21260000, 0.71520000, 0.07220000],
         [0.01930000, 0.11920000, 0.95050000]])
    illuminant_RGB = np.array([0.31270, 0.32900])
    illuminant_XYZ = np.array([0.34570, 0.35850])
    return cl.RGB_to_XYZ(p / 255, illuminant_RGB, illuminant_XYZ,
                         RGB_to_XYZ_matrix, 'Bradford')


def xyz_to_rgb(p):
    XYZ_to_RGB_matrix = np.array(
        [[3.24062548, -1.53720797, -0.49862860],
         [-0.96893071, 1.87575606, 0.04151752],
         [0.05571012, -0.20402105, 1.05699594]])
    illuminant_RGB = np.array([0.31270, 0.32900])
    illuminant_XYZ = np.array([0.34570, 0.35850])
    newp = cl.XYZ_to_RGB(p, illuminant_XYZ, illuminant_RGB,
                         XYZ_to_RGB_matrix, 'Bradford')
    return newp * 255


# converts from lab to rgb
def lab_to_rgb(p):
    xyz = cl.Lab_to_XYZ(p)
    return xyz_to_rgb(xyz)


def remove_green(original_frame, params={}):
    frame = remove_color(original_frame, ColorRange.green.color_range)
    return frame


def get_biggest_component_mask(original_frame, params):
    # search connected components over the mask, and get the biggest one
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(original_frame,
                                                                            params.get('connectivity', 4))
    biggest_component_label = stats.argmax(axis=0)[cv2.CC_STAT_AREA]

    # get a mask which includes only the biggest component
    biggest_component_mask = np.zeros_like(labels, np.uint8)
    biggest_component_mask[labels == biggest_component_label] = 255
    return biggest_component_mask


def get_biggest_components_mask(original_frame, params={}):
    # search connected components over the mask, and get the biggest one
    totalLabels, label_ids, values, centroid = cv2.connectedComponentsWithStats(
        original_frame,
        params.get('connectivity', 8),
        cv2.CV_32S
    )
    result = np.zeros_like(label_ids, np.uint8)

    for i in range(1, totalLabels):
        # Area of the component
        area = values[i, cv2.CC_STAT_AREA]

        if (area > 1) and (area < 10):
            # get a mask which includes only the biggest component
            result = np.zeros_like(label_ids, np.uint8)
            result[label_ids == label_ids[1]] = 255

    return result


def nothing(original_frame, params):
    return original_frame


def color_mask_bgr(original_frame, params):
    color_label = params.get('label', '')
    color = params.get(color_label)
    mask = cv2.inRange(original_frame, np.array(color.get_bgr_lower()), np.array(color.get_bgr_upper()))
    return mask


def color_mask_hsv(original_frame, params):
    hsv = cv2.cvtColor(original_frame, cv2.COLOR_BGR2HSV)
    color_label = params.get('label', '')
    color = params.get(color_label)
    mask = cv2.inRange(hsv, np.array(color.get_hsv_lower()), np.array(color.get_hsv_upper()))
    return mask


def color_mask(original_frame, params):
    green_mask = cv2.inRange(original_frame, params.get('min'), params.get('max'))
    return green_mask


def apply_mask(mask, params):
    frame_name = params.get('mask')
    frame = cv2.bitwise_and(params.get(frame_name), params.get(frame_name), mask=mask)
    return frame


def add_mask(frame, params):
    mask = params.get('mask')
    frame = cv2.bitwise_or(frame, mask)
    return frame


def remove_mask_2(frame, params):
    mask = params.get("mask")
    return cv2.bitwise_and(frame, frame, mask=~mask)


def remove_mask(frame, params):
    mask = params.get("mask")
    res = frame - mask
    return res


def transform_matrix_gray_range(original_frame, params=None):
    old_min, old_max, new_min, new_max = \
        params.get('old_min'), \
        params.get('old_max'), \
        params.get('new_min', 0), \
        params.get('new_max', 255)

    scale = (new_max - new_min) / (old_max - old_min)
    res = (original_frame - old_min) * scale

    if params.get('replace_0', None) is not None:
        res[res == 0] = params.get('replace_0')

    return res.astype(np.uint8)


def apply_otsu(frame, params=None):
    if params is None:
        params = {}

    _, image_result = cv2.threshold(
        frame,
        params.get('low', 0),
        params.get('high', 255),
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    return image_result


def join_masks(frame, params):
    label = params.get('label', 'mask')
    mask = params.get(label)
    mask = cv2.add(frame, mask)
    return mask


def apply_erosion(frame, params={}):
    percentage_of_frame = params.get('percentage_of_frame', None)

    if percentage_of_frame is not None:
        width = int(len(frame) * percentage_of_frame / 100)
        params['element_size'] = (width, width)

    kernel = cv2.getStructuringElement(
        params.get('element', cv2.MORPH_RECT),
        params.get('element_size', params.get('element_size', (6, 6)))
    )

    eroded_frame = cv2.erode(frame, kernel, iterations=params.get('iterations', 1))
    return eroded_frame


def apply_dilatation(frame, params={}):
    percentage_of_frame = params.get('percentage_of_frame', None)

    if percentage_of_frame is not None:
        width = int(len(frame) * percentage_of_frame / 100)
        params['element_size'] = (width, width)

    kernel = cv2.getStructuringElement(
        params.get('element', cv2.MORPH_RECT),
        params.get('element_size', (6, 6)))

    dilated_frame = cv2.dilate(frame, kernel, iterations=params.get('iterations', 1))
    return dilated_frame


def to_mask(pixel):
    if abs(pixel) > 40:
        return 255
    return 0


def apply_linear_function(frame, params={}):
    fn = params.get('fn')
    height = frame.shape[0]
    width = frame.shape[1]

    grayimg = np.zeros((height, width), np.uint8)

    for i in range(height):
        for j in range(width):
            grayimg[i, j] = fn(frame[i, j])

    return grayimg


def negate(original_frame, params={}):
    res = ~original_frame
    return res


def apply_blur(frame, params={}):
    blurred_frame = cv2.blur(frame, params.get('blur', params.get('element_size', (5, 5))))
    return blurred_frame


def change_contrast(frame, params={}):
    alpha = 1.0  # Simple contrast control
    beta = 0  # Simple brightness control
    # Initialize values
    alpha = 1.5  # Enter the alpha value [1.0-3.0]
    beta = 0  # Enter the beta value [0-100]
    # Do the operation new_image(i,j) = alpha*image(i,j) + beta
    # Instead of these 'for' loops we could have used simply:
    # new_image = cv.convertScaleAbs(image, alpha=alpha, beta=beta)
    # but we wanted to show you how to access the pixels :)
    new_image = cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)
    # for y in range(image.shape[0]):
    #     for x in range(image.shape[1]):
    #         for c in range(image.shape[2]):
    #             new_image[y, x, c] = np.clip(alpha * image[y, x, c] + beta, 0, 255)
    return new_image


def fill_contours(frame, params):
    (contours, hierarchy) = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for pic, contour in enumerate(contours):
        cv2.fillPoly(frame, pts=[contour], color=255)

    return frame


def filter_lines_using_hough(mask, min_length, min_width):
    # Utiliza la transformada de Hough probabilística para detectar líneas en la imagen binarizada
    rho = 1  # Resolución de distancia en píxeles de la acumulación
    theta = np.pi / 180  # Resolución angular en radianes de la acumulación
    threshold = int(min_length * 0.5)  # Solo las líneas que tengan un número de votos mayor al umbral serán devueltas
    lines = cv2.HoughLinesP(mask, rho, theta, threshold, minLineLength=min_length, maxLineGap=min_width)

    return lines
def get_lines_lsd(original_frame, params={}):
    # Create default Fast Line Detector (FSD)
    if params.get("gray_image", False):
        gray_image = original_frame
    else:
        gray_image = cv2.cvtColor(original_frame, cv2.COLOR_BGR2GRAY)

    height, width = original_frame.shape[:2]
    min_length = int(width * params.get('min_length_line_in_video_percentage', 0.01))
    fld = cv2.ximgproc.createFastLineDetector(min_length)

    # Detect lines in the image
    lines = fld.detect(gray_image)
    # Draw detected lines in the image
    black_image = np.zeros((height, width), np.uint8)
    mask = fld.drawSegments(black_image, lines)

    ScreenManager.get_manager().show_frame(mask, 'lines_1') if params.get('debug_lines', False) else None

    # keep only one channel (any channel works)
    mask = mask[:, :, 2]

    mask = morphological_closing(mask, {'element_size': (3, 3)})
    ScreenManager.get_manager().show_frame(mask, 'lines_close') if params.get('debug_lines', False) else None

    mask = apply_dilatation(mask, {'element_size': params.get('dilatation', (4, 4))})
    ScreenManager.get_manager().show_frame(mask, 'lines_dilatation') if params.get('debug_lines', False) else None

    # mask = morphological_opening(mask, {'element_size': (2, 2)})
    # ScreenManager.get_manager().show_frame(mask, 'lines_open') if params.get('debug_lines', False) else None

    min_length = min_length * 3
    min_width = 10
    filtered_lines = filter_lines_using_hough(mask, min_length, min_width)

    # Crea una nueva imagen en negro y dibuja solo las líneas filtradas
    filtered_mask = np.zeros((height, width), np.uint8)
    for line in filtered_lines:
        for x1, y1, x2, y2 in line:
            cv2.line(filtered_mask, (x1, y1), (x2, y2), 255, 2)

    # Muestra la máscara filtrada si se solicita en los parámetros
    ScreenManager.get_manager().show_frame(filtered_mask, 'filtered_lines') if params.get('debug_lines', False) else None

    return mask

def get_lines_top_hat(original_frame, params={}):
    top_hat = morphological_top_hat(original_frame, {
        'percentage_of_frame': params.get('percentage_of_frame', 0.3),
        'remove': True
    })
    lines = original_frame - top_hat
    grey_scale = cv2.cvtColor(lines, cv2.COLOR_BGR2GRAY)
    res = cv2.threshold(grey_scale, 10, 255, cv2.THRESH_BINARY)[1]
    return res


def remove_lines_canny(original_frame, params={}):
    lines = get_lines_lsd(original_frame, params)
    ScreenManager.get_manager().show_frame(lines, 'lines') if params.get("debug", None) else None

    image = remove_mask_2(original_frame, params={"mask": lines})
    return image


# def remove_lines_canny(frame, params):
#     mask = np.zeros(frame.shape, np.uint8)
#
#     canny = cv2.Canny(frame, 100, 200)
#     kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
#
#     ScreenManager.get_manager().show_frame(canny, '1')
#     close = cv2.morphologyEx(canny, cv2.MORPH_CLOSE, kernel)
#
#     ScreenManager.get_manager().show_frame(close, '2')
#
#     minLineLength = 100
#     maxLineGap = 350
#
#     lines = cv2.HoughLinesP(close, 1, np.pi / 180, 100, minLineLength, maxLineGap)
#
#     if lines is None:
#         return frame
#
#     for line in lines:
#         for x1, y1, x2, y2 in line:
#             cv2.line(mask, (x1, y1), (x2, y2), (255, 255, 255), 3)
#
#     cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#     cnts = cnts[0] if len(cnts) == 2 else cnts[1]
#
#     for c in cnts:
#         cv2.drawContours(frame, [c], -1, (255, 255, 255), -1)
#
#     return frame


def remove_lines(frame, params):
    # Create diagonal kernel

    kernels = [
        np.array([[0, 0, 0],
                  [1, 1, 1],
                  [0, 0, 0]], dtype=np.uint8),

        np.array([[0, 0, 1],
                  [0, 1, 0],
                  [1, 0, 0]], dtype=np.uint8),

        np.array([[0, 0, 0, 0, 1],
                  [0, 0, 0, 1, 0],
                  [0, 0, 1, 0, 0],
                  [0, 1, 0, 0, 0],
                  [1, 0, 0, 0, 0]], dtype=np.uint8),

        np.array([[1, 0, 0],
                  [0, 1, 0],
                  [0, 0, 1]], dtype=np.uint8)
    ]

    for k in kernels:
        opening = cv2.morphologyEx(frame, cv2.MORPH_OPEN, k, iterations=1)

        cnts = cv2.findContours(opening, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        for c in cnts:
            area = cv2.contourArea(c)
            if area < 500:
                cv2.drawContours(opening, [c], -1, (0, 0, 0), -1)

    return opening


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


def morphological_opening(original_frame, params={}):
    percentage_of_frame = params.get('percentage_of_frame', None)
    if percentage_of_frame is not None:
        width = int(len(original_frame) * percentage_of_frame / 100)
        params['element_size'] = (width, width)

    kernel = cv2.getStructuringElement(
        params.get('element', cv2.MORPH_RECT),
        params.get('element_size', (3, 3)))

    frame = cv2.morphologyEx(original_frame, cv2.MORPH_OPEN, kernel, iterations=params.get('iterations', 1))
    return frame


def morphological_top_hat(original_frame, params={}):
    percentage_of_frame = params.get('percentage_of_frame', None)

    if percentage_of_frame is not None:
        width = int(len(original_frame) * percentage_of_frame / 100)
        params['element_size'] = (width, width)

    kernel = cv2.getStructuringElement(
        params.get('element', cv2.MORPH_RECT),
        params.get('element_size', (3, 3)))

    image_result = cv2.morphologyEx(original_frame, cv2.MORPH_TOPHAT, kernel, iterations=params.get('iterations', 1))

    if params.get('remove', False):
        image_result = remove_mask(original_frame, {'mask': image_result})

    return image_result


def morphological_black_hat(original_frame, params={}):
    percentage_of_frame = params.get('percentage_of_frame', None)

    if percentage_of_frame is not None:
        width = int(len(original_frame) * percentage_of_frame / 100)
        params['element_size'] = (width, width)

    kernel = cv2.getStructuringElement(
        params.get('element', cv2.MORPH_RECT),
        params.get('element_size', (10, 10)))

    image_result = cv2.morphologyEx(original_frame, cv2.MORPH_BLACKHAT, kernel, iterations=params.get('iterations', 1))
    return image_result


# Use "close" morphological operation to close the gaps between contours
# https://stackoverflow.com/questions/18339988/implementing-imcloseim-se-in-opencv
def morphological_closing(original_frame, params={}):
    percentage_of_frame = params.get('percentage_of_frame', None)
    if percentage_of_frame is not None:
        width = int(len(original_frame) * percentage_of_frame / 100)
        params['element_size'] = (width, width)

    kernel = cv2.getStructuringElement(
        params.get('element', cv2.MORPH_RECT),
        params.get('element_size', (10, 10)))
    frame = cv2.morphologyEx(original_frame, cv2.MORPH_CLOSE, kernel, iterations=params.get('iterations', 1))
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


def fill_black_pixels_in_gray_image(original_frame, params):
    filled_frame = original_frame
    filled_frame[np.where((filled_frame == [0]))] = [params.get("value", 0)]
    return filled_frame


def grey_in_range_to_mask(original_frame, params):
    _, res = cv2.threshold(
        original_frame,
        params.get("max_gray_value", 255),
        params.get("to_value", 255),
        cv2.THRESH_BINARY
    )
    return res, None


def grey_in_range(original_frame, params):
    gray_mask = cv2.inRange(original_frame, params.get("low", 0), params.get("high", 0))
    applied_gray_mask = cv2.bitwise_and(original_frame, gray_mask)

    if params.get('blacks_defaults_to_high', False):
        # fill new black pixels with default value
        applied_gray_mask = fill_black_pixels_in_gray_image(applied_gray_mask, {'value': params.get('high', 0)})
        # restore original blacks
        applied_gray_mask = cv2.bitwise_and(applied_gray_mask, original_frame)

    if params.get('negated_result', False):
        negated_result = cv2.bitwise_and(original_frame, negate(gray_mask))
        return applied_gray_mask, gray_mask, negated_result, negate(gray_mask)

    return applied_gray_mask, None


def test(original_frame, params):
    default = params.get('default_values', False)
    mask = cv2.inRange(original_frame, params.get("low", 0), params.get("high", 0))
    res = cv2.bitwise_and(original_frame, mask)
    if default is not None:
        res = cv2.bitwise_or(res, ~mask)

    return res


# https://stackoverflow.com/questions/42257173/contrast-stretching-in-python-opencv
def contrast_stretching(original_frame, params={}):
    norm_img = cv2.normalize(original_frame, None, alpha=0, beta=1.6, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
    norm_img = np.clip(norm_img, 0, 1)
    norm_img = (255 * norm_img).astype(np.uint8)
    return norm_img


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


def gray_scale(original_frame, params={}):
    frame = cv2.cvtColor(original_frame, params.get('code', cv2.COLOR_BGR2GRAY))
    return frame


def rgb_to_mask(original_frame, params={}):
    return cv2.inRange(original_frame, np.array([1, 1, 1]), np.array([255, 255, 255]))


def sobel(original_frame, params):
    frame = cv2.Sobel(original_frame, cv2.CV_8U, 1, 0, ksize=1)
    return frame


def g_greater_than_r_greater_than_b_mask(original_frame, params=None):
    # frame is expected to be in BGR format
    r_channel = original_frame[:, :, 2]
    g_channel = original_frame[:, :, 1]
    b_channel = original_frame[:, :, 0]

    g_greater_than_r = g_channel > r_channel
    r_greater_than_b = r_channel > b_channel
    g_greater_than_r_greater_than_b = g_greater_than_r & r_greater_than_b

    # the resulting mask will be defined as:
    #   255 for pixels that satisfy G > R > B,
    #     0 otherwise
    return g_greater_than_r_greater_than_b.astype(np.uint8) * 255
