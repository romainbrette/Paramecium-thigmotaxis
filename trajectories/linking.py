'''
Trajectory linking

You can use predictors:
https://soft-matter.github.io/trackpy/v0.6.2/tutorial/prediction.html

trackpy is slower with numba!

TODO:
- predict with trackpy; unfortunately, the code is hardly readable
- use btrack
- augmentation: remove frames
- custom distance function with the inertia matrix
    use Frobenius norm on the inertia matrix (rotation invariant)
    diagonals are Mb^2/4 and Ma^2/4
    then RIR^T
    we must then dimension correctly given that it is quadratic

An implementation of Kalman filter + linking here:
https://github.com/mabhisharma/Multi-Object-Tracking-with-Kalman-Filter

Another option is SORT, similar but probably a bit more advanced:
https://github.com/abewley/sort/blob/master/sort.py
'''
import pandas as pd
import numpy as np
import warnings
from trajectories.trajectory_analysis import *
import random
from tqdm import tqdm

try:
    import trackpy as tp
except ImportError:
    warnings.warn("Trackpy is not available")
import time
try:
    import norfair
except ImportError:
    warnings.warn("Norfair is not available")

def norfair_track(trajectories, distance_threshold=30, memory=10, delay=0, velocity=False):
    '''
    Track objects identified in `trajectories` using Norfair.
    '''
    tracker = norfair.Tracker(distance_function="euclidean", distance_threshold=distance_threshold,
                              initialization_delay=delay, hit_counter_max=memory)

    if velocity: # Kalman based estimate
        trajectories['vx_kalman'] = 0.
        trajectories['vy_kalman'] = 0.
        trajectories['speed_kalman'] = 0.

    output = []
    nframes = trajectories['frame'].max()+1
    with tqdm(total=nframes, desc="Tracking") as pbar:
        for frame, rows in trajectories.groupby('frame'):
            norfair_detections = [norfair.Detection(points=np.array([row['x'], row['y']]), data=row) for _, row in rows.iterrows()]
            tracked_objects = tracker.update(detections=norfair_detections)
            for object in tracked_objects:
                last_detection = object.last_detection.data
                if last_detection['frame'] == frame: ## the last detection could be far in the past
                    row = last_detection.to_dict()
                    row.update({'id' : object.id})
                    if velocity:
                        vx, vy = object.estimate_velocity[0] # This is quite slow
                        row.update({'vx_kalman' : vx, 'vy_kalman' : vy, 'speed_kalman' : (vx**2 + vy**2)**.5})
                    output.append(row)
            pbar.update(1)
    return pd.DataFrame(output) # this line is actually quite slow

def trackpy_track(trajectories, search_range=40, memory=0):
    '''
    Track objects identified in `trajectories` using Trackpy.
    '''
    t = tp.link(trajectories, search_range=search_range, memory=memory, link_strategy='numba', adaptive_stop=search_range/2) # max pixel distance, max number of hidden frames
    #trajectories['id'] = t['particle']
    #return trajectories
    t['id'] = t['particle']
    return t

def tracking_quality(id, ground_truth_id):
    '''
    Evaluate the tracking quality with reference to a ground truth assignment.

    The arguments are just lists of ids, for each frame/object, corresponding to the pandas column `id`.
    For each ground truth trajectory, we count the number of ids in the data.

    Returns the average number of attribution errors per trajectory.
    '''
    table = pd.DataFrame({'id' : id,
                          'ground_truth' : ground_truth_id})
    return table.groupby('ground_truth')['id'].nunique().mean() - 1

def augment_tracks(data, n):
    '''
    Generate synthetic tracks by rotations, translations and temporal shifts.
    '''
    translation_range = (.5*(data['x'].var() + data['y'].var()))**.5 # one standard deviation
    cx, cy = data['x'].mean(), data['y'].mean()
    nframes = data['frame'].max()+1

    trajectories = trajectories_from_table(data)

    df = pd.DataFrame()
    for i in range(n):
        # Pick a random trajectory
        trajectory = trajectories[random.randint(0,len(trajectories)-1)].copy()

        trajectory['id'] = i

        # Rotation
        theta = 2*np.random.rand()*np.pi
        vx, vy = (trajectory['x']-cx), (trajectory['y']-cy)
        trajectory['x'] = vx*np.cos(theta)-vy*np.sin(theta)+cx
        trajectory['y'] = vx*np.sin(theta)+vy*np.cos(theta)+cy

        # Translation
        trajectory['x'] += (2*np.random.rand()-1)*translation_range
        trajectory['y'] += (2*np.random.rand()-1)*translation_range

        # Temporal shift
        #trajectory['frame'] = (trajectory['frame'] + random.randint(nframes)) % nframes
        # I need to split the trajectory in two

        df = pd.concat([df, trajectory], axis=0)
        df = df.sort_values(by='frame')

    return df

if __name__ == '__main__':
    ## Tracking with trackpy
    from trajectories.fasttrack import load_fasttrack
    f = load_fasttrack('/Users/romainbrette/Downloads/Single cells #1/Tracking_Result_Basler a2A5320-23umBAS (40311059)_20240419_110749085/tracking.txt')
    t1 = time.time()
    t = tp.link(f, 40, memory=0, link_strategy='numba') # max pixel distance, max number of hidden frames
    t2 = time.time()
    print(f['frame'].max()/(t2-t1), "Hz")
    f['id'] = t['particle']
