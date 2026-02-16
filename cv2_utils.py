import cv2


# this script is just a bunch of utilities for handling videos



# turn cv2 video into a list of frames
def cast_video_to_frame_list(source):
    cv_video = cv2.VideoCapture(source)
    if not cv_video.isOpened():
        raise FileNotFoundError(f"could not find file: {source}")
    
    frames = []

    while True:
        ret, next_frame = cv_video.read()
        if not ret: # no next frame, end
            break
        
        frames.append(next_frame)

    cv_video.release()

    return frames

# display a frame w/ optional timer for next frame
def show_frame(frame, size, timestep=None):
    upscaled_frame = cv2.resize(frame,size, interpolation=cv2.INTER_NEAREST_EXACT)

    cv2.imshow('Zebrafish Movement Tracking (q to exit)', upscaled_frame)

    if cv2.waitKey(timestep) & 0xFF == ord('q'):
        return True
    
def make_black_white_video(in_file, out_file, scale, threshold):
    cv_input = cv2.VideoCapture(in_file)
    if not cv_input.isOpened():
        raise FileNotFoundError(f"could not find file: {in_file}")
    
    cv_fps = int(cv_input.get(cv2.CAP_PROP_FPS))

    # make the codec
    cv_output = cv2.VideoWriter(out_file, cv2.VideoWriter_fourcc(*'mp4v'), cv_fps, (scale, scale), isColor=False)

    while True:
        ret, next_frame = cv_input.read()
        if not ret: # no next frame, end
            break

        # make frame greyscale
        next_frame_greyscale = cv2.cvtColor(next_frame, cv2.COLOR_BGR2GRAY)

        # apply pixel threshold
        #   (frame, threshold, color for above threshold, type of threshold)
        _, next_frame_binary_color = cv2.threshold(next_frame_greyscale, threshold, 255, cv2.THRESH_BINARY)

        # write new frame
        cv_output.write(next_frame_binary_color)

    cv_input.release()
    cv_output.release()

def get_video_dimensions(source):
    cv_video = cv2.VideoCapture(source)
    if not cv_video.isOpened():
        raise FileNotFoundError(f"could not find file: {source}")
    
    width = int(cv_video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cv_video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    cv_video.release()

    return width, height
