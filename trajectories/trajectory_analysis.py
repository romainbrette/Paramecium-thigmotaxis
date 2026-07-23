'''
Analysis of trajectories.

Trajectories have the following variables:
    x
    y
    angle
    length
    width
    eccentricity
    frame
    id

TODO and notes:
    - Careful: AR from motion cannot distinguish between the start and end of an AR.
'''
import pandas as pd
import numpy as np
from numpy import nan
from matplotlib.collections import LineCollection
import matplotlib.pyplot as plt
from numpy.fft import fft, fftfreq
from skimage import measure, morphology

def check_missing_frames(data):
    '''
    Check whether some frames are missing.
    '''
    frames = data['frame'].unique()
    return not (np.diff(frames)==1).all()

def sliding_average(arr, window_size):
    # Compute the sliding window average
    cumsum = np.cumsum(np.insert(arr, 0, 0))  # Cumulative sum
    return (cumsum[window_size:] - cumsum[:-window_size]) / window_size

def filter_shape(table, length=(10., 220.), width=(8., 120.)):
    '''
    Filters based on length and width.
    `length` and `width` are tuples.
    Default values assume um.
    '''
    if length is None: # automatic
        length = table['length'].median()
        length_min, length_max = length*.5, length*1.5
        width = table['width'].median()
        width_min, width_max = width*.5, width*2
        print("Median length:",length)
        print("Median width:", width)
    else:
        length_min, length_max = length
        width_min, width_max = width

    return table[(table['length']>=length_min) & (table['length']<=length_max) & (table['width']>=width_min) & (table['width']<=width_max)]

def split_into_regions(table, regions):
    '''
    Split the table into regions of interest.
    Each region is a list of (x1, y1, x2, y2) coordinates.
    '''
    tables = []
    for (x1, y1, x2, y2) in regions:
        tables.append(table[(table['x']>=x1) & (table['x']<=x2) & (table['y']>=y1) & (table['y']<=y2)])
    return tables

def tag_regions(table, regions):
    '''
    Tag regions of interest.
    Each region is a list of (x1, y1, x2, y2) coordinates.
    '''
    if "ROI" not in table:
        table['ROI'] = 0
    for i, (x1, y1, x2, y2) in enumerate(regions):
        table.loc[(table['x']>=x1) & (table['x']<=x2) & (table['y']>=y1) & (table['y']<=y2), 'ROI'] = i+1

