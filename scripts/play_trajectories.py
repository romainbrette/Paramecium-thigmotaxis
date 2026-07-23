import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from matplotlib.widgets import Slider, Button
import numpy as np
from trajectories.magic_loading import *
from interface import *
from trajectories.trajectory_analysis import *

## Choose the swimming tracking file
filename = ask_open_tracking_file(title='Choose a swimming tracking file')

## Parameters
# Here I could automatically get the number of images per background from tiff filenames
fps, pixel_size = guess_fps_and_pixelsize(filename)
parameters = [('fps', 'Frame rate (Hz)', fps or 20.),
              ('pixel_size', 'Pixel size (µm)', pixel_size or 1.)
              ]
P = ParametersDialog(title='Enter parameters', parameters=parameters).value
fps, pixel_size= P['fps'], P['pixel_size']
dt = 1/fps

## Load tracking file, only the first chunk
print("Loading swimming cells")
df = magic_load_trajectories(filename)
scale_lengths(df, pixel_size)
#df = filter_shape(df, length=None)

# --------------------------------------
# df must have columns:
# frame, id, x, y, angle, length, width
# --------------------------------------

# Group by frame for fast access
df['frame'] = df['frame'].astype(int)
n = df['frame'].max()

print("making figure")
# --- Matplotlib figure setup ---
fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.25)

ax.set_aspect('equal')
ax.set_xlim(df['x'].min() - 10, df['x'].max() + 10)
ax.set_ylim(df['y'].min() - 10, df['y'].max() + 10)
ax.set_title("Cell Trajectory Viewer")

# Store ellipses currently drawn
current_patches = []

# --- Slider ---
ax_slider = plt.axes([0.15, 0.1, 0.7, 0.05])
slider = Slider(ax_slider, "Frame", 0, n-1, valinit=0, valstep=1)

# --- Play/Pause Button ---
ax_button = plt.axes([0.45, 0.02, 0.1, 0.05])
button = Button(ax_button, "Play")

is_playing = False


def draw_frame(frame_idx):
    """Clear old ellipses and draw ellipses for this frame."""
    global current_patches

    # Remove previous ellipses
    for p in current_patches:
        p.remove()
    current_patches = []

    rows = df[df['frame'] == frame_idx]

    # Create ellipses for each cell in the frame
    for _, row in rows.iterrows():
        if row['mAR_start']>0:
            color = 'red'
        else:
            color = 'blue'

        e = Ellipse(
            (row["x"], row["y"]),
            width=row["width"],
            height=row["length"],
            angle=np.degrees(np.pi/2-row["angle"]),  # assuming angle is in radians
            fill=False,
            edgecolor=color,
            linewidth=1.0,
        )
        ax.add_patch(e)
        current_patches.append(e)

    fig.canvas.draw_idle()


# Slider callback
def on_slider(val):
    draw_frame(val)

slider.on_changed(on_slider)


# Play/Pause button callback
def on_button(event):
    global is_playing
    is_playing = not is_playing
    button.label.set_text("Pause" if is_playing else "Play")
    #fig.canvas.draw_idle()

button.on_clicked(on_button)

# ---- Timer for smooth animation ----
timer = fig.canvas.new_timer(interval=int(1000*dt))

def on_timer():
    if is_playing:
        next_idx = (slider.val + 1) % n
        slider.set_val(next_idx)

timer.add_callback(on_timer)
timer.start()

# Initial frame
draw_frame(0)

plt.show()
