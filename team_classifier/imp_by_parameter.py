from domain.player import *
from domain.team import *
from player_detector.step import *
from utils import constants
from utils.frame_utils import g_greater_than_r_greater_than_b_mask
from utils.utils import FramePrinter


class ByParameter:
    def __init__(self, **kwargs):
        self.args = kwargs

    def classify_teams(self, frame, players: [Player]):
        if self.args.get('defending_team', False):
            team = self.args['defending_team']
            set_defending_team(team)
        if self.args.get('attacking_team', False):
            team = self.args['attacking_team']
            set_attacking_team(team)


class ByBallDetection:

    def __init__(self, **kwargs):
        self.args = kwargs
        self.video = None
        self.debug = kwargs['debug']
        self.screen_manager = ScreenManager.get_manager()
        self.log = Logger(self, LoggingPackage.team_classifier)
        self.frame_printer = FramePrinter()
        self.ball_position = kwargs.get('ball_position_first_frame', None)
        self.ball_histogram = None
        self.latest_ball_histograms = []
        self.consecutive_searches_without_change = 0
        self.background_subtractor = cv2.createBackgroundSubtractorKNN(detectShadows=False)

    def classify_teams(self, video, players: [Player]):
        self.video = video
        # self.run()
        self.run2(players)

    def run2(self, players):
        # for the first frame, the ball is manually selected
        if self.ball_histogram is None:
            if self.ball_position is None:
                self.ball_position = self._manually_select_ball_postion()
            # self.latest_ball_histograms.append(self._calculate_hist(self.video.get_current_frame(), self.ball_position))
            self.ball_histogram = self._calculate_hist(self.video.get_current_frame(), self.ball_position)
        else:
            self.ball_position = self.find_ball_position2(players)

        set_defending_team(self.find_defending_team(players))

    def find_defending_team(self, players: [Player]):
        closest_player = None
        closest_player_distance = None
        for player in players:
            # if player is not in one of the two teams, continue
            if player.team not in all_teams:
                continue
            bounding_box_center = player.get_box().get_center()
            distance = np.sqrt(np.sum(np.square(np.array(self.ball_position, dtype=int) - np.array(bounding_box_center, dtype=int))))
            if closest_player is None or distance < closest_player_distance:
                closest_player = player
                closest_player_distance = distance

        if self.debug and closest_player is not None:
            frame = self.video.get_current_frame().copy()
            player_box = closest_player.get_box()
            cv2.rectangle(frame, player_box.down_left, player_box.upper_right, closest_player.get_color(), 2)
            self.screen_manager.show_frame(frame, "Closest player")

        # If no player was found we assign a default team. TODO: find another method instead of doint this
        if closest_player is None:
            return team_one

        return closest_player.team

    def find_ball_position(self):
        original_frame = self.video.get_current_frame()
        img = cv2.medianBlur(original_frame, 5)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        if self.debug:
            self.screen_manager.show_frame(img, "Img")

        g_greater_than_r_greater_than_b = g_greater_than_r_greater_than_b_mask(original_frame, {})
        g_greater_than_r_greater_than_b = cv2.morphologyEx(g_greater_than_r_greater_than_b, cv2.MORPH_ERODE,
                                                           cv2.getStructuringElement(cv2.MORPH_RECT, (15, 35)))

        if self.debug:
            self.screen_manager.show_frame(g_greater_than_r_greater_than_b, "G > R > B")

        substracted_players = cv2.bitwise_and(img, img, mask=g_greater_than_r_greater_than_b)

        if self.debug:
            self.screen_manager.show_frame(substracted_players, "Subtract players")

        param1 = 300
        ball_candidates = cv2.HoughCircles(substracted_players, cv2.HOUGH_GRADIENT, 1, 15, param1=param1, param2=5, minRadius=3, maxRadius=6)

        # if no candidates were detected we keep the previous frame ball position
        if ball_candidates is None:
            self.consecutive_searches_without_change = self.consecutive_searches_without_change + 1
            return self.ball_position

        ball_candidates = np.uint16(np.around(ball_candidates))
        hough_circles_frame = original_frame.copy()
        for i in ball_candidates[0, :]:
            # draw the outer circle
            cv2.circle(hough_circles_frame, (i[0], i[1]), i[2], (0, 255, 0), 1)
            # draw the center of the circle
            # cv2.rectangle(original_frame, (i[0] - i[2], i[1] - i[2]), (i[0] + i[2], i[1] + i[2]), (0, 0, 255), 2)

        if self.debug:
            cv2.imshow("Hough circ", hough_circles_frame)
            self.screen_manager.show_frame(hough_circles_frame, "Circular hough")

        print("Current position: (" + str(self.ball_position[0]) + ", " + str(self.ball_position[1]) + ")")
        nearest_ball_candidate = None
        nearest_ball_candidate_distance = None
        nearest_ball_candidate_histogram = None
        greatest_hist_comp = None

        max_consecutive_searches_without_change = 5
        max_distance = 20
        if self.consecutive_searches_without_change > max_consecutive_searches_without_change:
            print("CONSECUTIVE SEARCHES WITHOUT CHANGE")
            max_distance = max_distance * max_consecutive_searches_without_change

        for candidate in ball_candidates[0, :]:
            candidate_position = (candidate[0], candidate[1])

            print("Candidate: (" + str(candidate[0]) + ", " + str(candidate[1]) + ")")
            distance = np.sqrt(np.sum(np.square(np.array(self.ball_position, dtype=int) - np.array(candidate_position, dtype=int))))
            # luminance = self._calculate_luminance(original_frame, candidate)

            candidate_histogram = self._calculate_hist(original_frame, candidate)
            histogram_comp = self._compare_histograms(candidate_histogram)

            print("Candidate: (" + str(candidate[0]) + ", " + str(candidate[1]) + ") -- Distance: " + str(distance) + ") -- Hist: " + str(histogram_comp))
            # if distance < max_distance and 110 < luminance < 175 and (nearest_ball_candidate_distance is None or nearest_ball_candidate_distance > distance):
            if distance <= max_distance and (greatest_hist_comp is None or greatest_hist_comp > histogram_comp):
                nearest_ball_candidate = candidate_position
                nearest_ball_candidate_distance = distance
                nearest_ball_candidate_histogram = candidate_histogram
                greatest_hist_comp = histogram_comp

        if nearest_ball_candidate_distance is None:
            self.consecutive_searches_without_change = self.consecutive_searches_without_change + 1
            nearest_ball_candidate = self.ball_position
            nearest_ball_candidate_histogram = self.ball_histogram
        else:
            self.consecutive_searches_without_change = 0

        if self.debug:
            cv2.circle(original_frame, nearest_ball_candidate, 5, (0, 0, 255), 2)
            self.screen_manager.show_frame(original_frame, "Detected ball")

        if self.consecutive_searches_without_change == 0:
            if len(self.latest_ball_histograms) == 1:
                self.latest_ball_histograms.pop(0)

            self.latest_ball_histograms.append(nearest_ball_candidate_histogram)

        return nearest_ball_candidate

    # solution using background subtraction first
    def find_ball_position2(self, players):
        original_frame = self.video.get_current_frame()
        img = cv2.medianBlur(original_frame, 5)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        if self.debug:
            self.screen_manager.show_frame(img, "Gray")

        mask = self.background_subtractor.apply(img)

        mask_binary = cv2.threshold(mask, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        if self.debug:
            self.screen_manager.show_frame(mask_binary, "Background subtraction KNN BINARY")

        dilated = cv2.morphologyEx(mask_binary, cv2.MORPH_DILATE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))

        if self.debug:
            self.screen_manager.show_frame(dilated, "Dilated")

        # search connected components over the mask, and get the biggest one
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask_binary, connectivity=8)

        if self.debug:
            self.imshow_components_new(labels, "Components")

        if self.debug:
            frame_copy = original_frame.copy()
            for player in players:
                player_box = player.get_box()
                cv2.rectangle(frame_copy, player_box.down_left, player_box.upper_right, player.get_color(), 2)
            self.screen_manager.show_frame(frame_copy, "Players")

        candidate_euclidean_distances = []
        candidate_histogram_distances = []
        candidate_circularities = []
        candidate_centroids = []
        candidate_histograms = []

        for i in range(0, num_labels):
            component_stats = stats[i]
            height = component_stats[cv2.CC_STAT_HEIGHT]
            width = component_stats[cv2.CC_STAT_WIDTH]
            area = component_stats[cv2.CC_STAT_AREA]
            if math.isnan(centroids[i][0]):
                continue
            candidate_position = (round(centroids[i][0]), round(centroids[i][1]))
            distance = np.sqrt(np.sum(np.square(np.array(self.ball_position, dtype=int) - np.array(candidate_position, dtype=int))))
            # if 25 < area < 100 and 4 < height < 20 and 4 < width < 20 and distance <= 50:
            if 50 < area < 150 and 10 < height < 30 and 10 < width < 25 and distance <= 90:
                candidate_histogram = self._calculate_hist(original_frame, candidate_position)
                histogram_comp = self._compare_histograms(candidate_histogram)
                circularity, contours = self.calculate_circularity(labels, i, np.array(candidate_position))
                if self.debug:
                    print("Component: {} - Centroid: {} - Height: {} - Width: {} - Area: {} - Distance: {} - Hist comp: {} - Circ: {}".format(i, centroids[i], height, width, area, distance, histogram_comp, circularity))
                    copy = original_frame.copy()
                    cv2.drawContours(copy, contours, -1, (255, 0, 0), 1)
                    text_lines = [
                        "Centroid: ({}, {})".format(candidate_position[0], candidate_position[1]),
                        "Dist: {}".format(distance),
                        "Circ: {}".format(circularity),
                        "Histogram: {}".format(histogram_comp)
                    ]
                    FramePrinter().print_multiline_text(copy, text_lines, (candidate_position[0], candidate_position[1] - 65), (255, 255, 255))
                    cv2.imshow("Contours", copy)
                    # self.screen_manager.show_frame(copy, "Contours")
                if circularity > 3 and histogram_comp < 10 and not self.point_intersects_player_box(players, candidate_position):
                    candidate_euclidean_distances.append(distance)
                    candidate_histogram_distances.append(histogram_comp)
                    candidate_circularities.append(circularity)
                    candidate_centroids.append(candidate_position)
                    candidate_histograms.append(candidate_histogram)

        candidate_euclidean_distances = [(1 / x if x != 0 else 1) for x in candidate_euclidean_distances]
        candidate_histogram_distances = [(1 / x if x != 0 else 1) for x in candidate_histogram_distances]

        candidate_euclidean_distances = np.asarray(candidate_euclidean_distances, dtype=np.float32)
        candidate_histogram_distances = np.asarray(candidate_histogram_distances, dtype=np.float32)
        candidate_circularities = np.asarray(candidate_circularities, dtype=np.float32)

        cv2.normalize(candidate_euclidean_distances, candidate_euclidean_distances, alpha=1, beta=0, norm_type=cv2.NORM_INF)
        cv2.normalize(candidate_histogram_distances, candidate_histogram_distances, alpha=1, beta=0, norm_type=cv2.NORM_INF)
        cv2.normalize(candidate_circularities, candidate_circularities, alpha=1, beta=0, norm_type=cv2.NORM_INF)

        max_score = -1
        ball_position = None
        histogram = None
        for i in range(0, len(candidate_euclidean_distances)):
            euclidean_distance = candidate_euclidean_distances[i]
            histogram_distance = candidate_histogram_distances[i]
            circularity = candidate_circularities[i]

            score = euclidean_distance + histogram_distance + circularity
            print("Centroid: {} - Distance score: {} - Hist comp score: {} - Circ score: {} - SCORE: {}".format(candidate_centroids[i], euclidean_distance, histogram_distance, circularity, score))
            if score > max_score:
                max_score = score
                ball_position = candidate_centroids[i]
                histogram = candidate_histograms[i]

        if ball_position is None:
            ball_position = self.ball_position
        else:
            self.ball_histogram = histogram

        if self.debug:
            cv2.circle(original_frame, ball_position, 5, (0, 0, 255), 2)
            self.screen_manager.show_frame(original_frame, "Detected ball")

        return ball_position

    def point_intersects_player_box(self, players, point):
        for player in players:
            if self.point_inside_player_box(player, point):
                return True
        return False

    def point_inside_player_box(self, player, point):
        player_box = player.get_box()
        box_width = player_box.w
        box_height = player_box.h
        box_x = player_box.x
        box_y = player_box.y
        return box_x <= point[0] <= box_x + box_width and box_y <= point[1] <= box_y + box_height

    def calculate_circularity(self, labels, component_idx, centroid):
        candidates_mask = np.zeros_like(labels, np.uint8)
        candidates_mask[labels == component_idx] = 255
        if self.debug:
            cv2.imshow("Contours MASK", candidates_mask)
            # elf.screen_manager.show_frame(candidates_mask, "Contours MASK")

        contours, hierarchy = cv2.findContours(candidates_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        # calculate mu
        perimeter_points = contours[0].shape[0]
        sum = 0
        for i in range(0, perimeter_points):
            sum += np.linalg.norm(contours[0][i][0] - centroid)
        mu = sum / perimeter_points

        # calculate theta
        sum = 0
        for i in range(0, perimeter_points):
            sum += math.pow(np.linalg.norm(contours[0][i][0] - centroid) - mu, 2)
        theta = sum / perimeter_points

        circularity = mu / theta
        return circularity, contours


    def imshow_components_new(self, labels, window_name):
        if labels.shape[0] == 0:
            return
        # Map component labels to hue val
        label_hue = np.uint8(179 * labels / np.max(labels))
        blank_ch = 255 * np.ones_like(label_hue)
        labeled_img = cv2.merge([label_hue, blank_ch, blank_ch])

        # cvt to BGR for display
        labeled_img = cv2.cvtColor(labeled_img, cv2.COLOR_HSV2BGR)

        # set bg label to black
        labeled_img[label_hue == 0] = 0

        # self.screen_manager.show_frame(labeled_img, window_name)
        cv2.imshow(window_name, labeled_img)

    def _compare_histograms(self, candidate_histogram):
        histogram_comp_sum = 0
        hist_comps = []
        # for histogram in self.latest_ball_histograms:
        #     histogram_comp = cv2.compareHist(candidate_histogram, histogram, cv2.HISTCMP_KL_DIV)
        #     histogram_comp_sum = histogram_comp_sum + histogram_comp
        #     hist_comps.append(histogram_comp)

        # absolute value is applied since in some cases the output is negative. In those cases, the negative value
        # is very close to 0, so this shouldn't make a big difference
        return abs(cv2.compareHist(candidate_histogram, self.ball_histogram, cv2.HISTCMP_KL_DIV))

        # return histogram_comp_sum / len(self.latest_ball_histograms)
        # return min(hist_comps)

    def _calculate_luminance(self, frame, ball_candidate):
        centroid_x = ball_candidate[0]
        centroid_y = ball_candidate[1]
        radius = ball_candidate[2]
        extra = 15

        # top_left_bounding_box_corner = (max(centroid_x - radius - extra, 0), max(centroid_y - radius - extra, 0))
        # bottom_right_bounding_box_corner = (min(centroid_x + radius + extra, frame.shape[1]), min(centroid_y + radius + extra, frame.shape[0]))
        top_left_bounding_box_corner = (max(centroid_x - extra, 0), max(centroid_y - extra, 0))
        bottom_right_bounding_box_corner = (min(centroid_x + extra, frame.shape[1]), min(centroid_y + extra, frame.shape[0]))

        bounding_box_matrix = frame[top_left_bounding_box_corner[1]:bottom_right_bounding_box_corner[1], top_left_bounding_box_corner[0]:bottom_right_bounding_box_corner[0], :]
        pixels_array = bounding_box_matrix.reshape(bounding_box_matrix.shape[0] * bounding_box_matrix.shape[1], bounding_box_matrix.shape[2])

        # luminance_function = lambda p: 0.2126 * p[0] + 0.7152 * p[1] + 0.0722 * p[2]
        luminance_function = lambda p: 0.299 * p[0] + 0.587 * p[1] + 0.144 * p[2]

        pixels_luminance = np.apply_along_axis(luminance_function, 1, pixels_array)

        return np.average(pixels_luminance)

    def _calculate_hist(self, frame, ball_position):
        centroid_x = ball_position[0]
        centroid_y = ball_position[1]
        extra = 10

        top_left_bounding_box_corner = (max(centroid_x - extra, 0), max(centroid_y - extra, 0))
        bottom_right_bounding_box_corner = (min(centroid_x + extra, frame.shape[1]), min(centroid_y + extra, frame.shape[0]))

        bounding_box_matrix = frame[top_left_bounding_box_corner[1]:bottom_right_bounding_box_corner[1], top_left_bounding_box_corner[0]:bottom_right_bounding_box_corner[0], :]

        if self.debug:
            frame_copy = frame.copy()
            cv2.rectangle(frame_copy, top_left_bounding_box_corner, bottom_right_bounding_box_corner, (255, 0, 0), 2)
            self.screen_manager.show_frame(frame_copy, "Candidate hist region")

        h_bins = 60
        # s_bins = 128
        histSize = [h_bins]
        # hue varies from 0 to 179, saturation from 0 to 255
        h_ranges = [0, 180]
        # s_ranges = [0, 256]
        ranges = h_ranges  # concat lists
        # Use the 0-th and 1-st channels
        channels = [0]

        bounding_box_hsv = cv2.cvtColor(bounding_box_matrix, cv2.COLOR_BGR2HSV)
        hist = cv2.calcHist([bounding_box_hsv], channels, None, histSize, ranges, accumulate=False)
        cv2.normalize(hist, hist, alpha=1.0, beta=0.0, norm_type=cv2.NORM_INF)
        return hist

    def _manually_select_ball_postion(self):
        window_name = "Select ball position"
        frame = self.video.get_current_frame()
        arguments = {
            'captured_click': None,
            'frame': frame,
            'window_name': window_name
        }
        self.frame_printer.print_text(frame, "Select ball position (click over the ball)", (5, 30), constants.BGR_WHITE)
        cv2.imshow(window_name, frame)
        cv2.setMouseCallback(window_name, self._click_event, arguments)

        cv2.waitKey(0)
        cv2.destroyWindow(window_name)

        ball_position = arguments['captured_click']
        self.log.log("Manually selected ball position: " + str(ball_position))

        return ball_position

    def _click_event(self, event, x, y, flags, arguments):
        if event == cv2.EVENT_LBUTTONUP:
            click_coordinates = (x, y)
            frame = arguments['frame']
            arguments['captured_click'] = click_coordinates
            self.frame_printer.print_point(frame, click_coordinates, constants.BGR_RED)
            cv2.imshow(arguments['window_name'], frame)

    def run(self):
        original_frame = self.video.get_current_frame()

        g_greater_than_r_greater_than_b = cv2.bitwise_not(g_greater_than_r_greater_than_b_mask(original_frame, {}))

        if self.debug:
            self.screen_manager.show_frame(g_greater_than_r_greater_than_b, "G > R > B")

        sobel_frame = cv2.Sobel(cv2.cvtColor(original_frame, cv2.COLOR_BGR2GRAY), cv2.CV_8U, 1, 0, ksize=-1)

        if self.debug:
            self.screen_manager.show_frame(sobel_frame, "Sobel gradient over original image")

        sobel_frame_g_r_b = cv2.Sobel(g_greater_than_r_greater_than_b, cv2.CV_8U, 1, 0, ksize=-1)

        if self.debug:
            self.screen_manager.show_frame(sobel_frame_g_r_b, "Sobel gradient over G > R > B")

        sobel_plus_frame_g_r_b = cv2.bitwise_or(g_greater_than_r_greater_than_b, sobel_frame)
        sobel_plus_frame_g_r_b = cv2.threshold(sobel_plus_frame_g_r_b, 127, 255, cv2.THRESH_BINARY)[1]

        sobel_plus_frame_g_r_b = cv2.morphologyEx(sobel_plus_frame_g_r_b, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (10, 10)))
        sobel_plus_frame_g_r_b = cv2.morphologyEx(sobel_plus_frame_g_r_b, cv2.MORPH_DILATE, cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)))

        if self.debug:
            self.screen_manager.show_frame(sobel_plus_frame_g_r_b, "Sobel gradient + G > R > B")

        rho = 1
        theta = np.pi / 180
        threshold = 400
        height, width = original_frame.shape[:2]

        hsv_img = cv2.cvtColor(original_frame, cv2.COLOR_RGB2HSV)
        img_v = hsv_img[:, :, 2]
        # if self.debug:
        #     self.screen_manager.show_frame(open_img_v, "Dilated img V")
        img = cv2.Canny(img_v, 10, 30, apertureSize=3)
        if self.debug:
            self.screen_manager.show_frame(img, "Canny")

        dest = np.zeros((height, width), np.uint8)

        # lines = cv2.HoughLines(img, rho, theta, threshold)
        #
        # if lines is not None:
        #     for i in range(0, len(lines)):
        #         rho = lines[i][0][0]
        #         theta = lines[i][0][1]
        #         a = math.cos(theta)
        #         b = math.sin(theta)
        #         x0 = a * rho
        #         y0 = b * rho
        #         line_length = 3000
        #         pt1 = (int(x0 + line_length * (-b)), int(y0 + line_length * (a)))
        #         pt2 = (int(x0 - line_length * (-b)), int(y0 - line_length * (a)))
        #         cv2.line(dest, pt1, pt2, (255, 255, 255), 2)

        linesP = cv2.HoughLinesP(sobel_plus_frame_g_r_b, 1, np.pi / 180, 50, None, 200, 10)

        if linesP is not None:
            for i in range(0, len(linesP)):
                l = linesP[i][0]
                cv2.line(dest, (l[0], l[1]), (l[2], l[3]), (255, 255, 255), 4)

        if self.debug:
            self.screen_manager.show_frame(dest, "Hough")

        substracted_lines = cv2.bitwise_and(sobel_plus_frame_g_r_b, sobel_plus_frame_g_r_b, mask=~dest)
        # substracted_lines = cv2.subtract(eroded_label_mask, dest)

        if self.debug:
            self.screen_manager.show_frame(substracted_lines, "substracted_lines")

        elimination_threshold = height * width * 0.0005
        # search connected components over the mask, and get the biggest one
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(substracted_lines, connectivity=8)

        # get a mask which includes only the biggest component
        components_mask = np.ones_like(labels, np.uint8) * 255
        for i in range(0, num_labels):
            if stats[i][cv2.CC_STAT_AREA] > elimination_threshold or stats[i][cv2.CC_STAT_HEIGHT] / stats[i][cv2.CC_STAT_WIDTH] > 1.75:
                components_mask[labels == i] = 0

        if self.debug:
            self.screen_manager.show_frame(components_mask, "Components mask")

        asd = cv2.bitwise_xor(substracted_lines, components_mask)

        if self.debug:
            self.screen_manager.show_frame(asd, "AND")

        sobel_frame_asd = cv2.Sobel(asd, cv2.CV_8U, 1, 0, ksize=3)

        if self.debug:
            self.screen_manager.show_frame(sobel_frame_asd, "Sobel Again")

        combined = cv2.bitwise_or(sobel_frame_asd, sobel_frame_g_r_b)

        if self.debug:
            self.screen_manager.show_frame(combined, "Combined")

        # self.imshow_components(labels)

    def imshow_components(self, labels):
        # Map component labels to hue val
        label_hue = np.uint8(179 * labels / np.max(labels))
        blank_ch = 255 * np.ones_like(label_hue)
        labeled_img = cv2.merge([label_hue, blank_ch, blank_ch])

        # cvt to BGR for display
        labeled_img = cv2.cvtColor(labeled_img, cv2.COLOR_HSV2BGR)

        # set bg label to black
        labeled_img[label_hue == 0] = 0

        if self.debug:
            self.screen_manager.show_frame(labeled_img, "Components mask")