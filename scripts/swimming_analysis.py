'''
Basic analysis of swimming trajectories.
Count, speed and AR rate.
Note that thigmotactic cells may give high rates of AR.

TODO: save tables and statistics
'''
import pandas as pd
from pylab import *
import os
from trajectories.trajectory_analysis import *
from trajectories.visualization import *
from trajectories.magic_loading import *
import numpy as np
import concurrent.futures
from time import time
from interface import *
import matplotlib.pyplot as plt
from trajectories.linking import *
import logging

logging.basicConfig(level=logging.WARNING)

## Choose the swimming tracking file
filename = ask_open_tracking_file(title='Choose a swimming tracking file')

## Parameters
# Here I could automatically get the number of images per background from tiff filenames
fps, pixel_size = guess_fps_and_pixelsize(filename)
parameters = [('fps', 'Frame rate (Hz)', fps or 10.),
              ('pixel_size', 'Pixel size (µm)', pixel_size or 1.),
              ('window_size', 'Analysis window size (frames)', 300) # this can be obtained from the settings.yaml file, background/recalculated every
              ]
P = ParametersDialog(title='Enter parameters', parameters=parameters).value
fps, pixel_size= P['fps'], P['pixel_size']
window_size = int(P['window_size'])
dt = 1/fps

## Load tracking file, only the first chunk
print("Loading swimming cells")
data = magic_load_trajectories(filename)
scale_lengths(data, pixel_size)

data['speed'] *= pixel_size
data['angular_speed'] = np.abs(data['angular_speed'])

## Time scale (this could be refactored in plots)
if data['frame'].max()*dt>3*3600: # 3 h
    time_scale, time_label = 3600, 'h'
elif data['frame'].max()*dt>3*60.: # 3 min
    time_scale, time_label = 60, 'min'
else:
    time_scale, time_label = 1, 's'

## Process data in ROI
def process_ROI(x1, y1, x2, y2):
    ROI = data[(data['x'] >= x1) & (data['x'] <= x2) & (data['y'] >= y1) & (data['y'] <= y2)]
    ROI.sort_values(by='frame')
    ROI_frames = ROI.groupby('frame')

    ## Number of cells vs. time
    fig, (ax0, ax1, ax2, ax3) = plt.subplots(nrows=4, ncols=1, sharex=True)
    count = ROI_frames['frame'].count().to_numpy()
    count = count[:(len(count)//window_size)*window_size]
    count = count.reshape((len(count)//window_size, window_size)).max(axis=1)
    t = np.arange(count.shape[0])*dt*window_size
    ax0.plot(t/time_scale, count)
    ax0.set_ylim(bottom=0)
    ax0.set_ylabel('Cell count')

    ## Speed vs. time
    speed = ROI_frames['speed'].mean().to_numpy()
    speed = speed[:(len(speed)//window_size)*window_size]
    speed = np.nanmean(speed.reshape((len(speed)//window_size, window_size)), axis=1)
    ax1.plot(t/time_scale, speed/dt)
    ax1.set_ylim(bottom=0)
    ax1.set_ylabel('Speed (um/s)')

    ## Angular speed vs. time
    speed = ROI_frames['angular_speed'].mean().to_numpy()
    speed = speed[:(len(speed)//window_size)*window_size]
    speed = np.nanmean(speed.reshape((len(speed)//window_size, window_size)), axis=1)
    ax2.plot(t/time_scale, speed/dt)
    ax2.set_ylim(bottom=0)
    ax2.set_ylabel('Angular speed (rad/s)')

    ## AR rate vs. time
    AR = ROI_frames['mAR_start'].mean().to_numpy()
    AR = AR[:(len(AR)//window_size)*window_size]
    AR = np.nanmean(AR.reshape((len(AR)//window_size, window_size)), axis=1)
    ax3.plot(t/time_scale, AR/dt)
    ax3.set_ylim(bottom=0)
    ax3.set_xlabel(f'Time ({time_label})')
    ax3.set_ylabel('AR rate (Hz)')

    plt.show()

## Select a ROI
segments = trajectories_from_table(data[data['frame']<60./dt]) # Show the first minute
ROI_plot = TrajectoryPlot(segments, onselect=process_ROI)
plt.show()
