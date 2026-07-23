'''
PIV analysis, averaged across time
(Particle Image Velocimetry)

!!! in openpiv 0.21.2, y is flipped (y[::-1]), in the current version it's not...
'''
import openpiv.pyprocess
import os
from interface import *
import numpy as np
import yaml
from scipy.ndimage import gaussian_filter
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')

#### Parameters
window_size = 10. # in um
max_velocity = 0#200. # in um/s, particle velocity
particle_size = 1. # in um, for preprocessing (filtering particles based on size; this is the sigma of the inner Gaussian)
default_pixel_size = 0.45 # in um
default_fps = 90.
#invert_v = True # not sure why this is needed
SNR_threshold = 1.5 #1.5 # not sure how to choose this

preprocess = True

nframes = 1e6 #1000

#### Openpiv version check
# 0.21.8 is new, 0.21.2 is old ; the old version inverts the y axis, not the new one
y = openpiv.pyprocess.get_coordinates(image_size=(2,1), search_area_size=1, overlap=0)[1]
openpiv_is_old = (y[0] == 1.5) # should be 0.5 if recent
#openpiv_is_old = True

#### Open frames
movie = ask_open_movie(guess=False)
movie.gray = True
fps = movie.fps or default_fps
dt = 1/fps
pixel_size = movie.pixel_size or default_pixel_size
print("FPS =", fps, "Hz")
print("Pixel size =", pixel_size, "um")

#### Output
output_filename = os.path.splitext(movie.filename)[0]+'_piv.txt'
info_filename = os.path.splitext(movie.filename)[0]+'_piv.yaml'
pdf_filename = os.path.splitext(movie.filename)[0]+'_piv.pdf'

print('Processing {}'.format(movie.filename))

#### Calculate preprocessing and PIV parameters
sigma = int(particle_size / pixel_size)
winsize = int(window_size / pixel_size)  # in pixels
max_displacement = int(max_velocity * dt / pixel_size)  # in pixel
searchsize = winsize + 2 * max_displacement
overlap = int(winsize * 2 / 3)  # pixels
print('sigma =', sigma)
print('winsize =', winsize)
print('searchsize =', searchsize)
print('overlap =', overlap)
print()

#### Calculate grid
image = movie.current_frame()
x, y = openpiv.pyprocess.get_coordinates(image_size=image.shape, search_area_size=searchsize, overlap=overlap)
#x, y = openpiv.pyprocess.get_coordinates(image_size=image.shape, search_area_size=winsize, overlap=overlap)
if openpiv_is_old:
    print('Old OpenPIV, fixing y.')
    y = y[::-1]

#### Write parameters
d = {"window_size" : int(window_size),
     "max_velocity" : max_velocity,
     "particle_size" : particle_size,
     "dt" : float(dt),
     "pixel_size" : float(pixel_size),
     "x_min" : int(x.min()-winsize//2),
     "x_max" : int(x.max()+winsize//2),
     "y_min" : int(y.min()-winsize//2),
     "y_max" : int(y.max()-winsize//2)}
with open(info_filename, 'w') as f:
    yaml.dump(d, f)

#### Preprocess
#print("Calculating background")
background = movie.mean()

#### Compute vector fields on image pairs
previous_frame = None
nrows, ncols = x.shape
density_max = np.zeros((nrows, ncols), dtype=bool)
density_mean = np.zeros((nrows, ncols), dtype=bool)
frame_i = 0
print("Starting")
u_mean, v_mean = np.zeros_like(x), np.zeros_like(x)
counter = np.zeros_like(x)
for frame in movie.frames():
    #print('Frame',frame_i+1)

    if preprocess:
        # Preprocessing: remove background, filter particles with double Gaussian
        subtracted = frame - background
        # invert
        subtracted = -subtracted
        filtered = (gaussian_filter(subtracted, sigma, truncate=2) - gaussian_filter(subtracted, sigma * 1.6, truncate=2)) * 1.3 * sigma

        # Turn to int (apparently necessary for the PIV algorithm)
        frame = (filtered/filtered.max() * 32768).astype('int32')

    if previous_frame is not None:
        # Calculate vector field by cross-correlation
        # search_area_size actually optional
        # u, v, sig2noise = openpiv.pyprocess.extended_search_area_piv(previous_frame, frame, window_size=winsize,
        #                                                            overlap=overlap, dt=dt,
        #                                                            sig2noise_method='peak2peak')
        u, v, sig2noise = openpiv.pyprocess.extended_search_area_piv(previous_frame, frame, window_size=winsize,
                                                                   overlap=overlap, dt=dt, #search_area_size=searchsize,
                                                                   sig2noise_method='peak2peak')
        # Inversion of v
        #if invert_v:
        #    v = -v

        # Scaling to um/s
        u, v = u * pixel_size, v * pixel_size

        # Signal to noise mask
        #print(sig2noise.max(), sig2noise.mean())
        mask = sig2noise<SNR_threshold
        u[mask] = 0
        v[mask] = 0
        u_mean += u
        v_mean += v
        counter += ~mask

    previous_frame = frame.copy()
    frame_i += 1
    if frame_i == nframes:
        break

u_mean, v_mean = u_mean/counter, v_mean/counter
u_mean[counter==0] = 0. # no data
v_mean[counter==0] = 0.

# Save to file
np.savetxt(output_filename, np.array([x.flatten(), y.flatten(), u_mean.flatten(), v_mean.flatten()]).T)

# Make plot
#v = -v
height, width = x.shape
fig = plt.figure(figsize=(10, 10*height/width))
plt.axis('off')
ax = plt.axes([0, 0, 1, 1], frameon=False)
ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)
ax.invert_yaxis()

speed = (u_mean**2 + v_mean**2)**.5
print('Max speed:', speed.max(), 'um/s')
ax.pcolormesh(x, y, speed, cmap='inferno', shading='gouraud')
ax.streamplot(x, y, u_mean, v_mean, color='white', arrowsize=2)
plt.savefig(pdf_filename)

plt.show()
