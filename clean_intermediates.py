import os

# this file deletes intermediate files and folders.
#   - NOTE: please don't save anything important to the data folder


def main():
    for file in os.listdir("source_videos"):
        data_folder = "data/"+file.removesuffix('.mp4')
        compressed_video = "data/videos/compressed_sources/"+file
        binary_video = "data/videos/binary_sources/"+file

        if os.path.exists(data_folder):
            for data_file in ('dish_pixels.json','fish_pixels.json','scale.txt'):
                full_data_file = data_folder+"/"+data_file
                if os.path.exists(full_data_file):
                    os.remove(full_data_file)
            os.rmdir(data_folder)

        for video in (compressed_video,binary_video):
            if os.path.exists(video):
                os.remove(video)

if __name__ == "__main__":
    main()