import socket
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import datetime
import matplotlib.dates as mdates
from collections import deque
import numpy as np
import ctypes as c
import multiprocessing
import random

HOST = '140.112.71.94'
PORT = 3005

def run_server(sensor_data):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept() 
        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(1024).decode('utf-8')
                print('Received from socket server :')
                data = data.split()
                print(data)
                if len(data) == 8:
                    print("Get data", data)
                    for i in range(1,7):
                        sensor_data[i-1] = float(data[i])
                else:
                    print("Data loss:", data)


if __name__ == '__main__':
    
    HOST = '140.112.71.30'
    PORT = 3005

    sensor_data = multiprocessing.Array('f', 6)
    process1 = multiprocessing.Process(target = run_server, args =([sensor_data]))
    process1.start()


    HISTORY_SIZE = 40
    # INTERVAL = 0.1

    # Deque for X-Axis (time)
    x_vals = deque(maxlen=HISTORY_SIZE)

    # Deque for Y-Axis (accelerometer readings)
    accel_x = deque(maxlen=HISTORY_SIZE)
    accel_y = deque(maxlen=HISTORY_SIZE)
    accel_z = deque(maxlen=HISTORY_SIZE)

    gyro_x = deque(maxlen=HISTORY_SIZE)
    gyro_y = deque(maxlen=HISTORY_SIZE)
    gyro_z = deque(maxlen=HISTORY_SIZE)

    # Create 3 side-by-side subplots
    fig, ((ax1, ax2, ax3), (gx1, gx2, gx3)) = plt.subplots(2,3)

    # Automatically adjust subplot parameters for nicer padding between plots
    plt.tight_layout()


    def animate(i, sensor_data):
        # Poll the LSM303AGR
        # accel_data = [random.random(), random.random(), random.random()]
        print(sensor_data[0], sensor_data[1], sensor_data[2], sensor_data[3], sensor_data[4], sensor_data[5])
        accel_data = sensor_data[:3]
        gyro_data = sensor_data[3:6]
        # print(factor)
        # gyro_data = 
        # Add the X/Y/Z values to the accel arrays
        accel_x.append(accel_data[0])
        accel_y.append(accel_data[1])
        accel_z.append(accel_data[2])
        
        gyro_x.append(gyro_data[0])
        gyro_y.append(gyro_data[1])
        gyro_z.append(gyro_data[2])

        # Grab the datetime, auto-range based on length of accel_x array
        x_vals = [datetime.datetime.now() + datetime.timedelta(seconds=i) for i in range(len(accel_x))]

        # Clear all axis
        ax1.cla()
        ax2.cla()
        ax3.cla()

        gx1.cla()
        gx2.cla()
        gx3.cla()

        # Set grid titles
        ax1.set_title('acc X', fontsize=10)
        ax2.set_title('acc Y', fontsize=10)
        ax3.set_title('acc Z', fontsize=10)

        gx1.set_title('gyro X', fontsize=10)
        gx2.set_title('gyro Y', fontsize=10)
        gx3.set_title('gyro Z', fontsize=10)

        # Enable subplot grid lines
        ax1.grid(True, linewidth=0.5, linestyle=':')
        ax2.grid(True, linewidth=0.5, linestyle=':')   
        ax3.grid(True, linewidth=0.5, linestyle=':')

        gx1.grid(True, linewidth=0.5, linestyle=':')
        gx2.grid(True, linewidth=0.5, linestyle=':')   
        gx3.grid(True, linewidth=0.5, linestyle=':')

        # Display the sub-plots
        ax1.plot(x_vals, accel_x, color='r')
        ax2.plot(x_vals, accel_y, color='g')
        ax3.plot(x_vals, accel_z, color='b')

        gx1.plot(x_vals, gyro_x, color='r')
        gx2.plot(x_vals, gyro_y, color='g')
        gx3.plot(x_vals, gyro_z, color='b')

        # Pause the plot for INTERVAL seconds 
        plt.pause(0.1)

    ani = FuncAnimation(fig, animate, fargs=([sensor_data]))
    plt.show()
