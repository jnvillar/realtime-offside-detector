import players_detector.players_detector as players_detector
import video_repository.video_repository as video_repository
import utils.constants as constants
import cv2
import time


def play_video(video):
    play = True
    last_frame = False

    detector = players_detector.PlayerDetector()

    while True and not last_frame:
        while play:
            frame = video.get_next_frame()
            last_frame = frame.is_last_frame()
            if last_frame:
                break

            detector.detect_players_in_frame_4(frame)

            if cv2.waitKey(30) & 0xFF == ord('q'):
                play = not play

        if cv2.waitKey(30) & 0xFF == ord('q'):
            play = not play

    print("end")


if __name__ == '__main__':

    video_path = './test/videos'
    video_repository = video_repository.VideoRepository()

    while True:
        print("start")
        video_repository.load_videos(video_path)
        video = video_repository.get_video(constants.VideoConstants.video_1_from_8_to_12)
        play_video(video)
