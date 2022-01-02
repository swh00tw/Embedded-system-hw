# -------------------------------------------------------------- #
#                      USELESS & DEPRECATED                      #
# -------------------------------------------------------------- #

# Import packages
import os
import argparse
import cv2
import numpy as np
import sys
import time
from threading import Thread
import importlib.util

import subprocess as sp
import numpy
import queue
from tensorflow.lite.python.interpreter import Interpreter

#for frame1 in camera.capture_continuous(rawCapture, format="bgr",use_video_port=True):
def display(q):
    frame_num=0
    while True:
        if q.empty() != True:
            frame_num+=1
            frame_rate_calc=0
            # Start timer (for calculating frame rate)
            t1 = cv2.getTickCount()

            # Grab frame from video stream
            #frame1 = videostream.read()
            frame1 = q.get()

            # Acquire frame and resize to expected shape [1xHxWx3]
            frame = frame1.copy()
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb, (width, height))
            input_data = np.expand_dims(frame_resized, axis=0)

            # Normalize pixel values if using a floating model (i.e. if model is non-quantized)
            if floating_model: # False
                input_data = (np.float32(input_data) - input_mean) / input_std

            # Perform the actual detection by running the model with the image as input
            interpreter.set_tensor(input_details[0]['index'],input_data)
            interpreter.invoke()

            # Retrieve detection results
            boxes = interpreter.get_tensor(output_details[0]['index'])[0] # Bounding box coordinates of detected objects
            classes = interpreter.get_tensor(output_details[1]['index'])[0] # Class index of detected objects
            scores = interpreter.get_tensor(output_details[2]['index'])[0] # Confidence of detected objects

            print('Frame_num: ', frame_num)
            # print()
            # for i in range(len(scores)):
            #     if (scores[i] > min_conf_threshold) and (scores[i]<=1.0):
            #         print('--------------------------------------------------')
            #         print(f'Scores[{i}]: ', scores[i] )
            #         print(f'Classes[{i}]: ', labels[int(classes[i])] )
            #         print(f'Boxes[{i}]: ', boxes[i] )
            # print()
            
            # Calculate framerate
            t2 = cv2.getTickCount()
            time1 = (t2-t1)/freq
            frame_rate_calc= 1/time1
            print('FPS: {0:.2f}'.format(frame_rate_calc))

            # Press 'q' to quit
            if cv2.waitKey(1) == ord('q'):
                break

def get_frame(pipe,q):
    while True:
        # Capture frame-by-frame
        raw_image = pipe.stdout.read(640*480*3)
        # transform the byte read into a numpy array
        image =  numpy.frombuffer(raw_image, dtype='uint8')
        try:
            image = image.reshape((480,640,3))  
            q.put(image)        # Notice how height is specified first and then width
        except:
            continue
        pipe.stdout.flush()

if __name__ == "__main__":
    # Define and parse input arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--modeldir', help='Folder the .tflite file is located in',
                        required=True)
    parser.add_argument('--graph', help='Name of the .tflite file, if different than detect.tflite',
                        default='detect.tflite')
    parser.add_argument('--labels', help='Name of the labelmap file, if different than labelmap.txt',
                        default='labelmap.txt')
    parser.add_argument('--threshold', help='Minimum confidence threshold for displaying detected objects',
                        default=0.5)
    parser.add_argument('--resolution', help='Desired webcam resolution in WxH. If the webcam does not support the resolution entered, errors may occur.',
                        default='1280x720')
    parser.add_argument('--edgetpu', help='Use Coral Edge TPU Accelerator to speed up detection',
                        action='store_true')

    args = parser.parse_args()

    MODEL_NAME = args.modeldir
    GRAPH_NAME = args.graph
    LABELMAP_NAME = args.labels
    min_conf_threshold = float(args.threshold)
    resW, resH = args.resolution.split('x')
    imW, imH = int(resW), int(resH)
    use_TPU = args.edgetpu
    # print("use_TPU: ",use_TPU) # False

    # Import TensorFlow libraries
    # If tflite_runtime is installed, import interpreter from tflite_runtime, else import from regular tensorflow
    # If using Coral Edge TPU, import the load_delegate library
    pkg = importlib.util.find_spec('tflite_runtime')
    # print('pkg: ',pkg) # None
    if pkg:
        from tflite_runtime.interpreter import Interpreter
        if use_TPU:
            from tflite_runtime.interpreter import load_delegate
    else:
        from tensorflow.lite.python.interpreter import Interpreter
        if use_TPU:
            from tensorflow.lite.python.interpreter import load_delegate

    # If using Edge TPU, assign filename for Edge TPU model
    if use_TPU:
        # If user has specified the name of the .tflite file, use that name, otherwise use default 'edgetpu.tflite'
        if (GRAPH_NAME == 'detect.tflite'):
            GRAPH_NAME = 'edgetpu.tflite'       

    # Get path to current working directory
    CWD_PATH = os.getcwd()

    # Path to .tflite file, which contains the model that is used for object detection
    PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME,GRAPH_NAME)

    # Path to label map file
    PATH_TO_LABELS = os.path.join(CWD_PATH,MODEL_NAME,LABELMAP_NAME)

    # Load the label map
    with open(PATH_TO_LABELS, 'r') as f:
        labels = [line.strip() for line in f.readlines()]

    # Have to do a weird fix for label map if using the COCO "starter model" from
    # https://www.tensorflow.org/lite/models/object_detection/overview
    # First label is '???', which has to be removed.
    if labels[0] == '???':
        del(labels[0])

    # Load the Tensorflow Lite model.
    # If using Edge TPU, use special load_delegate argument
    if use_TPU:
        interpreter = Interpreter(model_path=PATH_TO_CKPT,
                                experimental_delegates=[load_delegate('libedgetpu.so.1.0')])
        print(PATH_TO_CKPT)
    else:
        interpreter = Interpreter(model_path=PATH_TO_CKPT)

    interpreter.allocate_tensors()

    # Get model details
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    height = input_details[0]['shape'][1]
    width = input_details[0]['shape'][2]

    floating_model = (input_details[0]['dtype'] == np.float32)
    # print("Floating-model: ",floating_model) # False

    input_mean = 127.5
    input_std = 127.5

    # Initialize frame rate calculation
    freq = cv2.getTickFrequency()

    FFMPEG_BIN = "ffmpeg"
    command = [ FFMPEG_BIN,
            '-i', 'picamera',             # picamera is the named pipe
            '-pix_fmt', 'bgr24',      # opencv requires bgr24 pixel format.
            '-vcodec', 'rawvideo',
            '-an','-sn',              # we want to disable audio processing (there is no audio)
            '-f', 'image2pipe', '-']    
    pipe = sp.Popen(command, stdout = sp.PIPE, bufsize=10**8)

    q = queue.Queue()
    thread2 = Thread(target=get_frame, args=[pipe,q])
    thread2.start()
    display(q)

# Clean up
cv2.destroyAllWindows()
#videostream.stop()
