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

# below is how I calculated this for the samples I used:
#   original video is 2048x2048
#   in the bottom left, there is a reference for 3.5mm. it is 416 pixels long
#       this means 118.86 pixels is ~1mm
#   since I compressed the videos to be 128x128:
#       118.86/(2048/128) = 7.42875 pixels is ~1mm

# 7.42875 pixels in the videos is ~1mm
UNIT_PER_PIXEL = 1/7.42875

# if the fish's body moves less than this amount of pixels per frame, don't count it
#   this prevents a fish slightly rotating counting as constant movement for distance tracking
MOVEMENT_THRESHOLD = 2

# how many frames per second
VIDEO_FRAMERATE = 18


########################################
# visualization settings
########################################

# width and height size in pixels for viewing the data
VISUAL_SCALE = 400


def get_avg_pixel(pixels):
    pixel_sum = [0,0]

    for pixel in pixels:
        pixel_sum[0] += pixel[0]
        pixel_sum[1] += pixel[1]

    if len(pixels) == 0:
        return None # fish is not visible! backoff to last known position.
    return (pixel_sum[0]/len(pixels),pixel_sum[1]/len(pixels))

def magnitude(pixel_a,pixel_b):
    return ((pixel_a[0]-pixel_b[0])**2 + (pixel_a[1]-pixel_b[1])**2)**.5

def get_dish_pixel_mm_conversion_rate(source):
    pass

def convert_pixels_to_mm(pixels_amount, mm_per_pixel):
    return pixels_amount*mm_per_pixel


# track distance and burst frequency
def get_movement_statistics(avg_positions):
    total_dist = 0
    last = avg_positions[0]

    burst_delays = []
    current_burst_delay = 0

    for pos in avg_positions[1:]:
        mag = magnitude(last,pos)
        if mag > MOVEMENT_THRESHOLD:
            # if the fish paused, add as a burst delay
            if current_burst_delay > 0:
                if current_burst_delay > 20:
                    burst_delays.append(round(current_burst_delay/VIDEO_FRAMERATE,2))
                current_burst_delay = 0
            
            total_dist += magnitude(last,pos)
            last = pos
        else: # fish didn't move for one frame
            current_burst_delay += 1

    return total_dist, burst_delays

def main(units_per_pixel, new_scale):

    cv2.namedWindow("Movement Visualization")

    for _,_, files in os.walk("data/videos/binary_sources"):
        for file in files:
            video_src = "data/videos/binary_sources/"+file
            result_image_path = "results/images/"+file.removesuffix(".mp4")+".png"
            result_stats_path = "results/numeric/"+file.removesuffix(".mp4")+".txt"
            dish, fish_frames, original_scale = get_saved_data_from_video(video_src)
            
            # set up the dish image
            center_of_dish = (original_scale//2, original_scale//2)

            # make entirely black picture
            dish_image = numpy.zeros((new_scale, new_scale, 4), dtype=numpy.uint8) # 4 channels for RGBA

            cv2.circle(dish_image, (new_scale//2,new_scale//2), new_scale//2, (0,0,0,255), cv2.FILLED)

            # add dish outline
            # for pixel in dish:
            #    dish_image[pixel[0],pixel[1]] = [255,255,255]



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
            median_positions = []

            for fish in fish_frames:
                new_avg = get_avg_pixel(fish)
                if new_avg: # if fish is visible, add its location
                    avg_positions.append(new_avg)
                    median_position = numpy.median(numpy.array(list(fish.keys())), axis=0)
                    median_positions.append(median_position)
                else: # if fish isn't visible, assume it was the last position it had
                    avg_positions.append(avg_positions[-1])

            # scale up dish for higher quality lines
            # dish_image = cv2.resize(dish_image, (new_scale, new_scale))

            num_frames = len(avg_positions)
            last = avg_positions[0]
            for i, pos in enumerate(avg_positions[1:]):
                # scale position to circle bounds
                pos_magnitude = ((pos[0]-center_of_dish[0])**2 + (pos[1]-center_of_dish[1])**2)**.5
                if pos_magnitude == 0:
                    continue
                pos_unit = ((pos[0]-center_of_dish[0]) / pos_magnitude, (pos[1]-center_of_dish[1]) / pos_magnitude)
                scaled_magnitude = min(pos_magnitude,original_scale/2-1) # 1 pixel offset to avoid clipping edges

                pos = (center_of_dish[0]+pos_unit[0]*scaled_magnitude, center_of_dish[1]+pos_unit[1]*scaled_magnitude)

                # get hex color for rainbow gradient
                hue = i / num_frames
                color = colorsys.hsv_to_rgb(hue, 1, 255)+(255,) # added 255 for opacity
                cv2.line(dish_image,(int(last[0]*scalar), int(last[1]*scalar)),(int(pos[0]*scalar), int(pos[1]*scalar)),color,2)
                last = pos

            #print(get_total_distance(avg_positions))
            
            cv2.imshow('Movement Visualization',dish_image)
            cv2.waitKey(1000)

            total_dist, bursts = get_movement_statistics(median_positions)
            #displacement = magnitude(avg_positions[0],avg_positions[-1])
            
            dist_in_mm = total_dist*units_per_pixel
            #displacement_in_mm = displacement*units_per_pixel

            print(file, dist_in_mm)
            print(bursts)
            save_frame(result_image_path, dish_image)

            fish_stats = [
                f"Total distance moved: {round(dist_in_mm,2)}mm",
                f"Number of bursts: {len(bursts)}",
                f"Average time between bursts: {sum(bursts) / len(bursts)}",
                f"Time between bursts: {bursts}"
            ]

            with open(result_stats_path, "w") as out_file:
                out_file.write("\n".join(fish_stats))




if __name__ == "__main__":
    main(UNIT_PER_PIXEL, VISUAL_SCALE)