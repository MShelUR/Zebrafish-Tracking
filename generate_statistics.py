import os

import tkinter

from file_io import get_saved_data_from_video
# this script generates information about how the zebrafish move

def get_avg_pixel(pixels):
    pixel_sum = [0,0]

    for pixel in pixels:
        pixel_sum[0] += pixel[0]
        pixel_sum[1] += pixel[1]

    return (pixel_sum[0]/len(pixels),pixel_sum[1]/len(pixels))

def get_total_distance(avg_positions):
    pass

def main():
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

            root.mainloop()




if __name__ == "__main__":
    main()