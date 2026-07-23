'''
Calculates and displays the frequency spectrum in the selected ROI.
'''
import numpy as np
import tkinter as tk
from tkinter import filedialog
import os
import tifffile as tiff
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector

save = False

# Choose folder
root = tk.Tk()
root.withdraw()  # Hide the main window
filename = filedialog.askopenfilename(initialdir=os.path.expanduser('~/Downloads/'))
root.destroy()

# Get FPS
fps_name = os.path.splitext(filename)[0] + '.fps'
with open(fps_name, 'r') as f:
    fps = float(f.readline())

stack = tiff.imread(filename)

print("Loaded.")
print('FPS = ', fps, 'Hz')

T, H, W = stack.shape
n = T

# Make folder
folder = os.path.splitext(filename)[0]+'_spectrum'
if not os.path.exists(folder):
    os.mkdir(folder)

# TEMPORAL FFT PER PIXEL
# FFT along time axis
fft_data = np.fft.rfft(stack, axis=0)

# Magnitude (power spectrum)
power = np.abs(fft_data) # **2 for power

# Frequencies corresponding to rFFT bins
freqs = np.fft.rfftfreq(T, d=1.0/fps)

# DOMINANT FREQUENCY
# Ignore DC component (frequency = 0)
power_no_dc = power[1:, :, :]
freqs_no_dc = freqs[1:]

# Average over the image
#mean_power = np.mean(power_no_dc, axis = (1, 2))

# Show image
fig, ax = plt.subplots()
ax.imshow(stack[0,:,:], cmap='gray')

out_fig, out_ax = plt.subplots()
out_ax.set_title("Selected region")

# --- callback function ---
def onselect(eclick, erelease):
    x1, y1 = int(eclick.xdata), int(eclick.ydata)
    x2, y2 = int(erelease.xdata), int(erelease.ydata)

    # Ensure proper ordering
    xmin, xmax = sorted([x1, x2])
    ymin, ymax = sorted([y1, y2])

    mean_power = np.mean(power_no_dc[:, ymin:ymax, xmin:xmax], axis=(1, 2))
    out_ax.clear()
    freq_selection = (freqs_no_dc>5) & (freqs_no_dc<100)
    out_ax.plot(freqs_no_dc[freq_selection], mean_power[freq_selection])
    out_ax.set_xlabel("Frequency (Hz)")
    out_ax.set_ylabel("Amplitude")
    out_ax.set_title("Power spectrum")
    out_fig.canvas.draw_idle()

    if save:
        # Save image with bounding box
        annotated_image = stack[0, :, :].copy()
        #M = annotated_image.max()
        annotated_image[ymin, xmin:xmax] = 0
        annotated_image[ymax, xmin:xmax] = 0
        annotated_image[ymin:ymax, xmin] = 0
        annotated_image[ymin:ymax, xmax] = 0
        plt.imsave(os.path.join(folder,f"image_with_bb_{xmin}_{xmax}_{ymin}_{ymax}.png"), annotated_image, cmap="gray")

        # Save plot and spectrum
        out_fig.savefig(os.path.join(folder,f"figure_{xmin}_{xmax}_{ymin}_{ymax}.png"))
        data = np.column_stack((freqs_no_dc, mean_power))
        np.savetxt(os.path.join(folder,f"spectrum_{xmin}_{xmax}_{ymin}_{ymax}.txt"), data)

plt.tight_layout()
# --- rectangle selector ---
selector = RectangleSelector(
    ax,
    onselect,
    useblit=True,
    #button=[1],  # left mouse button
    #minspanx=5,
    #minspany=5,
    spancoords='pixels',
    interactive=True
)

plt.show()
