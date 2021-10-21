import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import datetime
import matplotlib.dates as mdates
from collections import deque
import random

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


ani = FuncAnimation(fig, animate, fargs=[[0.1, 0.2, 0.3]])
plt.show()
