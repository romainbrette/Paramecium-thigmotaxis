from .fasttrack import load_fasttrack
import os
import pandas as pd
from trajectories.linking import trackpy_track
from tqdm import tqdm

__all__ = ['magic_load_trajectories']

__chunk_size = 50000

def read_with_progress(filename, load_function=pd.read_csv, nframes=1e12, **kwd): # A better way would be to report the number of frames
    '''
    Reads a tracking csv/tsv file and displays the number of frames read in a progress bar
    '''
    previous_n = 0
    chunks = []
    with tqdm(desc="Loading") as pbar:
        for chunk in load_function(filename, chunksize=__chunk_size, **kwd):
            n = chunk['frame'].max()
            pbar.update(n-previous_n)
            previous_n = n
            if (n<nframes+1):
                chunks.append(chunk)
            else:
                chunks.append(chunk[chunk['frame']<=nframes])
                break

    return pd.concat(chunks)

def magic_load_trajectories(filename, link=False, nframes=1e12):
    '''
    Magically loads a trajectory file by identifying its format.
    '''
    _, ext = os.path.splitext(filename)
    if (ext == '.tsv'): # table with header
        data = read_with_progress(filename, load_function=pd.read_table, nframes=nframes)
        # Older files have wrong names
        data = data.rename(
            columns={'centroid-0': 'y', 'centroid-1': 'x', 'major_axis_length': 'length', 'minor_axis_length': 'width',
                     'orientation': 'angle'})
        # Check if there are ids
    elif (ext == '.csv'):
        data = read_with_progress(filename, load_function=pd.read_csv, nframes=nframes)
    elif (ext == '.zip'):
        data = read_with_progress(filename, load_function=pd.read_csv, nframes=nframes, compression='zip')
    elif (ext == '.h5'):
        if nframes<1e12:
            data = pd.read_hdf(filename, key='df', stop=nframes*100) # not great, assuming 100 cells
            data = data[data['frame']<=nframes]
        else:
            data = pd.read_hdf(filename, key='df')
    elif os.path.basename(filename) == 'tracking.txt': # Fasttrack
        data = load_fasttrack(filename)
    else:
        raise OSError("Unknown format")

    if data['length'].mean() < data['width'].mean():  # Check whether it's inverted
        temp = data['length'].copy()
        data['length'] = data['width']
        data['width'] = temp

    if ('id' not in data) and link:
        t = trackpy_track(data)
        data["id"] = t['particle']

    return data
