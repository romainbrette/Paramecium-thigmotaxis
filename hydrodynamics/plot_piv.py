'''
Plot PIV field and Paramecium.

Input files:
- vel_2D.txt             : x, y, u, v velocity field
- cell_vertices.txt      : X1L vertex coordinates
- cell_triangles.txt     : triangle face connectivity
- cell_face_colors.txt   : RGB face colors

The simulation results folder is selected interactively.
The final PDF is saved in the selected folder.

The PIV field and Paramecium are rendered separately and
then combined. The Paramecium is rendered as a transparent
PNG using the actual 3D triangulation, then layered over
the PIV field.
'''

import os
import numpy as np

import matplotlib
matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from pypdf import PdfReader, PdfWriter

import tkinter as tk
from tkinter import filedialog

# ------------------------------------------------------------
# Select simulation results folder
# ------------------------------------------------------------


# Directory containing this Python script
python_dir = os.path.dirname(
    os.path.abspath(__file__)
)

# Main simulation directory
simulation_dir = os.path.dirname(
    python_dir
)

# Directory containing simulation results
results_dir = os.path.join(
    simulation_dir,
    'Results'
)


# Open folder-selection dialog
root = tk.Tk()
root.withdraw()

folder = filedialog.askdirectory(
    initialdir=results_dir,
    title='Choose simulation results folder'
)

root.destroy()


# Stop if no folder was selected
if not folder:
    raise RuntimeError(
        'No simulation results folder selected.'
    )


# ------------------------------------------------------------
# File locations
# ------------------------------------------------------------

filename = os.path.join(
    folder,
    'vel_2D.txt'
)

vertices_filename = os.path.join(
    folder,
    'cell_vertices.txt'
)

triangles_filename = os.path.join(
    folder,
    'cell_triangles.txt'
)

face_colors_filename = os.path.join(
    folder,
    'cell_face_colors.txt'
)

output_filename = os.path.join(
    folder,
    os.path.basename(folder) + '.pdf'
)

flow_filename = os.path.join(
    folder,
    'flow.png'
)

cell_filename = os.path.join(
    folder,
    'paramecium.png'
)

# ------------------------------------------------------------
# PDF rotation
# ------------------------------------------------------------

# Rotate the entire finished PDF.
#
# Change to -90 for the opposite direction.
rotation_deg = 90


# ------------------------------------------------------------
# Figure resolution
# ------------------------------------------------------------

# Both the flow field and Paramecium PNG use these exact
# dimensions so that they can be layered without shifting.
dpi = 200

fig_width = 10
fig_height = 10


# ------------------------------------------------------------
# Load PIV field
# ------------------------------------------------------------

x, y, u, v = np.loadtxt(filename).T

# Find grid dimensions
width = (np.diff(y) > 0.).nonzero()[0][0] + 1
height = len(x) // width

# Reshape data onto Cartesian grid
x = x.reshape((height, width))
y = y.reshape((height, width))

u = u.reshape((height, width))
v = v.reshape((height, width))


# ------------------------------------------------------------
# Load Paramecium geometry
# ------------------------------------------------------------

X1L = np.loadtxt(vertices_filename)

tri = np.loadtxt(
    triangles_filename,
    dtype=int
)

# Convert MATLAB's 1-based indexing to Python's 0-based indexing
tri = tri - 1

# ------------------------------------------------------------
# Calculate velocity magnitude
# ------------------------------------------------------------

speed = np.sqrt(u**2 + v**2)


# ------------------------------------------------------------
# Determine common plot limits
# ------------------------------------------------------------

x_min = min(
    x.min(),
    X1L[:, 0].min()
)

x_max = max(
    x.max(),
    X1L[:, 0].max()
)

y_min = min(
    y.min(),
    X1L[:, 1].min()
)

y_max = max(
    y.max(),
    X1L[:, 1].max()
)

# ------------------------------------------------------------
# Assign face colors
# ------------------------------------------------------------

Cdata = np.loadtxt(
    face_colors_filename
)

# Add alpha channel
Cdata = np.column_stack((
    Cdata,
    np.ones(len(Cdata))
))


# ============================================================
# 1. RENDER FLOW FIELD
# ============================================================

fig = plt.figure(
    figsize=(fig_width, fig_height),
    dpi=dpi
)

ax = fig.add_axes(
    [0, 0, 1, 1],
    frameon=False
)

ax.set_aspect('equal')

ax.set_xlim(x_min, x_max)
ax.set_ylim(y_min, y_max)

ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)


# ------------------------------------------------------------
# Smooth velocity magnitude
# ------------------------------------------------------------

ax.pcolormesh(
    x,
    y,
    speed,
    cmap='inferno',
    shading='gouraud'
)


# ------------------------------------------------------------
# Streamlines with arrows
# ------------------------------------------------------------

ax.streamplot(
    x,
    y,
    u,
    v,
    color='white',
    density=1.0,
    linewidth=1.0,
    arrowsize=2.0
)


# ------------------------------------------------------------
# Save flow field
# ------------------------------------------------------------

