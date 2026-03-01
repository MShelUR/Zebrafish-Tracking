import os

import colorsys
import cv2
import numpy

from cv2_utils import save_frame
from file_io import get_saved_data_from_video

# this script generates information about how the zebrafish move

########################################
# conversion related settings
########################################

# in mm
DISH_SIZE = 100

# width and height size in pixels for viewing the data
VISUAL_SCALE = 400


def get_avg_pixel(pixels):
    pixel_sum = [0,0]

    for pixel in pixels:
        pixel_sum[0] += pixel[0]
        pixel_sum[1] += pixel[1]

    return (pixel_sum[0]/len(pixels),pixel_sum[1]/len(pixels))

def magnitude(pixel_a,pixel_b):
    return ((pixel_a[0]-pixel_b[0])**2 + (pixel_a[1]-pixel_b[1])**2)**.5

def get_dish_pixel_mm_conversion_rate(source):
    pass

def convert_pixels_to_mm(pixels_amount, conversion_rate):
    pass


def get_total_distance(avg_positions):
    total_dist = 0
    last = avg_positions[0]
    for pos in avg_positions[1:]:
        total_dist += magnitude(last,pos)
        last = pos

    return total_dist

def main(dish_size, new_scale):

    cv2.namedWindow("Movement Visualization")

    for _,_, files in os.walk("data/videos/binary_sources"):
        for file in files:
            video_src = "data/videos/binary_sources/"+file
            result_path = "results/"+file.removesuffix(".mp4")+".png"
            dish, fish_frames, original_scale = get_saved_data_from_video(video_src)
            
            # set up the dish image

            # make entirely white picture
            dish_image = numpy.ones((original_scale, original_scale, 3), dtype=numpy.uint8) # 3 channels for RGB

            # add dish outline
            for pixel in dish:
                dish_image[pixel[0],pixel[1]] = [255,255,255]



            # multiplier to recale pixel coordinates for the preview
            scalar = new_scale / original_scale

            # scale coordinates
            scaled_fish_frames = []
            for frame in fish_frames:
                new_frame = {}
                for coordinate in frame:
                    new_frame[round(coordinate[0]*scalar),round(coordinate[1]*scalar)] = True
                scaled_fish_frames.append(new_frame)

            avg_positions = []

            for fish in fish_frames:
                avg_positions.append(get_avg_pixel(fish))

            # scale up dish for higher quality lines
            dish_image = cv2.resize(dish_image, (new_scale, new_scale))

            num_frames = len(avg_positions)
            last = avg_positions[0]
            for i, pos in enumerate(avg_positions[1:]):

                # get hex color for rainbow gradient
                hue = i / num_frames
                color = colorsys.hsv_to_rgb(hue, 1, 255)
                cv2.line(dish_image,(int(last[0]*scalar), int(last[1]*scalar)),(int(pos[0]*scalar), int(pos[1]*scalar)),color,2)
                last = pos

            #print(get_total_distance(avg_positions))
            
            cv2.imshow('Movement Visualization',dish_image)
            cv2.waitKey(1000)

            save_frame(result_path, dish_image)




if __name__ == "__main__":
    main(DISH_SIZE, VISUAL_SCALE)