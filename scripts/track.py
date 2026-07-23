'''
Track cells and calculate features (speed etc.)

Numbers are stored with 1 decimal.
'''
from trajectories.magic_loading import *
from trajectories.trajectory_analysis import *
import os
from interface import *
from trajectories.linking import *
import yaml
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
import concurrent.futures

print("** Tracking with Norfair **")

## Select tracking file
filename = ask_open_tracking_file()
fps, pixel_size = guess_fps_and_pixelsize(filename)

## Parameters
parameters = [('fps', 'Frame rate (Hz)', fps or 10.),
              ('pixel_size', 'Pixel size (um)', pixel_size or 1),
              ('truncate', 'Truncation (s)', 1e8),
              ('speed_threshold', 'Maximum speed (um/s)', 3000),
              ('memory', 'Maximum object loss duration (s)', .5),
              ('delay', 'Track initiation delay (s)', .2)
              ]
P = ParametersDialog(title='Enter parameters', parameters=parameters).value
fps, pixel_size = P['fps'], P['pixel_size']
dt = 1/fps

## Truncate
truncate = int(P['truncate']/dt)

## Load tracking file
print(filename)
data = magic_load_trajectories(filename, link=False, nframes=truncate)

## Convert pixels to um
scale_lengths(data, pixel_size)
data = filter_shape(data)

## Track
data['id'] = 0
data = norfair_track(data, distance_threshold=int(P['speed_threshold']*dt), memory=int(P['memory']/dt), delay=int(P['delay']/dt))
print("Average number of cells:", cell_number(data)) # this is actually quite slow! maybe mean rather than median?
print("Number of ids:", data['id'].max())

### Calculate features (speed etc.)
# Select all contiguous segments
segments = segments_from_table(data)
print("Calculating features over", len(segments), "segments")
segments = [calculate_features(segment) for segment in tqdm(segments, total=len(segments), desc="Calculating features")]
segments = [mark_avoiding_reactions_from_motion(segment) for segment in tqdm(segments, total=len(segments), desc="Calculating features")]

## This doesn't work on Windows!
# with ProcessPoolExecutor() as executor: # much faster!
#     # Basic features
#     futures = [executor.submit(calculate_features, segment) for segment in segments]
#     segments = [future.result() for future in tqdm(as_completed(futures), total=len(segments), desc="Calculating features")]
#     # Avoiding reactions from motion
#     futures = [executor.submit(mark_avoiding_reactions_from_motion, segment) for segment in segments]
#     segments = [future.result() for future in tqdm(as_completed(futures), total=len(segments), desc="Calculating avoiding reactions")]
table = pd.concat(segments)
table.sort_values(by='frame')

P['scaled'] = True  # notifies that spatial dimensions are already scaled at the right scale
try:
    ### Save tracking file
    print("Saving tracked file")
    tracked_filename = os.path.splitext(filename)[0]+'_tracked_with_features.csv.zip'
    table.to_csv(tracked_filename, float_format="%.1f", compression='zip') ## This is slow!
    ### Save info file
    info_filename = os.path.splitext(filename)[0] + '_tracked_with_features.yaml'
    with open(info_filename, 'w') as file:
        yaml.dump(P, file, default_flow_style=False)
except (OSError, IOError) as e: # Most likely a network error, save locally
    print(f"Network error: {e}")
    tracked_filename = os.path.splitext(os.path.basename(filename))[0] + '_tracked_with_features.csv.zip'
    tracked_filename = os.path.join(os.path.expanduser('~/Downloads'), tracked_filename)
    print("Saving to", tracked_filename)
    table.to_csv(tracked_filename, float_format="%.1f", compression='zip')
    ### Save info file
    info_filename = os.path.splitext(os.path.basename(filename))[0] + '_tracked_with_features.yaml'
    info_filename = os.path.join(os.path.expanduser('~/Downloads'), info_filename)
    with open(info_filename, 'w') as file:
        yaml.dump(P, file, default_flow_style=False)
