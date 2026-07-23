'''
From a set of czi or tiff files:
- Selects the most stable bit
- Average image
- Temporal variation image
'''
import tkinter as tk
from tkinter import filedialog
from dateutil import parser
import tifffile as tiff
from pylab import *
import czifile

# PARAMETERS
w = 2000  # number of frames in the stable interval
f_max = 100. # Hz
flip = True # Flip horizontally

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

    extract_name = os.path.splitext(filename)[0]+'_stable.tiff'
    average_name =os.path.splitext(filename)[0]+'_average.tiff'
    variation_name =os.path.splitext(filename)[0]+'_variation.tiff'

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
        with tiff.TiffFile(filename) as tif:
            metadata = tif.imagej_metadata
        # FPS
        fps = 1./metadata['finterval']
        stack = tiff.imread(filename)

        print("Loaded.")
        # czi artifact correction
        T, H, W = stack.shape
        stack = stack.astype(float).reshape((T, H*W))
        constant = np.where(np.sum(np.abs(np.diff(stack, axis=0)), axis=0) == 0)[0]
        if len(constant)>0:
            shift = constant.max()
            #stack[:, : 1+ (shift // W), :] = 0
            length = H*W - (1+(shift//W))*W
            print(stack.shape, length)
            print(T, H, W, shift)
            stack = stack[:, shift:shift+length].reshape((T, H-(1+(shift//W)), W))
        else:
            stack = stack.reshape((T,H,W))
    print('FPS = ', fps, 'Hz')

    T, H, W = stack.shape
    n = T

    stack = stack.astype(float)

    # Flip horizontally
    if flip:
        stack = stack[:,:,::-1]

    print('Shape:', stack.shape)
    print(stack.min(), stack.max())

    # Background subtraction
    #original_type = stack.dtype
    bstack = stack.astype(float) # background subtracted
    bstack -= bstack.mean(axis=0)
    bstack = np.clip(bstack, 0, np.inf)
    #stack = stack.astype(original_type)

    # Centroid
    y_indices, x_indices = np.indices(bstack.shape[1:])
    total = np.sum(bstack, axis=(1,2))
    xs = np.sum(x_indices * bstack, axis=(1,2)) / total
    ys = np.sum(y_indices * bstack, axis=(1,2)) / total
    #print(xs.mean(), ys.mean())
    # subplot(211)
    # plot(xs)
    # subplot(212)
    # plot(ys)
    # show()

    # Find interval of size w with smallest centroid variance
    # Precompute prefix sums for mean and mean-of-squares
    px  = np.concatenate([[0], np.cumsum(xs)])
    py  = np.concatenate([[0], np.cumsum(ys)])
    px2 = np.concatenate([[0], np.cumsum(xs ** 2)])
    py2 = np.concatenate([[0], np.cumsum(ys ** 2)])

    # For a window [i, i+w): var = mean(x²) - mean(x)²
    i = np.arange(n - w + 1)

    sum_x  = px[i + w]  - px[i]
    sum_y  = py[i + w]  - py[i]
    sum_x2 = px2[i + w] - px2[i]
    sum_y2 = py2[i + w] - py2[i]

    var_x = sum_x2 / w - (sum_x / w) ** 2
    var_y = sum_y2 / w - (sum_y / w) ** 2
    trace = var_x + var_y

    best = int(np.argmin(trace))
    print('Most stable part from frame', best)

    stack = stack[best:best+w,:,:]

    # Save tif
    tiff.imwrite(extract_name, stack.astype("uint16"), compression="zlib", imagej=True,
                 metadata={
                     "axes": "TYX",  # T = time, Y = height, X = width
                     #"fps": fps,
                     "unit": "um"
                     #"pixel_width": pixel_size_x*1e6, # not working
                     #"pixel_height": pixel_size_y*1e6
                 })

    # Save mean image
    tiff.imwrite(average_name, stack.mean(axis=0).astype("uint16"), compression="zlib")

    # Save variation image
    CV = np.mean(np.abs(np.diff(stack, axis=0)), axis=0)
    tiff.imwrite(variation_name, (CV/CV.max()*255).astype(np.uint8))

