'''
Visualization of trajectories and analysis

1. Plots of trajectories with ARs (and possibly speed?)
- It should be possible to redraw the trajectories if the time scale is changed
    (maybe simply clear and replot?)
- The background could be shown

2. Plot of speed vs. time
- The table could be updated

3. Plot of AR rate vs. time

Thus, if those are dynamic figures, it should be an object.

Maybe, we have a data object, which gets the relevant properties from figures
(ROI, etc.), and outputs a filtered data object. This output is then connected to
the various plots, which are updated.
So for example, when a time axis is changed, there is a callback that updates
the data, and then all figures updated.
So the object must hold a list of figures to update.
The figure must have an update method (perhaps using bokeh instead).

The time axes of different plots are linked; the space axes are linked.

For time-dependent data, we can have a drop-down menu with different properties (speed, etc.).
'''
from trajectories.trajectory_analysis import *
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector, Button, SpanSelector

__all__ = ['plot_trajectories', 'TrajectoryPlot', 'TimePlot', 'sliding_window_average']

def sliding_window_average(arr, window_size):
    # Convert to numpy array if not already
    data = np.asarray(arr, dtype=float)

    # Create a mask for non-NaN values
    valid_mask = np.isfinite(data)

    # Replace NaNs with 0 in the data to safely use cumsum
    safe_data = np.where(valid_mask, data, 0)

    # Compute the cumulative sum and cumulative count of valid entries
    cumsum = np.cumsum(safe_data)
    valid_count = np.cumsum(valid_mask.astype(int))

    # Sliding window sums and counts
    cumsum_sliding = cumsum[window_size:] - cumsum[:-window_size]
    valid_count_sliding = valid_count[window_size:] - valid_count[:-window_size]

    # Compute the sliding averages (avoid division by zero)
    sliding_avg = np.where(valid_count_sliding > 0, cumsum_sliding / valid_count_sliding, np.nan)

    # Pad the result to make it the same size as the input
    pad_width = (window_size - 1) // 2
    result = np.full_like(data, np.nan)
    result[pad_width:pad_width + len(sliding_avg)] = sliding_avg

    return result

def plot_trajectories(ax, segments, colormap=plt.cm.viridis):
    '''
    Plot trajectories with avoiding reactions.
    '''
    for segment in segments:
        #BS_start = avoiding_reactions_from_motion(segment)
        x, y = np.array(segment['x']), np.array(segment['y'])
        if 'ROI' in segment:
            color = colormap(segment['ROI'].iloc[0] / 10)
        else:
            color = 'k'
        ax.plot(x, y, color=color)
        #ax.scatter(x[BS_start], y[BS_start], color=color)
    ax.invert_yaxis() # It's upside down!

class TrajectoryPlot(object):
    '''
    An interactive plot showing trajectories.
    '''
    def __init__(self, segments, colormap=plt.cm.viridis, onselect_title=None, onselect=None):
        self.segments = segments
        self.colormap = colormap
        self.fig, self.ax = plt.subplots()
        self.onselect_title = onselect_title
        self._onselect = onselect

        self.frame_start, self.frame_end = 0, 1e12

        self.rs = RectangleSelector(self.ax, self.onselect, useblit=True, button=[1],
                                    minspanx=5, minspany=5, spancoords='data', interactive=True)
        self.update()
        if onselect_title is not None:
            self.update_title(onselect_title(0,0,1e6,1e6))

    def onselect(self, eclick, erelease):
        self.x1, self.y1 = int(eclick.xdata), int(eclick.ydata)
        self.x2, self.y2 = int(erelease.xdata), int(erelease.ydata)
        if self._onselect is not None:
            self._onselect(self.x1, self.y1, self.x2, self.y2)
        if self.onselect_title is not None:
            self.update_title(self.onselect_title(self.x1, self.y1, self.x2, self.y2))

    def update_title(self, new_title):
        self.ax.set_title(new_title)
        self.fig.canvas.draw()
        plt.tight_layout()

    def update(self):
        self.ax.clear()
        segments = [segment[(segment['frame']>=self.frame_start) & (segment['frame']<self.frame_end)] for segment in self.segments]
        print("Plotting", len(segments), "segments")
        plot_trajectories(self.ax, segments, colormap=self.colormap)
        self.fig.canvas.draw()

    def set_frame_interval(self, frame_start, frame_end):
        self.frame_start, self.frame_end = frame_start, frame_end
        self.update()

class TimePlot(object):
    '''
    An interactive plot showing a time-dependent feature
    '''
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        self.data = data
        self.x1, self.x2, self.y1, self.y2 = data['x'].min(), data['x'].max(), data['y'].min(), data['y'].max()
        self.frame_start, self.frame_end = 0, 1e12

        self.span_selector = SpanSelector(self.ax, self.onselect, 'horizontal', useblit=True)

        self.update()

    def onselect(self, xmin, xmax):
        self.frame_start, self.frame_end = int(xmin), int(xmax)

    def update(self):
        #t = np.array(well['frame'] * dt)
        pass

if __name__ == '__main__':
    from fasttrack import load_fasttrack
    from pylab import *
    import time

    data = load_fasttrack('/Users/romainbrette/Downloads/Single cells #1/Tracking_Result_Basler a2A5320-23umBAS (40311059)_20240419_110749085/tracking.txt')
    dt = 1 / 20.
    pixel_size = 4.95

    # Convert pixels to um
    scale_lengths(data, pixel_size)
    data = data[data['frame'] * dt < 100.]  # Only the first 100 s are correct, then we have recording problems.

    ### Select all contiguous segments
    segments = segments_from_table(data)

    ### Filter segments: longer than 1 s and spanning a distance of at least min_distance
    min_distance = 100  # in um
    selected_segments = [segment for segment in segments if len(segment) > int(.3 / dt) and \
                         ((segment['x'].max() - segment['x'].min()) ** 2 + (
                                 segment['y'].max() - segment['y'].min()) ** 2) > min_distance ** 2]
    for segment in selected_segments:
        calculate_features(segment)

    #plot_trajectories(ax, selected_segments)
    myplot = TrajectoryPlot(selected_segments, onselect_title=lambda x1,y1,x2,y2: 'x1 = {}\ny1 = {}'.format(x1, y1))

    #cid = fig.canvas.mpl_connect('draw_event', on_zoom)

    #myplot.set_frame_interval(10/dt, 30/dt)

    #def update(frame):
    #    myplot.set_frame_interval(5*frame, 5*(frame+10))

    # ani = animation.FuncAnimation(fig=fig, func=update, frames=200, interval=10)

    show()
