import ast
import os

import json

def verify_data_folders_exist():
    if not os.path.exists('data'):
        os.mkdir('data')

    if not os.path.exists('data/videos'):
        os.mkdir('data/videos')
        
    if not os.path.exists('data/videos/compressed_sources'):
        os.mkdir('data/videos/compressed_sources')

    if not os.path.exists('data/videos/binary_sources'):
        os.mkdir('data/videos/binary_sources')

# cast dish and fish objects to string and save them
def save_data(output_folder, dish, fish, scale):

    try:
        os.mkdir(output_folder)
    except FileExistsError:
        pass # folder is already there, this is okay.
    except FileNotFoundError:
        verify_data_folders_exist()
        os.mkdir(output_folder)

    dish_pixels_str = [str(pixel) for pixel in dish]
    dish_output = json.dumps(dish_pixels_str, indent=4)

    fish_pixels_str = [json.dumps([str(pixel) for pixel in x]) for x in fish]
    fish_output = json.dumps(fish_pixels_str, indent=4)

    with open(output_folder+"/dish_pixels.json", 'w') as out_file:
        out_file.write(dish_output)
        
    with open(output_folder+"/fish_pixels.json", 'w') as out_file:
        out_file.write(fish_output)

    with open(output_folder+"/scale.txt", "w") as out_file:
        out_file.write(str(scale[0]))

    print(f"saved output to {output_folder}")

# load dish and fish objects from save files
def load_data(input_folder):
    if not os.path.isdir(input_folder):
        raise FileNotFoundError(f"missing data folder: {input_folder}")
    
    dish_file = input_folder+"/dish_pixels.json"
    fish_file = input_folder+"/fish_pixels.json"

    if not os.path.isfile(dish_file) or not os.path.isfile(fish_file):
        raise FileNotFoundError(f"{input_folder} is missing data files")
    
    dish = {}
    fish = []

    with open(dish_file,"r") as dish_input:
        dish_list = json.loads(dish_input.read())

        for value in dish_list:
            dish[ast.literal_eval(value)] = True

    with open(fish_file,"r") as fish_input:
        fish_frame_list = json.loads(fish_input.read())

        for frame in fish_frame_list:
            fish_list = json.loads(frame)
            fish_list = [ast.literal_eval(pixel) for pixel in fish_list]

            fish_dict = {}

            for value in fish_list:
                fish_dict[value] = True

            fish.append(fish_dict)

    return dish, fish

def get_saved_data_from_video(video_src):
    data_path = "data/"+video_src.removeprefix('data/videos/binary_sources/').removesuffix('.mp4')
    dish_union, fish_pixels = load_data(data_path)
    return dish_union, fish_pixels

# loads scale file, which is just an int
def load_scale(input_folder):
    with open(input_folder+"/scale.txt","r") as in_file:
        return int(in_file.read())