fig.savefig(
    flow_filename,
    dpi=dpi,
    transparent=False,
    facecolor='black',
    edgecolor='none',
    pad_inches=0
)

plt.close(fig)


# ============================================================
# 2. RENDER PARAMECIUM
# ============================================================

fig = plt.figure(
    figsize=(fig_width, fig_height),
    dpi=dpi
)

ax = fig.add_axes(
    [0, 0, 1, 1],
    projection='3d'
)


# ------------------------------------------------------------
# Build actual 3D triangular faces
# ------------------------------------------------------------

# Keep the full x,y,z coordinates.
#
# No projection or coordinate manipulation is performed here.

face_vertices = X1L[tri]


# ------------------------------------------------------------
# Plot triangular mesh
# ------------------------------------------------------------

poly3d = Poly3DCollection(
    face_vertices,
    facecolors=Cdata,
    edgecolors='black',
    linewidths=0.7,
    alpha=1.0
)

ax.add_collection3d(poly3d)


# ------------------------------------------------------------
# Set common x/y limits
# ------------------------------------------------------------

ax.set_xlim(x_min, x_max)
ax.set_ylim(y_min, y_max)

ax.set_zlim(
    X1L[:, 2].min(),
    X1L[:, 2].max()
)


# ------------------------------------------------------------
# Set equal aspect ratio
# ------------------------------------------------------------

ax.set_box_aspect([
    x_max - x_min,
    y_max - y_min,
    X1L[:, 2].max() - X1L[:, 2].min()
])


# ------------------------------------------------------------
# View Paramecium from above
# ------------------------------------------------------------

# Camera is at +z looking toward -z.

ax.view_init(
    elev=90,
    azim=-90
)


# ------------------------------------------------------------
# Use orthographic projection
# ------------------------------------------------------------

# Prevent perspective distortion of the cell.
ax.set_proj_type('ortho')


# ------------------------------------------------------------
# Remove axes
# ------------------------------------------------------------

ax.set_axis_off()


# ------------------------------------------------------------
# Save transparent Paramecium PNG
# ------------------------------------------------------------

fig.savefig(
    cell_filename,
    dpi=dpi,
    transparent=True,
    facecolor='none',
    edgecolor='none',
    pad_inches=0
)

plt.close(fig)


# ============================================================
# 3. COMBINE FLOW FIELD + PARAMECIUM
# ============================================================

# Load the two PNGs as arrays.
flow_img = plt.imread(flow_filename)
cell_img = plt.imread(cell_filename)

# ------------------------------------------------------------
# Create composite figure
# ------------------------------------------------------------

fig = plt.figure(
    figsize=(fig_width, fig_height),
    dpi=dpi
)

ax = fig.add_axes(
    [0, 0, 1, 1]
)

ax.imshow(
    flow_img,
    origin='upper'
)

# Overlay Paramecium.
#
# The transparent background means only the cell itself
# covers the PIV field.

ax.imshow(
    cell_img,
    origin='upper'
)

ax.set_axis_off()


# ------------------------------------------------------------
# Save composite temporarily
# ------------------------------------------------------------

temp_filename = os.path.join(
    folder,
    'piv_temp.pdf'
)

fig.savefig(
    temp_filename,
    dpi=dpi,
    pad_inches=0,
    facecolor='none',
    edgecolor='none'
)

plt.close(fig)


# ============================================================
# 4. ROTATE AND CROP ENTIRE PDF
# ============================================================

reader = PdfReader(temp_filename)
writer = PdfWriter()

for page in reader.pages:

    # --------------------------------------------------------
    # Rotate the entire page
    # --------------------------------------------------------

    page.rotate(rotation_deg)

    # --------------------------------------------------------
    # Crop page to the aspect ratio of the flow field
    # --------------------------------------------------------

    x_range = x.max() - x.min()
    y_range = y.max() - y.min()

    flow_aspect = x_range / y_range

    # Page dimensions after rotation
    page_width = float(page.mediabox.width)
    page_height = float(page.mediabox.height)

    # For a 90-degree rotation, the page dimensions are
    # effectively swapped.
    rotated_width = page_height
    rotated_height = page_width

    # Determine crop dimensions while preserving the
    # center of the existing rendered image.
    if rotated_width / rotated_height > flow_aspect:

        # Page is too wide
        crop_width = rotated_height * flow_aspect
        crop_height = rotated_height

    else:

        # Page is too tall
        crop_width = rotated_width
        crop_height = rotated_width / flow_aspect

    # Center the crop
    left = (rotated_width - crop_width) / 2
    bottom = (rotated_height - crop_height) / 2

    right = left + crop_width
    top = bottom + crop_height

    page.mediabox.lower_left = (
        left,
        bottom
    )

    page.mediabox.upper_right = (
        right,
        top
    )

    writer.add_page(page)


with open(output_filename, 'wb') as f:
    writer.write(f)

# ------------------------------------------------------------
# Clean up temporary files
# ------------------------------------------------------------

os.remove(temp_filename)
os.remove(flow_filename)
os.remove(cell_filename)

print('Saved:', output_filename)