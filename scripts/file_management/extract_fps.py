'''
Extracts the FPS from a set of czi and tiff files, and save it to a file (.fps).
'''
import tkinter as tk
from tkinter import filedialog
import os
from dateutil import parser
import tifffile as tiff
import czifile
import numpy as np

# Choose folder
root = tk.Tk()
root.withdraw()  # Hide the main window
#filename = filedialog.askopenfilename(initialdir=os.path.expanduser('~/Downloads/'))
file_paths = list(filedialog.askopenfilenames(
    title="Select files",
    filetypes=[("All files", "*.*")]
))

root.destroy()

all_fps_name = os.path.join(os.path.dirname(file_paths[0]), 'all_fps.txt')

all_fps = []
for filename in file_paths:
    print(filename)
    print()

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

    else:
        with tiff.TiffFile(filename) as tif:
            metadata = tif.imagej_metadata
        # FPS
        fps = 1./metadata['finterval']
    print('FPS = ', fps, 'Hz')

    fps_name = os.path.splitext(filename)[0] + '.fps'
    fps_name_stable = os.path.splitext(filename)[0] + '_stable.fps'
    with open(fps_name, "w") as f:
        f.write(str(int(fps)))
    with open(fps_name_stable, "w") as f:
        f.write(str(int(fps)))

    all_fps.append((filename, int(fps)))

with open(all_fps_name, "w") as f:
    for filename, fps in all_fps:
        f.write(f"{filename}\t{fps}\n")
