import players_detector.players_detector as players_detector
import video_repository.video_repository as video_repository
import cv2
import time

if __name__ == '__main__':
    video_path = './videos/corto.mp4'

    video_repository = video_repository.VideoRepository()
    video = video_repository.get_video(video_path)

    players_detector = players_detector.PlayerDetector(dilatation=True)

    while True:
        frame = video.get_next_frame()
       # players_detector.detect_players_in_frame(frame)
        players_detector.detect_players_in_frame_2(frame)

        if cv2.waitKey(30) & 0xFF == ord('q'):
            time.sleep(10)
            break
