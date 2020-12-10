import cv2
import numpy as np
from typing import List

import utils.utils as utils
import log.log as log
from video_repository.video_repository import *
import imutils


class Step:
    def __init__(self, name: str, function, debug: bool = False):
        self.log = log.Log(self, log.LoggingPackage.player_detector)
        self.name = name
        self.function = function
        self.debug = debug

    def apply(self, number, original_frame):
        self.log.log('applying step', {"number": number, "name": self.name})
        frame = self.function(original_frame)
        if self.debug:
            name = str(number) + " " + self.name
            cv2.imshow(name, frame)
            cv2.moveWindow(name, number * 300, 200)

        return frame


class Player:
    def __init__(self, coordinates, team=None):
        self.coordinates = coordinates
        self.team = team


class PlayerDetector:

    def __init__(self, dilatation: bool = False):
        self.last_frame = None
        self.dilatation = dilatation
        self.log = log.Log(self, log.LoggingPackage.player_detector)
        self.frame_utils = utils.FrameUtils()
        self.fgbg = cv2.createBackgroundSubtractorMOG2(history=100, detectShadows=False, varThreshold=50)
        self.min_area = 0.5

        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        self.kernel_dil = np.ones((1, 1), np.uint8)

    def set_dilatation(self, dilatation: bool):
        self.dilatation = dilatation

    def remove_green(self, frame):
        # convert to hsv color space
        green_lower = (29, 86, 6)
        green_upper = (64, 255, 255)

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, green_lower, green_upper)
        frame = cv2.bitwise_not(frame, frame, mask=mask)
        return frame

    def apply_dilatation(self, frame):
        dilated_frame = cv2.dilate(frame, None, iterations=1)
        return dilated_frame

    def delete_small_countours(self, frame):
        (contours, hierarchy) = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        for pic, contour in enumerate(contours):
            area = cv2.contourArea(contour)

            if area < 50:
                cv2.fillPoly(frame, pts=[contour], color=0)
                continue

        return frame

    # https://stackoverflow.com/questions/52247821/find-width-and-height-of-rotatedrect
    def filter_countours_by_aspect_ratio(self, frame):
        (contours, hierarchy) = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        for pic, c in enumerate(contours):
            rect = cv2.minAreaRect(c)
            (x, y), (w, h), angle = rect
            # Assume player must be more tall than narrow, so, filter the ones that has more width than height
            if w > h:
                cv2.fillPoly(frame, pts=[c], color=0)

            # Assume player bb must be a rectangle, so, the division of larger side / shorter side must be more than 1
            aspect_ratio = max(w, h) / min(w, h)
            if aspect_ratio < 1.5:
                cv2.fillPoly(frame, pts=[c], color=0)
                continue

        return frame

    # Use "close" morphological operation to close the gaps between contours
    # https://stackoverflow.com/questions/18339988/implementing-imcloseim-se-in-opencv
    def join_close_countours(self, frame):
        cv2.morphologyEx(frame, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (51, 51)))
        return frame

    def background_substitution(self, original_frame):
        frame = self.fgbg.apply(original_frame)
        return frame

    def find_players(self, frame):
        players = []
        cv2.imshow('detect_players_in_frame original', frame)

        pipeline: List[Step] = [
            Step("remove green", self.remove_green, debug=True),
            Step("background_substitution", self.background_substitution, debug=True),
            Step("delete small countours", self.delete_small_countours, debug=True),
            Step("filter by aspect ration", self.filter_countours_by_aspect_ratio, debug=True),
            Step("join close countours", self.join_close_countours, debug=True),
            Step("apply dilatation", self.apply_dilatation, debug=True),
        ]

        for idx, step in enumerate(pipeline):
            frame = step.apply(idx, frame)

        (contours, hierarchy) = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        for pic, c in enumerate(contours):
            area = cv2.contourArea(c)
            # Small contours are ignored.
            if area < 10:
                cv2.fillPoly(frame, pts=[c], color=0)
                continue

            x, y, w, h = cv2.boundingRect(c)

            area = w * h
            percentage_of_frame = self.frame_utils.percentage_of_frame(frame, area)

            if 0.9 > percentage_of_frame > 0.1:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                cv2.putText(frame, 'People', (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2,
                            cv2.LINE_AA)
                players.append(Player([x, y, w, h]))

        cv2.imshow('final result', frame)
        return players

    # def detect_players_in_frame(self, frame: Frame) -> List[Player]:
    #     fgmask = self.fgbg.apply(frame.get_frame())
    #     fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, self.kernel)
    #     fgmask = self.apply_dilatation(fgmask)
    #     players = self.find_players(fgmask, area_percentage=5)
    #     return players
    #
    # def detect_players_in_frame_2(self, frame: Frame) -> List[Player]:
    #     frame = frame.get_frame()
    #     # frame = cv2.flip(frame), 180)
    #     outmask = self.fgbg.apply(frame)
    #     outmask = self.apply_dilatation(outmask)
    #     players = self.find_players(outmask)
    #     cv2.imshow('detect_players_in_frame_2', outmask)
    #     return players

    def detect_players_in_frame(self, frame: Frame) -> List[Player]:
        self.log.log("finding players", {"frame": frame.get_frame_number()})

        frame = frame.get_frame()
        frame = cv2.resize(frame, (500, 500))
        players = self.find_players(frame)
        return players

    # def detect_players_in_frame_3(self, frame: Frame) -> List[Player]:
    #     frame = frame.get_frame()
    #
    #     # convert it to grayscale
    #     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #
    #     # blur it
    #     # gray = cv2.GaussianBlur(gray, (21, 21), 0)
    #
    #     if self.last_frame is None:
    #         self.last_frame = gray
    #         return []
    #
    #     # last frame
    #     frameDelta = cv2.absdiff(self.last_frame, gray)
    #
    #     # update last frame
    #     self.last_frame = gray
    #
    #     thresh = cv2.threshold(frameDelta, 15, 255, cv2.THRESH_BINARY)[1]
    #
    #     # erode
    #     thresh = cv2.erode(thresh, None, iterations=2)
    #
    #     # dilate the thresholded image to fill in holes
    #     thresh = cv2.dilate(thresh, None, iterations=3)
    #
    #     # find contours
    #     cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #     cnts = imutils.grab_contours(cnts)
    #
    #     players = []
    #     # loop over the contours
    #     for c in cnts:
    #         # if the contour is too small, ignore it
    #         countour_area = cv2.contourArea(c)
    #         self.log.log("countour area", {"area": countour_area, "countour": cv2.boundingRect(c)})
    #         if countour_area < self.min_area:
    #             continue
    #         # compute the bounding box for the contour, draw it on the frame,
    #         # and update the text
    #         (x, y, w, h) = cv2.boundingRect(c)
    #         # cv2.rectangle(thresh, (x, y), (x + w, y + h), (255, 0, 0), 2)
    #         # cv2.putText(thresh, 'People', (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2, cv2.LINE_AA)
    #         players.append(Player([x, y, w, h]))
    #
    #     cv2.imshow('detect_players_in_frame_3', thresh)
    #
    #     return players


'''
if __name__ == '__main__':
    cap = cv2.VideoCapture('../videos/quintero.mp4')

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    subtractor = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=50, detectShadows=False)

    while True:
        _, frame = cap.read()
        mask = subtractor.apply(frame)
        cv2.imshow("Frame", frame)
        cv2.imshow("mask", mask)
        key = cv2.waitKey(30)
        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
'''
