'''
Calculate features (speed etc.) from a tracking file.
'''
from trajectories.magic_loading import *
from trajectories.trajectory_analysis import *
import os
from interface import *
from trajectories.linking import *
from tqdm import tqdm
#from concurrent.futures import ProcessPoolExecutor, as_completed
import concurrent.futures

if __name__ == "__main__":
    print("** Calculating features **")

    ## Select tracking file
    filename = ask_open_tracking_file()
    fps, pixel_size = guess_or_ask_fps_and_pixelsize(filename)
    dt = 1/fps

    ## Load tracking file
    print(filename)
    data = magic_load_trajectories(filename, link=False)

    ## Convert pixels to um
    scale_lengths(data, pixel_size)
    data = filter_shape(data) # maybe shouldn't be here

    ### Calculate features (speed etc.)
    # Select all contiguous segments
    segments = segments_from_table(data)
    print("Calculating features over", len(segments), "segments")
    with concurrent.futures.ProcessPoolExecutor() as executor:  # much faster!
        segments = executor.map(calculate_features, segments)
        segments = executor.map(mark_avoiding_reactions_from_motion, segments)
    # with ProcessPoolExecutor() as executor: # much faster!
    #     # Basic features
    #     futures = [executor.submit(calculate_features, segment) for segment in segments]
    #     segments = [future.result() for future in tqdm(as_completed(futures), total=len(segments), desc="Calculating features")]
    #     # Avoiding reactions from motion
    #     futures = [executor.submit(mark_avoiding_reactions_from_motion, segment) for segment in segments]
    #     segments = [future.result() for future in tqdm(as_completed(futures), total=len(segments), desc="Calculating avoiding reactions")]
    table = pd.concat(segments)
    table.sort_values(by='frame')

    ### Save tracking file
    print("Saving tracked file")
    tracked_filename = os.path.splitext(os.path.splitext(filename)[0])[0]+'_tracked_with_features.csv.zip'
    table.to_csv(tracked_filename, float_format="%.1f", compression='zip') ## This is slow!
