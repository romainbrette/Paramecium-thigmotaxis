'''
Converts czi and tiff files to mp4.
'''
import tkinter as tk
from tkinter import filedialog
from dateutil import parser
import tifffile as tiff
from pylab import *
import czifile
import imageio.v2 as imageio

## Parameters
fps_divider = 10 ## Slows down the movie by this factor
target_fps = None #20 ## If not None, changes the playback FPS, without making it faster or slower (ie selects frames)
## target_fps must be smaller than the original fps

# Choose files
root = tk.Tk()
root.withdraw()  # Hide the main window
#filename = filedialog.askopenfilename(initialdir=os.path.expanduser('~/Downloads/'))
file_paths = list(filedialog.askopenfilenames(
    title="Select files",
    filetypes=[("All files", "*.*")]
))

root.destroy()

for filename in file_paths:
    print(filename)
    print()
    output_name = os.path.splitext(filename)[0] + '.mp4'

    if filename.endswith('.czi'):
        with czifile.CziFile(filename) as czi:
            # FPS
            timestamps = []

            for segment in czi.segments():
                if isinstance(segment, czifile.SubBlockSegment):
                    meta = segment.metadata()
                    if meta and 'Tags' in meta:
                        acq_time = meta['Tags'].get('AcquisitionTime')
                        if acq_time:
                            t = parser.parse(acq_time)
                            timestamps.append(t.timestamp())  # en secondes (float)

            timestamps = sorted(timestamps)
            deltas = np.diff(timestamps)
            fps = 1 / np.mean(deltas)
            stack = czi.asarray().squeeze()
    else:
        # Get FPS
        fps_name = os.path.splitext(filename)[0] + '.fps'
        with open(fps_name, 'r') as f:
            fps = float(f.readline())

        stack = tiff.imread(filename)

    print('FPS = ', fps, 'Hz')

    T, H, W = stack.shape
    n = T

    stack = stack.astype(float32)
    stack = (255 * stack / stack.max()).astype("uint8")

    # Write MP4
    if target_fps is not None: # assumed slower
        k = int(fps/target_fps)
        stack = stack[::k,:,:]
        print("Output FPS:", fps/k, "Hz")
    else:
        k = 1
    imageio.mimsave(output_name, stack, fps=fps/k/fps_divider, codec="libx264", quality=7)
