import players_detector.players_detector as players_detector
import video_repository.video_repository as video_repository
import utils.constants as constants
import cv2
import time

if __name__ == '__main__':
    play = True
    video_path = './test/videos'

    video_repository = video_repository.VideoRepository()
    video_repository.load_videos(video_path)
    video = video_repository.get_video(constants.VideoConstants.video_1_from_8_to_12)

    players_detector = players_detector.PlayerDetector(dilatation=True)

    while True:
        while play:
            frame = video.get_next_frame()
            players_detector.detect_players_in_frame_2(frame)

            if cv2.waitKey(30) & 0xFF == ord('q'):
                play = not play

        if cv2.waitKey(30) & 0xFF == ord('q'):
            play = not play
