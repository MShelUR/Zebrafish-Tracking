from collections import deque
import os

from tqdm import tqdm

from cv2_utils import cast_video_to_frame_list, get_video_dimensions
from file_io import load_scale, save_data
from visualize_movement import show_full_capture

##################################################################
# this script takes compressed videos (from compress_videos.py)
# and does various math to isolate what pixels are:
#   - the dish
#   - the fish
#   - deadzones (the rest of the pixels)
##################################################################


########################################
# user settings
########################################


# take only one file, process it, and visualize results
DEBUG_MODE = False

# redo processing on videos that already have saved data
#   NOTE: DEBUG_MODE overwrites this
reprocess = False



########################################
# display related settings
########################################

# hide extra progress bars per file
#   NOTE: DEBUG_MODE overwrites this
hide_internal_tqdm_bars = True



########################################
# image processing related settings
#   NOTE: these WILL affect your data!
########################################

# above this color (/255) is white, below is black
#   200 is used because there may be noise after converting to black/white
#       ex. a pixel may be [254,240,235]
black_white_threshold = 200

# how often to check which pixels form the dish
#   increasing this greatly improves performance but decreases accuracy
#   1 = every frame
#   10 = every 10 frames
DISH_STEP = 10



########################################
# raster utilities
########################################

def get_color(frame,pixel):
    # finds the color of pixel (x,y) in given frame
    # returns 0 for black, 1 for white

    # index is [row, column] so x and y are swapped
    #   returns [R,G,B], only R is needed since video is black and white
    color_value = frame[pixel[1],pixel[0]][0]


    # since black and white, red is the only color needed to check
    if color_value >= black_white_threshold:
        return 1
    return 0

# get the neighbors of a pixel within image bounds of a specific color
def get_new_neighbors(frame, img_size, pixel, desired_color, closed_pixels, check_corners=False):
    neighbors = []

    for new_pixel in get_neighbors(pixel,check_corners):
        if new_pixel[0] < 0 or new_pixel[0] >= img_size:
            continue # out of bounds, ignore
        if new_pixel[1] < 0 or new_pixel[1] >= img_size:
            continue # out of bounds, ignore
        if closed_pixels.get(new_pixel):
            continue # already known
        if get_color(frame,new_pixel) != desired_color:
            continue # not the correct color
        
        neighbors.append(new_pixel)


    return neighbors

def get_matching_neighbors_from_frame(frame, img_size, starting_point, desired_color, check_corners=False):
    
    unchecked_pixels = deque() # need to be processed
    closed_pixels = {} # don't add to unchecked
    match_pixels = {} # is in the dish

    unchecked_pixels.append(starting_point)
    closed_pixels[starting_point] = True

    while len(unchecked_pixels) > 0:
        new_pixel = unchecked_pixels.popleft()

        if get_color(frame,new_pixel) == desired_color:
            match_pixels[new_pixel] = True
            
            new_neighbors = get_new_neighbors(frame, img_size, new_pixel, desired_color, closed_pixels, check_corners)

            for neighbor in new_neighbors:
                if not closed_pixels.get(neighbor):
                    unchecked_pixels.append(neighbor)
                    closed_pixels[neighbor] = True
    
    return match_pixels

# get all black borders in frame
def get_edges_at_frame(frame):
    img_size, _, _ = frame.shape

    corner_pixels = {}

    for x in range(0,img_size):
        for y in range(0,img_size,img_size-1):
            if get_color(frame,(x,y)) == 0 and not corner_pixels.get((x,y)):
                for pixel in get_matching_neighbors_from_frame(frame,img_size,(x,y),0,True):
                    corner_pixels[pixel] = True
    
    for x in range(0,img_size,img_size-1):
        for y in range(0,img_size):
            if get_color(frame,(x,y)) == 0 and not corner_pixels.get((x,y)):
                for pixel in get_matching_neighbors_from_frame(frame,img_size,(x,y),0,True):
                    corner_pixels[pixel] = True

    return corner_pixels

def find_middle_of_tray(frame, img_size, reach=5):
    middle_of_frame = img_size//2

    for dx in range(-reach,reach):
        for dy in range(-reach,reach):
            new_pixel = (middle_of_frame+dx,middle_of_frame+dy)
            if get_color(frame,new_pixel):
                return new_pixel # found starting point
    
    # if can't find dish, expand scope
    return find_middle_of_tray(frame, img_size, reach*2)

def get_difference_set(frame, pixels, desired_color):
    difference_set = []

    for pixel in pixels:
        if get_color(frame,pixel) == desired_color:
            difference_set.append(pixel)

    return difference_set


########################################
# pixel location utilities
########################################

def get_neighbors(pixel, check_corners):
    neighbors = []

    for dx in range(-1,2,2):
        neighbors.append((pixel[0]+dx,pixel[1]))
    
    for dy in range(-1,2,2):
        neighbors.append((pixel[0],pixel[1]+dy))

    if check_corners:
        for dx in range(-1,2,2):
            for dy in range(-1,2,2):
                neighbors.append((pixel[0]+dx,pixel[1]+dy))

    return neighbors

