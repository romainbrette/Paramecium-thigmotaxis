'''
Analysis of trajectories obtained with FastTrack

Fields of trajectory files:
xHead	yHead	tHead	xTail	yTail	tTail	xBody	yBody	tBody	curvature	areaBody	perimeterBody	headMajorAxisLength	headMinorAxisLength	headExcentricity	tailMajorAxisLength	tailMinorAxisLength	tailExcentricity	bodyMajorAxisLength	bodyMinorAxisLength	bodyExcentricity	imageNumber	id
'''
from numpy import *
from pandas import *
from scipy.signal import medfilt
import numpy as np
import pandas as pd

__all__ = ['fasttrack_to_table', 'load_fasttrack']

def fasttrack_to_table(table):
    # Transforms a fasttrack table into a table with standard readable variables
    return pd.DataFrame(data={'x': table['xBody'],
                               'y': table['yBody'],
                               'angle': np.pi - table['tBody'],  # the angle is inverted (head/tail swap)
                               'length': table['bodyMajorAxisLength'],
                               'width': table['bodyMinorAxisLength'],
                               'eccentricity': table['bodyExcentricity'],
                               'frame': table['imageNumber'],
                               'id': table['id']})

def load_fasttrack(filename):
    return fasttrack_to_table(pd.read_csv(filename, sep='\t'))

### For debugging
def fasttrack_angle(filename):
    # Calculate angle directly
    table = pd.read_csv(filename, sep='\t')
    cx, cy = table['xHead'] - table['xTail'], table['yHead'] - table['yTail']  # cell axis
    cx, cy = -cx, -cy # head/tail are reversed
    return np.arctan2(cy, cx)
