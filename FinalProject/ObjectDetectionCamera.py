# Import packages
import os
import cv2
import numpy as np
from threading import Thread

import subprocess as sp
import numpy
import queue
from tensorflow.lite.python.interpreter import Interpreter

class ObjectDetectionCamera():
    def __init__(self, pipe_name='picamera', model_dir='Sample_TFLite_model'):
        # init queue to store frames
        self.frame_queue = queue.Queue()
        # set pipe
        FFMPEG_BIN = "ffmpeg"
        command = [ FFMPEG_BIN,
                '-i', pipe_name,             # picamera is the named pipe
                '-pix_fmt', 'bgr24',      # opencv requires bgr24 pixel format.
                '-vcodec', 'rawvideo',
                '-an','-sn',              # we want to disable audio processing (there is no audio)
                '-f', 'image2pipe', '-']    
        self.pipe = sp.Popen(command, stdout = sp.PIPE, bufsize=10**8)

        # load model
        self.freq = cv2.getTickFrequency()
        self.modeldir = model_dir
        self.graph_name = 'detect.tflite'
        self.label_name = 'labelmap.txt'
        self.min_conf_threshold = 0.5
        self.imW = 1280
        self.imH = 720

        #Get path to current working directory
        CWD_PATH = os.getcwd()
        # Path to .tflite file, which contains the model that is used for object detection
        PATH_TO_CKPT = os.path.join(CWD_PATH,self.modeldir,self.graph_name)
        # Path to label map file
        PATH_TO_LABELS = os.path.join(CWD_PATH,self.modeldir,self.label_name)

        # Load the label map
        with open(PATH_TO_LABELS, 'r') as f:
            self.labels = [line.strip() for line in f.readlines()]
        # Have to do a weird fix for label map if using the COCO "starter model" from
        # https://www.tensorflow.org/lite/models/object_detection/overview
        # First label is '???', which has to be removed.
        if self.labels[0] == '???':
            del(self.labels[0])

        # Load the Tensorflow Lite model.
        self.interpreter = Interpreter(model_path=PATH_TO_CKPT)
        self.interpreter.allocate_tensors()

        # Get model details
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.height = self.input_details[0]['shape'][1]
        self.width = self.input_details[0]['shape'][2]
        self.floating_model = (self.input_details[0]['dtype'] == np.float32) # False
        self.input_mean = 127.5
        self.input_std = 127.5

    def display(self):
        frame_num=0
        while True:
            if self.frame_queue.empty() != True:
                frame_num+=1
                frame_rate_calc=0
                # Start timer (for calculating frame rate)
                t1 = cv2.getTickCount()

                # Grab frame from video stream
                #frame1 = videostream.read()
                frame1 = self.frame_queue.get()

                # Acquire frame and resize to expected shape [1xHxWx3]
                frame = frame1.copy()
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_resized = cv2.resize(frame_rgb, (self.width, self.height))
                input_data = np.expand_dims(frame_resized, axis=0)


                # Perform the actual detection by running the model with the image as input
                self.interpreter.set_tensor(self.input_details[0]['index'],input_data)
                self.interpreter.invoke()

                # Retrieve detection results
                boxes = self.interpreter.get_tensor(self.output_details[0]['index'])[0] # Bounding box coordinates of detected objects
                classes = self.interpreter.get_tensor(self.output_details[1]['index'])[0] # Class index of detected objects
                scores = self.interpreter.get_tensor(self.output_details[2]['index'])[0] # Confidence of detected objects

                print('Frame_num: ', frame_num)
                print()
                for i in range(len(scores)):
                    if (scores[i] > self.min_conf_threshold) and (scores[i]<=1.0):
                        print('--------------------------------------------------')
                        print(f'Scores[{i}]: ', scores[i] )
                        print(f'Classes[{i}]: ', self.labels[int(classes[i])] )
                        print(f'Boxes[{i}]: ', boxes[i] )
                print()
                
                # Calculate framerate
                t2 = cv2.getTickCount()
                time1 = (t2-t1)/self.freq
                frame_rate_calc= 1/time1
                print('FPS: {0:.2f}'.format(frame_rate_calc))

                # Press 'q' to quit
                if cv2.waitKey(1) == ord('q'):
                    break
    
    def get_frame(self):
        while True:
            # Capture frame-by-frame
            raw_image = self.pipe.stdout.read(640*480*3)
            # transform the byte read into a numpy array
            image =  numpy.frombuffer(raw_image, dtype='uint8')
            try:
                image = image.reshape((480,640,3))  
                self.frame_queue.put(image)        # Notice how height is specified first and then width
            except:
                continue
            self.pipe.stdout.flush()

    def print_all_data(self):
        print('frame_queue: ', self.frame_queue)
        print('pipe: ', self.pipe)
        print('Freq: ', self.freq)
        print('model_dir: ', self.modeldir)
        print('graph_name: ', self.graph_name)
        print('label_name: ', self.label_name)
        print('threshold: ', self.min_conf_threshold)
        print('resolution: ', [self.imW, self.imH])
        print('Labels: ', self.labels)
        print('Interpreter: ', self.interpreter)
        print('input_details: ', self.input_details)
        print('output_details: ', self.output_details)
        print('height: ', self.height)
        print('width: ', self.width)
        print('input_mean: ', self.input_mean)
        print('input_std: ', self.input_std)