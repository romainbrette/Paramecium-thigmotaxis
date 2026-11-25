'''
Splits a trajectory file in different ROIs.
Select the ROI with the mouse, and a new trajectory file is created.
Do it for all ROI.
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
root, ext = os.path.splitext(filename)

## Load tracking file, only the first chunk
print("Loading swimming cells")
data = magic_load_trajectories(filename)

current_n = 1

## Process data in ROI
def process_ROI(x1, y1, x2, y2):
    global current_n
    ROI = data[(data['x'] >= x1) & (data['x'] <= x2) & (data['y'] >= y1) & (data['y'] <= y2)]
    ROI.sort_values(by='frame')
    new_filename = root+'_'+str(current_n)+ext
    current_n += 1
    # Save it now
    print("Saving to", new_filename)
    ROI.to_csv(new_filename, sep="\t", index=False)
    print('Done')

## Select a ROI
segments = trajectories_from_table(data.head(100000)) # Show the beginning
ROI_plot = TrajectoryPlot(segments, onselect=process_ROI)
plt.show()
