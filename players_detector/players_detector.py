import cv2
import numpy as np
import utils.utils as utils
import log.log as log


class Player():
    def __init__(self, coordinates, team=None):
        self.coordinates = coordinates
        self.team = team


class PlayerDetector():

    def __init__(self, dilatation=False):
        self.dilatation = dilatation
        self.log = log.Log(self, log.LoggingPackage.player_detector)
        self.frame_utils = utils.FrameUtils()
        self.fgbg = cv2.createBackgroundSubtractorMOG2(history=100, detectShadows=False, varThreshold=80)

        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        self.kernel_dil = np.ones((1, 1), np.uint8)

    def set_dilatation(self, dilatation):
        self.dilatation = dilatation

    def apply_dilatation(self, frame):
        if self.dilatation:
            return cv2.dilate(frame, self.kernel_dil, iterations=1)
        return frame

    def method1(self):
        cap = cv2.VideoCapture(self.video_path)

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

    def find_players(self, frame, area_percentage=0.2):
        players = []
        (contours, hierarchy) = cv2.findContours(frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for pic, contour in enumerate(contours):
            #epsilon = 0.1 * cv2.arcLength(contours, True)
            #approx = cv2.approxPolyDP(contours, epsilon, True)
            area = cv2.contourArea(contour)

            x, y, w, h = cv2.boundingRect(contour)

            percentage_of_frame = self.frame_utils.percentage_of_frame(frame, area)

            if percentage_of_frame > area_percentage:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                cv2.putText(frame, 'People', (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2, cv2.LINE_AA)
                players.append(Player([x, y, w, h]))

        return players

    def detect_players_in_frame_2(self, frame):
        frame = frame.get_frame()
        # frame = cv2.flip(frame), 180)
        outmask = self.fgbg.apply(frame)
        outmask = self.apply_dilatation(outmask)
        players = self.find_players(outmask)
        cv2.imshow('detect_players_in_frame_2', outmask)
        return players

    def detect_players_in_frame(self, frame):

        fgmask = self.fgbg.apply(frame.get_frame())
        fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, self.kernel)
        fgmask = self.apply_dilatation(fgmask)
        players = self.find_players(fgmask, area_percentage=5)
        #cv2.imshow('detect_players_in_frame', fgmask)
        return players

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
