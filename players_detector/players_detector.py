import cv2
import numpy as np
import time
import utils.utils as utils
import log.log as log


class PlayerDetector():

    # video_path = string
    def __init__(self, video_path):
        self.video_path = video_path
        self.log = log.Log(self, log.LoggingPackage.player_detector)
        self.frame_utils = utils.FrameUtils()

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

    def find_players(self, frame, area_percentage=5):
        (contours, hierarchy) = cv2.findContours(frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for pic, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            x, y, w, h = cv2.boundingRect(contour)

            percentage_of_frame = self.frame_utils.percentage_of_frame(frame, area)

            self.log.log("player area", {'area': percentage_of_frame})

            if percentage_of_frame > area_percentage:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                cv2.putText(frame, 'People', (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2, cv2.LINE_AA)

    def method2(self):
        cap = cv2.VideoCapture(self.video_path)

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

        fgbg = cv2.createBackgroundSubtractorMOG2(history=100, detectShadows=False, varThreshold=60)
        kernel_dil = np.ones((4, 4), np.uint8)

        while True:
            ret, frame = cap.read()
            fgmask = fgbg.apply(frame)
            fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)
            dilation = cv2.dilate(fgmask, kernel_dil, iterations=1)

            self.find_players(dilation, area_percentage=5)
            cv2.imshow('dilatation', dilation)

            if cv2.waitKey(30) & 0xFF == ord('q'):
                time.sleep(10)
                break

        cap.release()
        cv2.destroyAllWindows()


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
