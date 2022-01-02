# Import packages
import os
import argparse
import cv2
import numpy as np
from threading import Thread
import importlib.util

import subprocess as sp
import queue
from ObjectDetectionCamera import ObjectDetectionCamera

camera = ObjectDetectionCamera('picamera', 'Sample_TFLite_model')
thread2 = Thread(target=camera.get_frame)
thread2.start()
camera.display()

# Clean up
cv2.destroyAllWindows()
#videostream.stop()
