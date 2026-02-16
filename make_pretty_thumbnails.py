import os

import cv2

from cv2_utils import get_thumbnail, show_frame
from file_io import load_data
from visualize_movement import visualize_data

# this file generates the pictures used in the repository

DISPLAY_WIDTH = 720
DISH_COLOR = [255,200,200]
FISH_COLOR = [255,0,0]
FISH_PATH_COLOR = [0,255,0]

# change specific pixels from a frame to a new color
def draw_pixels_on_image(frame, pixels, color=[255,0,0]):
    for pixel in pixels:
        frame[pixel[1],pixel[0]] = color

    return frame

def add_overlays_to_frame(frame, dish_overlay, fish_overlay, fish_union={}):
    draw_pixels_on_image(frame, dish_overlay, DISH_COLOR)
    draw_pixels_on_image(frame, fish_union, FISH_PATH_COLOR)
    draw_pixels_on_image(frame, fish_overlay[0], FISH_COLOR)

    return frame

def save_image(path,image):
    upscaled_image = cv2.resize(image, (DISPLAY_WIDTH, DISPLAY_WIDTH), interpolation=cv2.INTER_NEAREST_EXACT)
    show_frame(upscaled_image,(DISPLAY_WIDTH,DISPLAY_WIDTH),0)
    #cv2.imwrite(path, image)

for _,_, files in os.walk("source_videos/"):
    for file in files:
        video_src = "source_videos/"+file
        compressed_src = "data/videos/compressed_sources/"+file
        binary_src = "data/videos/binary_sources/"+file

        original_frame = get_thumbnail(video_src)
        compressed_frame = get_thumbnail(compressed_src)
        binary_frame = get_thumbnail(binary_src)

        dish, fish = load_data('data/'+file.removesuffix(".mp4"))

        fish_union = {}
        for fish_frame in fish:
            for fish_pixel in fish_frame:
                fish_union[fish_pixel] = True

        frame_with_data = add_overlays_to_frame(binary_frame.copy(), dish, fish, fish_union)

        save_image('assets/original_frame.png', original_frame)
        save_image('assets/compressed_frame.png', compressed_frame)
        save_image('assets/binary_frame.png', binary_frame)
        save_image('assets/binary_frame_with_overlays.png', frame_with_data)


