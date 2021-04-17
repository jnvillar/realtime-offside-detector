from domain.player import *
from log.log import *
import cv2

OPENCV_OBJECT_TRACKERS = {
    "csrt": cv2.TrackerCSRT_create,
    "kcf": cv2.TrackerKCF_create,
    "boosting": cv2.TrackerBoosting_create,
    "mil": cv2.TrackerMIL_create,
    "tld": cv2.TrackerTLD_create,
    "medianflow": cv2.TrackerMedianFlow_create,
    "mosse": cv2.TrackerMOSSE_create
}


class OpenCVTracker:

    def __init__(self, **kwargs):
        self.log = Log(self, LoggingPackage.player_tracker)
        self.tracking = False
        self.trackers = []
        self.tracker_name = kwargs['tracker']

    def init_trackers(self, frame, players: [Player]):
        if len(players) == 0:
            return

        payers_bb = get_players_bb(players)

        for player_bb in payers_bb:
            tracker = OPENCV_OBJECT_TRACKERS[self.tracker_name]()
            tracker.init(frame, tuple(player_bb))
            self.trackers.append(tracker)

        self.tracking = True

    def track_players(self, frame, players: [Player]):

        if not self.tracking or len(players) != len(self.trackers):
            self.init_trackers(frame, players)
            return players

        for tracker in self.trackers:
            (success, box) = tracker.update(frame)

            # check to see if the tracking was a success
            if success:
                (x, y, w, h) = [int(v) for v in box]
                cv2.rectangle(frame, (x, y), (x + w, y + h),
                              (0, 255, 0), 2)
        return frame
