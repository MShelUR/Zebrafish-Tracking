import os

import tkinter

from file_io import get_saved_data_from_video

# this script generates information about how the zebrafish move

########################################
# conversion related settings
########################################

# in mm
DISH_SIZE = 100


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

def main(dish_size):
    root = tkinter.Tk()
    canvas = tkinter.Canvas(root, width=720, height=540)
    canvas.pack()

    for _,_, files in os.walk("data/videos/binary_sources"):
        for file in files:
            video_src = "data/videos/binary_sources/"+file
            dish, fish_frames = get_saved_data_from_video(video_src)

            avg_positions = []

            for fish in fish_frames:
                avg_positions.append(get_avg_pixel(fish))

            print(avg_positions)

            last = avg_positions[0]
            for pos in avg_positions[1:]:
                canvas.create_line(last[0],last[1],pos[0],pos[1], fill="blue")
                last = pos

            print(get_total_distance(avg_positions))

            root.mainloop()




if __name__ == "__main__":
    main(DISH_SIZE)