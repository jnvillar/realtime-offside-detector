from __future__ import unicode_literals
from argparse import ArgumentParser

from youtube_dl import YoutubeDL
from moviepy.video.io import ffmpeg_tools


def parse_arguments():
    parser = ArgumentParser("Youtube video downloader")
    parser.add_argument("-o", help="Output video name (if not used, the name will be 'videoTitle_startTime_endTime')", default=None)
    parser.add_argument("-d", help="Videos directory to store the downloaded video", default=None)
    parser.add_argument("video_url", help="Youtube URL of video")
    parser.add_argument("start_time", help="Start time to use when cropping")
    parser.add_argument("end_time", help="End time to use when cropping")
    arguments = parser.parse_args()
    url = arguments.video_url
    start_time = int(arguments.start_time)
    end_time = int(arguments.end_time)
    outfile = arguments.o
    directory = arguments.d
    return url, start_time, end_time, outfile, directory


if __name__ == '__main__':
    url, start_time, end_time, outfile, directory = parse_arguments()
    ydl_opts = {}
    full_hd = True
    with YoutubeDL(ydl_opts) as ydl:
        print("Fetching video info: {}".format(url))
        info = ydl.extract_info(url, download=False)
        if full_hd:
            video_url = info['requested_formats'][0]['url']
        else:
            formats = info['formats']
            # format_id == 136 --> 720p
            result = filter(lambda video_format: video_format['format_id'] == '136', formats)
            video_url = list(result)[0]['url']

        print(video_url)

        if outfile is None:
            outfile = info['title']

        if directory is None:
            output_video = "{}_{}_{}.mp4".format(outfile, start_time, end_time)
        else:
            output_video = "{}/{}_{}_{}.mp4".format(directory, outfile, start_time, end_time)

        ffmpeg_tools.ffmpeg_extract_subclip(video_url, start_time, end_time, targetname=output_video)
        print("Output video: {}".format(output_video))
