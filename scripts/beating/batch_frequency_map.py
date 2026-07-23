'''
From a set of tiff files (each one being a movie of a cell), calculates the peak beating frequency map.
'''
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
import os
import tifffile as tiff
from scipy.ndimage import uniform_filter1d
from cmap import Colormap

f_min = 5.
f_max = 100. # Hz

# Choose folder
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

    map_name = os.path.splitext(filename)[0]+'_map.tiff'
    firemap_name = os.path.splitext(filename)[0]+'_firemap.tiff'

    # Get FPS
    fps_name = os.path.splitext(filename)[0]+'.fps'
    with open(fps_name, 'r') as f:
        fps = float(f.readline())

    # with tiff.TiffFile(filename) as tif:
    #     metadata = tif.imagej_metadata
    # # FPS
    # fps = 1./metadata['finterval']
    stack = tiff.imread(filename)

    print("Loaded.")
    print('FPS = ', fps, 'Hz')

    T, H, W = stack.shape
    n = T

    # TEMPORAL FFT PER PIXEL
    # FFT along time axis
    fft_data = np.fft.rfft(stack, axis=0)

    # Magnitude (power spectrum)
    power = np.abs(fft_data)  # **2 for power
    F_power = power.shape[0]

    # Frequencies corresponding to rFFT bins
    freqs = np.fft.rfftfreq(T, d=1.0 / fps)

    # Bin
    def bin_image(image, m=2):
        """Bin an image array by 2x2 bins (averages each 2x2 block)."""
        # Crop to even dimensions if needed
        image = image[:, :H // m * m, :W // m * m]
        return image.reshape(F_power, H // m, m, W // m, m).mean(axis=(2, 4))

    power = bin_image(power, m=3)

    # DOMINANT FREQUENCY
    # Ignore DC component (frequency = 0)
    power_no_dc = power[1:, :, :]
    freqs_no_dc = freqs[1:]

    # Background (low power)
    total_power = np.sum(power_no_dc ** 2, axis=0)
    background = total_power < .01 * total_power.max()

    power_no_dc = uniform_filter1d(power_no_dc, size=3, axis=0)
    power_no_dc = power_no_dc[(freqs_no_dc >= f_min) & (freqs_no_dc <= f_max), :, :]
    freqs_no_dc = freqs_no_dc[(freqs_no_dc >= f_min) & (freqs_no_dc <= f_max)]

    # Dominant frequency map
    freq_map = freqs_no_dc[np.argmax(power_no_dc, axis=0)]

    # Sets too low / too high frequency to 0
    freq_map[freq_map == freqs_no_dc.max()] = 0.
    freq_map[freq_map == freqs_no_dc.min()] = 0.

    # Mask background
    freq_map[background] = 0.

    freq_norm = freq_map / f_max

    # Save as tiff
    tiff.imwrite(map_name, (freq_norm * 255).astype(np.uint8))

    # ------------------------------------------------------------
    # APPLY LINEAR COLORMAP
    # ------------------------------------------------------------
    # cmap = cm.get_cmap(cmap_name)
    cmap = Colormap('imagej:fire')
    freq_rgb = cmap(freq_norm)[..., :3]  # (H,W,3)

    # SAVE OUTPUT
    plt.imsave(firemap_name, freq_rgb)
    print(f"Saved output image: {firemap_name}")
    plt.close()
