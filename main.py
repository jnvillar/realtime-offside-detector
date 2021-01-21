import player_detector.player_detector as player_detector
import player_sorter.player_sorter as player_sorter
import video_repository.video_repository as video_repository
import utils.constants as constants
import cv2
from domain.video import Video
from utils.frame_utils import *

def play_video(soccer_video: Video, stop_in_frame: int = None):
    play = True
    last_frame = False

    detector = player_detector.PlayerDetector(debug=False)
    sorter = player_sorter.PlayerSorter()

    while True and not last_frame:
        while play:
            frame = soccer_video.get_next_frame()
            if frame is None:
                last_frame = True
                break

            frame = cv2.resize(frame, (500, 500))
            players = detector.detect_players_in_frame(frame, soccer_video.get_current_frame_number())
            sorter.sort_players(frame, players)
            mark_players(frame, players)

            cv2.imshow('final result', frame)

            if stop_in_frame is not None and stop_in_frame == soccer_video.get_current_frame_number():
                play = not play

            if cv2.waitKey(30) & 0xFF == ord('q'):
                play = not play

        if cv2.waitKey(30) & 0xFF == ord('q'):
            play = not play

    print("end")


if __name__ == '__main__':

    video_path = './test/videos'

    while True:
        print("start")
        video_container = video_repository.VideoRepository(video_path)
        video = video_container.get_video(constants.VideoConstants.video_1_from_8_to_12)
        play_video(video, stop_in_frame=59)