def get_matching_neighbors_from_set(starting_point, comparison_set, check_corners=False):
    
    unchecked_pixels = deque() # need to be processed
    closed_pixels = {} # don't add to unchecked
    match_pixels = {} # is in the dish

    unchecked_pixels.append(starting_point)
    closed_pixels[starting_point] = True

    while len(unchecked_pixels) > 0:
        new_pixel = unchecked_pixels.popleft()

        if comparison_set.get(new_pixel):
            match_pixels[new_pixel] = True

            new_neighbors = get_neighbors(new_pixel, check_corners)
            for neighbor in new_neighbors:
                if not closed_pixels.get(neighbor) and comparison_set.get(neighbor):
                    unchecked_pixels.append(neighbor)
                    closed_pixels[neighbor] = True

    return match_pixels

def num_neighbors_in_set(pixel, comparison_set):
    num_neighbors = 0

    for neighbor in get_neighbors(pixel, True):
        if comparison_set.get(neighbor):
            num_neighbors += 1

    return num_neighbors

def get_largest_body(pixels):
    bodies = []

    closed_pixels = {}

    for pixel in pixels:
        if closed_pixels.get(pixel):
            continue

        body = get_matching_neighbors_from_set(pixel, pixels, True)

        for body_pixel in body:
            closed_pixels[body_pixel] = True

        bodies.append(body)

    if len(bodies) == 0:
        return {} # no pixels

    selected_body = bodies[0]
    selected_size = len(bodies[0])

    for body in bodies:
        body_size = len(body)
        if body_size > selected_size:
            selected_body = body
            selected_size = body_size

    return selected_body




########################################
# main functions
########################################

# find where the dish is at a specific frame
def get_dish_at_frame(frame):
    # looks near center
    # finds white pixels
    # finds all neighboring pixels that are white
    
    img_size, _, _ = frame.shape


    # start with a white pixel in the center of the dish
    middle_of_tray = find_middle_of_tray(frame, img_size)

    dish_pixels = get_matching_neighbors_from_frame(frame,img_size,middle_of_tray,1)

    return dish_pixels

# get every pixel that, at some point, was unobstructed
def get_dish_union(frames):
    
    # union of the dish
    dish_union = {}

    # union of pixels that at some point were connected to the corners
    corner_union = {}

    for frame in tqdm(frames, disable=hide_internal_tqdm_bars):

        for dish_pixel in get_dish_at_frame(frame):
            dish_union[dish_pixel] = True
        for edge_pixel in get_edges_at_frame(frame):
            corner_union[edge_pixel] = True

    for pixel in corner_union:
        if dish_union.get(pixel):
            del dish_union[pixel]

    return dish_union

def get_fish_pixels(frames,dish_union):

    # per frame, list of fish pixels
    fish_pixels_set = []

    for frame in tqdm(frames, disable=hide_internal_tqdm_bars):
        new_pixels = get_difference_set(frame,dish_union, 0)
        fish_pixels = {}

        for pixel in new_pixels:
            if num_neighbors_in_set(pixel,dish_union) == 8:
                fish_pixels[pixel] = True

        fish = get_largest_body(fish_pixels)

        fish_pixels_set.append(fish)

    return fish_pixels_set




########################################
# video processing and display
########################################


# process video, display progress, display results
def debug_tracking(video_src):

    global hide_internal_tqdm_bars
    global reprocess
    
    reprocess = False
    hide_internal_tqdm_bars = False

    print(f"loading video: {video_src}")
    video_frames = cast_video_to_frame_list(video_src)
    video_size, _, _ = video_frames[0].shape

    print(f"getting dish bounds...")
    dish_union = get_dish_union(video_frames[::10]) # only check every 10th frame
    dish_pixel_percent = round(len(dish_union)/(video_size**2)*100,2)
    print(f"found {len(dish_union)} pixels that comprise the dish ({dish_pixel_percent}% of video)")

    print(f"getting fish pixels...")
    fish_pixels = get_fish_pixels(video_frames,dish_union)

    print(f"getting all pixels that will be the fish...")
    fish_union = {}
    for fish_frame in fish_pixels:
        for fish_pixel in fish_frame:
            fish_union[fish_pixel] = True

    print("displaying video with overlays (press q to exit): ")
    show_full_capture(video_frames, dish_union, fish_pixels, fish_union)


def is_file_already_processed(video_src, output_destination):
    if not os.path.isdir(output_destination):
        return False
    if not os.path.isfile(output_destination+"/dish_pixels.json"):
        return False
    if not os.path.isfile(output_destination+"/fish_pixels.json"):
        return False
    if not os.path.isfile(output_destination+"/scale.txt"):
        return False
    
    video_scale = get_video_dimensions(video_src)[0]
    saved_scale = load_scale(output_destination)

    if video_scale != saved_scale:
        return False
    
    return True



def main(step, threshold):
    global black_white_threshold
    black_white_threshold = threshold

    videos_processed = 0
    for _,_, files in os.walk("data/videos/binary_sources"):
        for file in files:
            video_src = "data/videos/binary_sources/"+file
            output_destination = f"data/{file}".removesuffix(".mp4")

            if not reprocess and is_file_already_processed(video_src, output_destination):
                print(f"skipping {video_src}, already processed")
                continue

            if DEBUG_MODE:
                debug_tracking(video_src)
                exit()


            print(f"processing {video_src}")

            video_frames = cast_video_to_frame_list(video_src)

            dish_union = get_dish_union(video_frames[::step])
            fish_pixels = get_fish_pixels(video_frames,dish_union)

            save_data(output_destination, dish_union, fish_pixels, get_video_dimensions(video_src))

            videos_processed += 1

    print(f"processed {videos_processed} video(s)")

if __name__ == "__main__":
    main(DISH_STEP, black_white_threshold)