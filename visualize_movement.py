import os

import cv2
from tqdm import tqdm

from cv2_utils import cast_video_to_frame_list, show_frame
from file_io import get_saved_data_from_video

##################################################################
# This script takes processed data (from process_movement.py)
# and visualizes what was actually isolated in the data.
#
# The primary use for this is tuning parameters like:
#   - in compress_videos.py
#       - VIDEO_SIZE
#       - COLOR_COMPRESSION_THRESHOLD
#   - in process_movement.py
#       - DISH_STEP
#       - BLACK_WHITE_THRESHOLD
#
# If the data tracks the fish movement accurately and w/o noise
# then the data you have is good!
##################################################################


########################################
# display related settings
########################################

# the width in pixels to display frames
DISPLAY_WIDTH = 720
# colors
DISH_COLOR = [255,200,200]
FISH_COLOR = [255,0,0]
FISH_PATH_COLOR = [0,255,0]



# change specific pixels from a frame to a new color
def draw_pixels_on_image(frame, pixels, color=[255,0,0]):
    for pixel in pixels:
        frame[pixel[1],pixel[0]] = color

    return frame

# track movement and show full video w/ bounding boxes
def show_full_capture(frames, dish_overlay, fish_overlay, fish_union={}):
    for i, frame in enumerate(tqdm(frames)):
        draw_pixels_on_image(frame, dish_overlay, DISH_COLOR)
        draw_pixels_on_image(frame, fish_union, FISH_PATH_COLOR)
        draw_pixels_on_image(frame, fish_overlay[i], FISH_COLOR)
        
        if show_frame(frame, (DISPLAY_WIDTH,DISPLAY_WIDTH), 1):
            break
    
    cv2.destroyAllWindows()

# show video with overlays for the dish, fish, and full fish travel path
def visualize_data(video_src, dish_union, fish_pixels):
    print(f"loading video: {video_src}")
    video_frames = cast_video_to_frame_list(video_src)

    fish_union = {}
    for fish_frame in fish_pixels:
        for fish_pixel in fish_frame:
            fish_union[fish_pixel] = True

    print("displaying video with overlays (press q to exit): ")
    show_full_capture(video_frames, dish_union, fish_pixels, fish_union)


def main(show_all_videos=False):
    for _,_, files in os.walk("data/videos/binary_sources"):
        for file in files:
            video_src = "data/videos/binary_sources/"+file
            dish_union, fish_pixels, video_scale = get_saved_data_from_video(video_src)

            visualize_data(video_src, dish_union, fish_pixels)
            if not show_all_videos:
                return


if __name__ == "__main__":
    main(True)