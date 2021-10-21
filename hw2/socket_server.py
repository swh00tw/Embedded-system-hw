import socket

# import numpy as np
import json
import time
import random

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import datetime
import matplotlib.dates as mdates
from collections import deque
import random
import threading
import multiprocessing as mp

l = [0, 0, 0]

HISTORY_SIZE = 20
INTERVAL = 0.1

# Deque for X-Axis (time)
x_vals = deque(maxlen=HISTORY_SIZE)

# Deque for Y-Axis (accelerometer readings)
accel_x = deque(maxlen=HISTORY_SIZE)
accel_y = deque(maxlen=HISTORY_SIZE)
accel_z = deque(maxlen=HISTORY_SIZE)

# Create 3 side-by-side subplots
fig, (ax1, ax2, ax3) = plt.subplots(1, 3)

# Automatically adjust subplot parameters for nicer padding between plots
plt.tight_layout()


def animate(i, factor):
    # Poll the LSM303AGR
    # accel_data = [random.random(), random.random(), random.random()]
    accel_data = factor
    # gyro_data =
    # Add the X/Y/Z values to the accel arrays
    accel_x.append(accel_data[0])
    accel_y.append(accel_data[1])
    accel_z.append(accel_data[2])

    # Grab the datetime, auto-range based on length of accel_x array
    x_vals = [datetime.datetime.now() + datetime.timedelta(seconds=i)
              for i in range(len(accel_x))]

    # Clear all axis
    ax1.cla()
    ax2.cla()
    ax3.cla()

    # Set grid titles
    ax1.set_title('X', fontsize=10)
    ax2.set_title('Y', fontsize=10)
    ax3.set_title('Z', fontsize=10)

    # Enable subplot grid lines
    ax1.grid(True, linewidth=0.5, linestyle=':')
    ax2.grid(True, linewidth=0.5, linestyle=':')
    ax3.grid(True, linewidth=0.5, linestyle=':')

    # Display the sub-plots
    ax1.plot(x_vals, accel_x, color='r')
    ax2.plot(x_vals, accel_y, color='g')
    ax3.plot(x_vals, accel_z, color='b')

    # Pause the plot for INTERVAL seconds
    plt.pause(INTERVAL)


def server(l):
    HOST = '140.112.87.110'
    PORT = 3000

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print('server starting...')
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            # plt.show()
            while True:
                data = conn.recv(1024).decode('utf-8')
                print('Received from socket server : \n', data)
                data = data.split()
                l[0], l[1], l[2] = data[0], data[1], data[2]


def draw():
    ani = FuncAnimation(fig, animate, fargs=[[0.1, 0.2, 0.3]])
    plt.show()


p_list = []
p1 = mp.Process(target=server, args=(l))
p_list.append(p1)