def automatic_regions(table, resolution=1000., convex_hull = False):
    '''
    Clusters trajectories into regions of interest.
    Trajectories are placed on a grid with resolution 'resolution'
    (um if scaled, otherwise pixel).
    If `convex_hull` is True, finds smallest convex regions.
    Region number is stored in column `ROI`.
    '''
    # Draw trajectories on a grid
    xmin, xmax = table['x'].min(), table['x'].max()
    ymin, ymax = table['y'].min(), table['y'].max()
    j = ((table['x'] - xmin) // resolution).astype(int)
    i = ((table['y'] - ymin) // resolution).astype(int)
    field = np.zeros((i.max()+1, j.max()+1), dtype=bool)
    field[i, j] = True

    # Get connected regions
    regions, num = measure.label(field, background=False, connectivity=2, return_num=True)

    if convex_hull:
        # Convex hull of each region
        for i in range(num):
            region = morphology.convex_hull_image(regions==i+1)
            field[region] = True

        # Get connected regions again
        regions, num = measure.label(field, background=False, connectivity=2, return_num=True)

    # Assign labels
    table['ROI'] = regions[i, j]

    return table

def trajectories_from_table(big_table):
    # Transforms a big dataset into a list of tables, one per trajectory
    # Copies are returned(not views).
    return [pd.DataFrame(traj) for id, traj in big_table.groupby('id', sort=True)]

def segments_from_trajectory(traj):
    # Extracts uninterrupted segments from a trajectory
    # Copies are returned(not views).
    breaks = list(1+(np.diff(traj['frame'] ) > 1).nonzero()[0]) + [len(traj)]
    n = 0
    segments = []
    for i in breaks:
        segment = pd.DataFrame(traj.iloc[n:i])
        if len(segment)>2: # otherwise we can't do any calculation
            segments.append(segment)
        n = i
    return segments

def segments_from_table(table):
    # Extracts a list of uninterrupted segments from a table
    # Copies are returned(not views).
    segments = []
    for _, traj in table.groupby('id', sort=True):
        breaks = list(1+(np.diff(traj['frame'] ) > 1).nonzero()[0]) + [len(traj)]
        n = 0
        for i in breaks:
            segment = pd.DataFrame(traj.iloc[n:i])
            if len(segment) > 2:  # otherwise we can't do any calculation
                segments.append(segment)
            n = i
    return segments

def scale_lengths(table, pixel_size):
    # Convert lengths from pixel to um using pixel_size (in um/pixel)
    if pixel_size != 1:
        table['x'] = table['x']*pixel_size
        table['y'] = table['y']*pixel_size
        if 'z' in table:
            table['z'] = table['z'] * pixel_size
        table['length'] = table['length']*pixel_size
        if 'width' in table:
            table['width'] = table['width']*pixel_size

def calculate_features(segment):
    '''
    Calculate trajectory features for a contiguous segment:
    - vx (velocity)
    - vy
    - speed
    - ax (acceleration)
    - ay
    - motion_reversal (dot product between two successive velocity vectors)
    - reversal (dot product between motion vector and angle)
    - angular speed (angle is modulo pi)
    '''
    if len(segment)>2:
        vx, vy = np.diff(segment['x']), np.diff(segment['y'])
        segment['vx'] = np.hstack([vx, nan])
        segment['vy'] = np.hstack([vy, nan])
        speed = (vx**2 + vy**2)**.5
        segment['speed'] = np.hstack([speed, nan])

        segment['ax'] = np.hstack([nan, np.diff(np.diff(segment['x'])), nan])
        segment['ay'] = np.hstack([nan, np.diff(np.diff(segment['y'])), nan])
        segment['acceleration'] = (segment['ax']**2 + segment['ay']**2)**.5

        segment['motion_reversal'] = np.hstack([nan, (vx[1:]*vx[:-1] + vy[1:]*vy[:-1])/ (speed[1:]*speed[:-1]), nan])
        segment['reversal'] = segment['vx']*np.cos(segment['angle']) + segment['vy']*np.sin(segment['angle'])

        angle = segment['angle']
        angular_speed = ((np.diff(angle) + np.pi / 2) % np.pi) - np.pi / 2
        segment['angular_speed'] = np.hstack([ angular_speed, nan])
    return segment

def calculate_mean_displacement(table):
    '''
    Subtract the mean displacement over all cells on each frame.

    Doesn't work.
    '''
    # Calculate mean displacement
    segments = segments_from_table(table)
    for segment in segments:
        if len(segment) > 2:
            vx, vy = np.diff(segment['x']), np.diff(segment['y'])
            segment['vx'] = np.hstack([vx, nan])
            segment['vy'] = np.hstack([vy, nan])
    table = pd.concat(segments)
    mean_table = table.groupby('frame').mean()
    table['mean_vx'] = mean_table['vx']
    table['mean_vy'] = mean_table['vy']
    return table.sort_values(by='frame') # useful?

def calculate_vertical_angle(segment):
    '''
    Calculates vertical angle (with respect to focal plane),
    assuming the cell is planar at some point.
    This probably doesn't work when far from the focal plane.
    I'm also not sure about the formula.
    '''
    # Vertical angle calculation
    length = segment['length'].mean() # could be the median or max instead
    width = segment['width'].mean()
    segment['vertical_angle'] = np.arccos(((length**2-segment['length']**2)/(length**2-width**2))**.5)

def planar_segments(segment, threshold=0.75):
    '''
    Extract segments within the horizontal plane, with the given eccentricity threshold.
    Copies are returned(not views).
    Works on segments or trajectories.
    '''
    frames = 1 + np.diff(segment['eccentricity'] > threshold).nonzero()[0] # frame numbers in horizontal plane
    breaks = list(1+(np.diff(frames) > 1).nonzero()[0]) + [len(segment)]
    n = 0
    segments = []
    for i in breaks:
        segments.append(pd.DataFrame(segment.iloc[n:i]))
        n = i
    return segments

def is_circular(segment, threshold=0.9):
    '''
    Returns true if the trajectory is circular.
    The idea is that a circular trajectory always turns in the same direction
    (clockwise or anticlockwise).

    Features must have been calculated.
    '''
    p_clockwise= (segment['angular_speed']>0).mean() # proportion of clockwise turning
    return (p_clockwise<threshold) or (p_clockwise>1-threshold)

def avoiding_reactions_from_motion(segment, refractory=1, threshold=None, dt=1): # refractory period in frames
    '''
    Returns the indexes of avoiding reactions (start), calculated from motion.
    '''
    if threshold is None:
        threshold_cos = 0
    else:
        threshold_cos = np.cos(threshold*dt) # maximum dot product
    # indexes of ARs
    backward_swimming = segment['motion_reversal']<threshold_cos
    AR = 1+(np.diff(1*backward_swimming)>0).nonzero()[0] # 1+ or 2+ ?
    if len(AR)>0:
        return AR[np.hstack([np.diff(AR)>refractory, True])]
    else:
        return []

def calculate_backward_swimming(segment):
    '''
    Calculates whether the cell is backward swimming.
    '''
    segment['BS'] = (np.cos(segment['angle'])*segment['vx'] + np.sin(segment['angle'])*segment['vy'])<0

def forward_swimming_segments(table):
    '''
    Returns all forward swimming segments.
    First use `calculate_backward_swimming`.
    '''
    return segments_from_table(table[table['BS']==False])

def avoiding_reactions_from_posture(segment):
    '''
    Returns the indexes of avoiding reactions (start), calculated from the comparison of posture and motion.
    '''
    return 1+(np.diff(1*segment['BS'])>0).nonzero()[0]

def mark_avoiding_reactions_from_motion(segment, refractory=1, threshold=None, dt=1.):
    '''
    Mark the start of an avoiding reaction, calculated from motion.

    Refractoriness not taken into account here.
    '''
    if threshold is None:
        threshold_cos = 0
    else:
        threshold_cos = np.cos(threshold*dt) # maximum dot product
    backward_swimming = segment['motion_reversal']<threshold_cos
    segment['mAR_start'] = np.hstack([np.diff(1*backward_swimming)>0, False])
    return segment

def cell_number(table):
    '''
    Returns the median number of cells in all frames.
    '''
    return table.groupby('frame')['frame'].count().median()

def median_speed(table):
    '''
    Returns median velocity vs. time.
    THIS ONE IS WEIRD
    '''
    return table.groupby('speed').count().median()

def fix_angle(segment):
    '''
    Fix discontinuities in cell angle due to front-back confusions.
    '''
    if len(segment)>2:
        segment['angle'] = np.unwrap(2*(segment['angle'] % (np.pi)))/2
        # Adjust
        if (np.cos(segment['angle'])*segment['vx'] + np.sin(segment['angle'])*segment['vy']).mean()<0:
            segment['angle'] = (segment['angle']+np.pi) % (2*np.pi)
    return segment

def PDC(segment, threshold=4.45, dt=1):
    '''
    Percent directional change from Clark and Nelson (1991):
    returns the proportion of time during which motion angular speed is greater than  4.45 rad/s.
    The advantage of this measurement is that it does not require posture information, and it might be more
    sensitive than detecting avoiding reactions from motion (it would also detect directional changes without
    backward swimming).

    According to our paper (Escoubet et al. 2022), if we take this for the posture angle rather than motion
    angle, then this seems to correspond to the turning phase of an avoiding reaction.
    It could be interesting to look at the distribution of this angular speed.

    There is also the issue of cells that barely swim at all.
    '''
    threshold_cos = np.cos(threshold*dt) # maximum dot product
    return np.nanmean(1.*(segment['motion_reversal'] < threshold_cos))

def centroid(table):
    '''
    Returns the centroid of all trajectories
    '''
    return table['x'].mean(), table['y'].mean()

def diameter(table):
    '''
    Returns the diameter of the circle enclosing all trajectories
    '''
    xc, yc = centroid(table)
    return 2*((((table['x'] - xc)**2 + (table['y'] - yc)**2)**.5).max())

def swirl_index(table, annulus=0.):
    '''
    Returns a signed index of swirling motion, vs. time, between -1 and 1 (>0 is clockwise).
    Selects trajectories from an annulus at distance `annulus' x diameter from the centroid.
    '''
    xc, yc = centroid(table)
    d = diameter(table)
    table_annulus = table[(table['x'] - xc)**2 + (table['y'] - yc)**2 > (.5*d*annulus)**2]

    rx, ry = table_annulus['x']-xc, table_annulus['y']-yc # vector pointing from center to trajectory
    rx, ry = rx/(rx**2 + ry**2)**.5, ry/(rx**2 + ry**2)**.5
    vx, vy = table_annulus['vx'], table_annulus['vy'] # motion vector
    vx, vy = table_annulus['vx'], table_annulus['vy'] # motion vector
    #vx, vy = np.cos(table['angle']), np.sin(table['angle']) # here with cell angle instead of motion
    vx, vy = vx / (vx ** 2 + vy ** 2) ** .5, vy / (vx ** 2 + vy ** 2) ** .5

    table_annulus['swirl'] = rx*vy - ry*vx

    return table_annulus.groupby('frame').mean()['swirl']

def circling_index(table, annulus=0.):
    '''
    Returns an index of circling motion, vs. time, with 0 meaning no random motion and 1 meaning circling.
    Selects trajectories from an annulus at distance `annulus' x diameter from the centroid.
    In contrast with `swirl_index', this one also returns a large value if cells circle in different directions.
    '''
    xc, yc = centroid(table)
    d = diameter(table)
    table_annulus = table[(table['x'] - xc)**2 + (table['y'] - yc)**2 > (.5*d*annulus)**2]

    rx, ry = table_annulus['x']-xc, table_annulus['y']-yc # vector pointing from center to trajectory
    rx, ry = rx/(rx**2 + ry**2)**.5, ry/(rx**2 + ry**2)**.5
    vx, vy = table_annulus['vx'], table_annulus['vy'] # motion vector
    vx, vy = table_annulus['vx'], table_annulus['vy'] # motion vector
    #vx, vy = np.cos(table['angle']), np.sin(table['angle']) # here with cell angle instead of motion
    vx, vy = vx / (vx ** 2 + vy ** 2) ** .5, vy / (vx ** 2 + vy ** 2) ** .5

    table_annulus['circling'] = (np.abs(rx*vy - ry*vx) - 2/np.pi)/(1-2/np.pi) # expectation with random angle is 2/pi

    return table_annulus.groupby('frame').mean()['circling']

def spiral_features(segment, dt=1):
    '''
    Returns spiral features.

    NOT WORKING YET
    '''
    # FFT
    speed = segment['speed'].array/dt
    speed = speed[~np.isnan(speed)]
    N = len(speed)
    X = fft(speed**2)
    freq = fftfreq(N, d=dt)
    X_norm = np.abs(X[:N // 2])*2./N

    v2 = X_norm[0] # instantaneous speed, squared
    omega = freq[np.argmax(X_norm)]*(2*np.pi) # spinning speed
    power = max(X_norm) # lambda^2*omega^2 /2
    linear_speed = (v2-power)**.5
    pitch = (2*power)**.5/omega
    angle = np.arctan2((2*power)**.5, linear_speed)

    return {'duration' : N, # number of frames
            'linear_speed' : linear_speed,
            'pitch' : pitch,
            'spinning_speed' : omega/(2*np.pi),
            'spinning_angle' : angle} # in radians

#def meandering_index(segment):
#    '''
#    Calculates the mean scalar product of motion and posture unit vectors,
#    giving an index of meandering.
#    '''
#    segment['reversal']/segment['speed']

############
# Plotting
############
def plot_colored_trajectory(axs, x, y, color, color_min=None, color_max=None):
    '''
    Plot a trajectory with a color-coded value.
    '''
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    if (color_min is None) or (color_max is None):
        color_min, color_max = np.nanmin(color), np.nanmax(color)
    norm = plt.Normalize(color_min, color_max)
    lc = LineCollection(segments, cmap='hot', norm=norm)  # twilight, spring
    lc.set_array(color)
    line = axs.add_collection(lc)
    return line


if __name__ == '__main__':
    from pylab import *
    import os
    from trajectories.fasttrack import load_fasttrack, fasttrack_angle
    #from trajectories.trex import load_trex_files
    from matplotlib.collections import LineCollection

    ### Load FastTrack trajectories
    # Thermotaxis experiment
    data = load_fasttrack(os.path.expanduser('~/Downloads/thermotaxis_videos/Tracking_Result_20220805_18/tracking.txt'))
    #data = load_trex_files(os.path.expanduser('~/Downloads/TRex/20220805_18'))
    dt = 0.06  # 17 Hz
    pixel_size = 14.6 # um/pixel (according to Antoine)
    #pixel_size = 1000 ### For TRex, scale has to be adjusted

    # Convert pixels to um
    scale_lengths(data, pixel_size)

    # Select frames after 30 s
    data = data[data['frame']>int(30./dt)]

    ### Select all contiguous segments
    segments = segments_from_table(data)

    ### Select all contiguous segments in the first trajectory
    #trajectories = trajectories_from_table(data)
    #segments = segments_from_trajectory(trajectories[0])

    ### Filter segments: longer than 1 s and spanning a distance of at least min_distance
    min_distance = 400 # in um
    selected_segments = [segment for segment in segments if len(segment)>int(1/dt) and \
                         ((segment['x'].max() - segment['x'].min()) ** 2 + (
                                     segment['y'].max() - segment['y'].min()) ** 2) > min_distance ** 2]

    ### Calculate features for all selected segments
    for segment in selected_segments:
        calculate_features(segment)
        fix_angle(segment)
        calculate_backward_swimming(segment)
        mark_avoiding_reactions_from_motion(segment, dt=dt)

    ### Determine if the cell is going left or right for all selected segments
    shift = int(1/dt) # 1 second movement
    for segment in selected_segments:
        x = np.array(segment['x'])
        segment['movement'] = np.hstack([[nan]*shift,x[shift:]-x[:-shift]])

    ### Make a big table of all segments
    table = pd.concat(selected_segments)
    print("Number of cells:", cell_number(table))

    ########################
    ### Plot one trajectory
    ########################
    traj = selected_segments[20]
    x, y = np.array(traj['x']), np.array(traj['y'])
    v = np.array(traj['speed'])/dt
    BS_start = avoiding_reactions_from_motion(traj, refractory=1, dt=dt)
    BS_start_posture = avoiding_reactions_from_posture(traj)

    # Color plot speed on trajectory
    fig, axs = plt.subplots(1, 1)
    line = plot_colored_trajectory(axs, x, y, v, color_min=0, color_max=1000)
    fig.colorbar(line, ax=axs)
    #axs.set_xlim(x.min(), x.max())
    #axs.set_ylim(y.min(), y.max())

    # Plot avoiding reactions
    axs.plot(x[BS_start], y[BS_start], '.k')
    axs.plot(x[BS_start_posture], y[BS_start_posture], '.b')

    #############################################
    ### Some exploration of that trajectory
    #############################################
    figure()
    t = np.array(traj['frame'])*dt
    subplot(611)
    plot(t, traj['speed']/dt)
    ylabel('Speed (um/s)')
    subplot(612)
    plot(t, traj['motion_reversal'])
    plot(t[BS_start], traj['motion_reversal'].iloc[BS_start], '.')
    plot(t, 0*t, 'k--')
    ylabel('Motion reversal')
    subplot(613)
    plot(t, traj['BS'])
    ylabel('Backward swimming')
    subplot(614)
    plot(t, traj['angle'] % (2*np.pi), 'k')
    plot(t[BS_start], traj['angle'].iloc[BS_start] % (2*np.pi), '.')
    motion_angle = np.arctan2(traj['vy'], traj['vx']) % (2*np.pi)
    plot(t, motion_angle % (2*np.pi), 'b')
    ylabel('Angle (rad)')
    subplot(615)
    plot(t, traj['angular_speed']/dt)
    plot(t[BS_start], traj['angular_speed'].iloc[BS_start] /dt, '.')
    plot(t, 0*t,'k--')
    ylabel('Angular speed (rad/s)')
    #subplot(616)
    #plot(t, traj['eccentricity'])
    #ylabel('Eccentricity')

    ############################
    ### Plot speed vs. x
    ############################
    figure()
    x, v = np.array(table['x']), array(table['speed'])/dt

    bins = linspace(min(x), max(x), 20)
    bin_indexes = digitize(x, bins)
    v_mean = ([np.nanmean(v[bin_indexes == i]) for i in range(1, len(bins))])

    plot(bins[1:], v_mean)
    xlabel('x (um)')
    ylabel('Speed (um/s)')

    ############################
    ### Plot firing rate vs. x
    ############################
    figure()

    # Cells moving left ; it should probably be measured on a longer distance
    table_left = table[table['movement']<-100.] # 100 um over the last second
    AR_left = np.array(table_left['mAR_start']) # motion-based avoiding reactions
    #AR_left = np.array(table_left['eccentricity']) # motion-based avoiding reactions
    bin_indexes_left = digitize(table_left['x'], bins)
    AR_rate_left = ([np.nanmean(AR_left[bin_indexes_left == i])/dt for i in range(1, len(bins))])

    # Cells moving right
    table_right = table[table['movement']>100.]
    AR_right = np.array(table_right['mAR_start'])
    #AR_right = np.array(table_right['eccentricity'])
    bin_indexes_right = digitize(table_right['x'], bins)
    AR_rate_right = ([np.nanmean(AR_right[bin_indexes_right == i])/dt for i in range(1, len(bins))])

    plot(bins[1:], AR_rate_left,'b') # The x axis should be labelled
    plot(bins[1:], AR_rate_right,'r')
    xlabel('x (um)')
    ylabel('Avoiding reaction rate (Hz)')

    ############################
    ### Plot eccentricity vs. x
    ############################
    """
    figure()

    # Cells moving left ; it should probably be measured on a longer distance
    table_left = table[table['movement']<-100.] # 100 um over the last second
    eccentricity_left = np.array(table_left['eccentricity']) # motion-based avoiding reactions
    bin_indexes_left = digitize(table_left['x'], bins)
    eccentricity_left = ([np.nanmean(eccentricity_left[bin_indexes_left == i]) for i in range(1, len(bins))])

    # Cells moving right
    table_right = table[table['movement']>100.]
    eccentricity_right = np.array(table_right['eccentricity'])
    bin_indexes_right = digitize(table_right['x'], bins)
    eccentricity_right = ([np.nanmean(eccentricity_right[bin_indexes_right == i]) for i in range(1, len(bins))])

    plot(bins[1:], eccentricity_left,'b') # The x axis should be labelled
    plot(bins[1:], eccentricity_right,'r')
    xlabel('x (um)')
    ylabel('Eccentricity')
    """

    ############################
    ### Plot a few long segments
    ############################
    figure()
    for segment in selected_segments:
        if len(segment) > int(40/dt): # at least 30 seconds
            plot(segment['x'], segment['y'])

    show()
