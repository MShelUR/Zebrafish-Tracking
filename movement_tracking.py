import clean_intermediates
import compress_videos
import process_movement
import visualize_movement

# This script runs all of the other scripts.


# Input:
#   - videos of zebrafish in dishes: copy them to videos/sources
#   - parameters: the variables below, adjust them to best fit your data


# Output:
#   - intermediary files that let some steps be skipped if rerunning this script
#   - results about movement per video file, under the results folder




DEBUG = False


VIDEO_SIZE = 64
COLOR_COMPRESSION_THRESHOLD = 50

DISH_STEP = 10
BLACK_WHITE_THRESHOLD = 127

# if True, deletes all generated files that aren't results
#   - this makes recomputing results take longer to do, but saves some space

DELETE_INTERMEDIATE_FILES = False

compress_videos.main(VIDEO_SIZE, COLOR_COMPRESSION_THRESHOLD)
process_movement.main(DISH_STEP, BLACK_WHITE_THRESHOLD)
visualize_movement.main()

if DELETE_INTERMEDIATE_FILES:
    clean_intermediates.main()