'''
Count attached and swimming cells from two trajectory files.
One trajectory file for the background images.
One for the background-removed images, with calculated features (speed).
The user selects a ROI (rectangle).
The result is saved in a tsv file with columns:
    t, swimming (number of swimming cells), attached (number of attached cells)

TODO:
- adjust ROI shift with pixel size from settings
  For now, works if we use the unlinked background file.
'''
from pylab import *
import os
from trajectories.visualization import *
from trajectories.magic_loading import *
from trajectories.linking import *
import logging
import yaml
from interface import *

logging.basicConfig(level=logging.WARNING)

## Choose the swimming tracking file
filename = ask_open_tracking_file(title='Choose a swimming tracking file')
filename_background = ask_open_tracking_file(title='Choose a background tracking file')

## Load the two tracking files
print("Loading trajectories")
data = magic_load_trajectories(filename)
data_background = magic_load_trajectories(filename_background)

### !Fixing an old bug! angle, width and height were messed up
# if np.abs(data_background['angle'].mean())<1.:
#     print("Columns are messed up!")
#     width, angle, length = \
#         data_background['angle'].values.copy(), data_background['width'].values.copy(), \
#             data_background['length'].values.copy()
#     data_background['angle'], data_background["width"], data_background['length'] =\
#         [x for _, x in \
#         sorted([(width.mean(), width), (angle.mean(), angle), (length.mean(), length)])]

## Parameters
fps, pixel_size = guess_fps_and_pixelsize(filename)
_, background_pixel_size = guess_fps_and_pixelsize(filename_background)

output_folder = os.path.dirname(filename)

# Get from settings.yaml
settings_filename = os.path.join(os.path.dirname(os.path.dirname(filename_background)), "settings.yaml")

with open(settings_filename, "r") as f:
    settings = yaml.safe_load(f)

# Guess number of images per background
window_size = round((1+data['frame'].max()) / (1+data_background['frame'].max())) # assuming frame 0

parameters = [('fps', 'Frame rate (Hz)', fps or 20.),
              ('pixel_size', 'Pixel size (µm)', pixel_size*1. or 1.),
              ('background_pixel_size', 'Background pixel size (µm)', background_pixel_size or 1.),
              ('window_size', 'Background interval (frames)', window_size), # this can be obtained from the settings.yaml file, background/recalculated every
              ('speed_threshold', 'Swimming speed threshold (um/s)', 30),
              ('tmax', 'Maximum time (s)', 1e6)
              ]
P = ParametersDialog(title='Enter parameters', parameters=parameters).value
fps, pixel_size, background_pixel_size= P['fps'], P['pixel_size'], P['background_pixel_size']
window_size = int(P['window_size'])
dt = 1/fps
speed_threshold = P['speed_threshold']

## Prepare tracking file
data = data[data['frame']*dt<=P['tmax']]
scale_lengths(data, pixel_size)
# length = data['length'].median()
# length_min, length_max = length * .5, length * 1.5
# width = data['width'].median()
# width_min, width_max = width * .5, width * 2
# data = filter_shape(data, length=(length_min, length_max), width=(width_min, width_max))
data = filter_shape(data, length=None)

data_background = data_background[data_background['frame']*window_size*dt<=P['tmax']]
scale_lengths(data_background, background_pixel_size)
#data_background = filter_shape(data_background, length=(length_min, length_max), width=(width_min, width_max))
data_background = filter_shape(data_background, length=None)

data['speed'] *= pixel_size/dt
data["frame"] = data["frame"].astype(int)
data_background["frame"] = data_background["frame"].astype(int)

## ROI adjustment
ROI_x, ROI_y = settings['roi_xy']
ROI_x, ROI_y = int(ROI_x)*background_pixel_size, int(ROI_y)*background_pixel_size # !!! not the right pixel size!
data_background['x'] += ROI_x
data_background['y'] += ROI_y

## Time scale (this could be refactored in plots)
if data['frame'].max()*dt>3*3600: # 3 h
    time_scale, time_label = 3600, 'h'
elif data['frame'].max()*dt>3*60.: # 3 min
    time_scale, time_label = 60, 'min'
else:
    time_scale, time_label = 1, 's'

def new_file(name):
    # Checks whether name exists, if so return name2 and so on
    formatted_name = name.format('')
    if os.path.exists(formatted_name):
        i = 2
        formatted_name = name.format(i)
        while os.path.exists(formatted_name):
            i += 1
            formatted_name = name.format(i)
    return formatted_name

## Process data in ROI
def process_ROI(x1, y1, x2, y2):
    ROI = data[(data['x'] >= x1) & (data['x'] <= x2) & (data['y'] >= y1) & (data['y'] <= y2)]
    ROI.sort_values(by='frame')
    ROI_background = data_background[(data_background['x'] >= x1) & (data_background['x'] <= x2) &\
                                     (data_background['y'] >= y1) & (data_background['y'] <= y2)]
    ROI_background.sort_values(by='frame')

    ## Number of cells vs. time
    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, sharex=True)

    n_frames = max(ROI['frame'].max() + 1, (ROI_background['frame'].max() + 1)*window_size)

    ## Swimming cells vs. time
    swimming = ROI[ROI['speed']>=speed_threshold]
    swimming_frames = swimming.groupby('frame')
    # Count maximum number of swimming cells per background period
    #n_frames = ROI['frame'].max() + 1
    count = swimming_frames['frame'].size().reindex(range(0, n_frames), fill_value=0).to_numpy()
    count = count[:(len(count)//window_size)*window_size]
    count = count.reshape((len(count)//window_size, window_size)).max(axis=1)
    t = np.arange(count.shape[0])*dt*window_size
    # Count number of attached cells
    background_frames = ROI_background.groupby('frame')
    background_count = background_frames['frame'].size().reindex(range(0, n_frames//window_size), fill_value=0).to_numpy()
    # Total number of cells
    total_count = count + background_count

    ax1.plot(t/time_scale, count, 'r')
    ax1.plot(t/time_scale, background_count, 'k')
    ax1.plot(t/time_scale, total_count, 'b')
    ax1.set_ylim(bottom=0)
    ax1.set_ylabel('Cell count')
    #ax1.set_xlabel(f'Time ({time_label})')

    ax2.plot(t/time_scale, 100*count/total_count, 'r')
    ax2.plot(t/time_scale, 100*background_count/total_count, 'k')
    ax2.set_ylabel('Proportion (%)')
    ax2.set_xlabel(f'Time ({time_label})')

    plt.show()

    # Save
    results = pd.DataFrame({'t':t , 'swimming': count, 'attached': background_count})
    results.to_csv(new_file(os.path.join(output_folder, 'count{}.tsv')), sep="\t", index=False)

## Select a ROI
segments = trajectories_from_table(data[data['frame']<60./dt]) # Show the first minute
ROI_plot = TrajectoryPlot(segments, onselect=process_ROI)
plt.show()
