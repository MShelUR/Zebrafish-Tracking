import contextlib
import os

import ffmpeg # NOTE: must install ffmpeg separately and add to path in windows

from cv2_utils import get_video_dimensions, make_black_white_video
from file_io import verify_data_folders_exist


# this script compresses full quality videos into smaller videos, then
# makes the compressed videos have exclusively black and white pixels






########################################
# user settings
########################################

# reprocess videos that have a file in "videos/binary_sources" already
REPROCESS = False

########################################
# image processing related settings
#   NOTE: these WILL affect your data!
########################################

# width and height of videos post compression
#   lossless is 2048
VIDEO_SIZE = 128

# threshold for black/white coloring
#   0 makes all pixels white
#   255 makes all pixels black
COLOR_COMPRESSION_THRESHOLD = 50

def compress_video(in_file, out_file, scale):
    try:
        ffmpeg.input(in_file).output(
            out_file,
            vf=f'scale={scale}:-2',
            loglevel="quiet"
        ).run(overwrite_output=True)
    except ffmpeg.Error as error:
        print('ffmpeg ran into a problem:\n\t', error.stderr.decode('utf8'))
    except Exception as error:
        print('unknown error occurred with video compression:\n\t', error)

def is_file_already_processed(binary_file, scale):
    if os.path.exists(binary_file) and get_video_dimensions(binary_file)[0] == scale:
        return True
        
videos_processed = 0

def preprocess_video(file, scale, threshold):
    global videos_processed

    source_file = 'source_videos/'+file
    compressed_file = 'data/videos/compressed_sources/'+file
    binary_file = 'data/videos/binary_sources/'+file

    if not REPROCESS:
        if is_file_already_processed(binary_file, scale):
            if __name__ == "__main__":
                print(f"skipping {source_file}, already processed")
            return

    print(f"compressing {source_file}...")

    # change video scale
    compress_video(source_file, compressed_file, scale)

    # make videos black and white
    make_black_white_video(compressed_file, binary_file, scale, threshold)

    videos_processed += 1


def main(scale, threshold):
    global videos_processed

    verify_data_folders_exist()

    for _,_, files in os.walk('source_videos'):
        for file in files:
            preprocess_video(file, scale, threshold)

    print(f"compressed {videos_processed} video(s)")


if __name__ == "__main__":
    main(VIDEO_SIZE, COLOR_COMPRESSION_THRESHOLD)