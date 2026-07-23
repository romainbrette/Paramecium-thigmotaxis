'''
Selection of a drop.
'''
import matplotlib.pyplot as plt
from skimage.feature import canny
from skimage.draw import circle_perimeter
from skimage.transform import hough_circle, hough_circle_peaks
import numpy as np
from skimage import morphology, measure, feature
from scipy import ndimage as ndi

__all__ = ['DropCircleClicker', 'click_on_drop']

def click_on_drop(image, erosion=15):
    '''
    Shows an image and lets the user select a drop.
    '''
    # edge detection
    edges = feature.canny(image, sigma=3)#, use_quantiles=True)
    edges = morphology.binary_closing(edges, morphology.disk(2))
    # fill
    mask = ndi.binary_fill_holes(edges)
    # erode
    mask_shrunk = morphology.erosion(mask, morphology.disk(erosion))
    labels = measure.label(mask_shrunk, connectivity=2)

    fig, ax = plt.subplots()
    ax.imshow(image, cmap='gray')
    ax.imshow(mask, cmap='Reds', alpha=0.5)
    ax.axis('off')
    #fig.title("Select a drop")

    x, y = plt.ginput(1)[0]
    x, y = int(x), int(y)
    plt.close(fig)

    label = labels[y, x]
    if label == 0:
        raise ValueError("You clicked on the background")

    return (labels == label)

class DropCircleClicker:
    '''
    Shows an image and lets the user select a region that encompasses a drop.
    In that region, a matching circle is selected.
    '''
    _DOWNSAMPLING = 10

    def __init__(self, image, scaling_factor = 1.1, process=None):
        self.image = image
        self.scaling_factor = scaling_factor
        self.process = process
        self.fig, self.ax = plt.subplots()
        self.ax.imshow(image, cmap='gray')
        #self.rs = RectangleSelector(self.ax, self.onselect, useblit=True, button=[1],
        #                            interactive=True)
        plt.axis('off')
        plt.show()

    def onselect(self, eclick, erelease):
        x1, y1 = int(eclick.xdata), int(eclick.ydata)
        x2, y2 = int(erelease.xdata), int(erelease.ydata)

        # Crop
        image = self.image[y1:y2, x1:x2]

        radius = .25*(x2-x1+y2-y1)/self._DOWNSAMPLING

        edges = canny(image[::self._DOWNSAMPLING, ::self._DOWNSAMPLING]) # downsampling for increased efficiency
        radii_range = np.arange(radius*.75, radius*1.25, 10)
        hough_res = hough_circle(edges, radii_range)

        # Extract the most prominent circle
        accums, cx, cy, radii = hough_circle_peaks(hough_res, radii_range, total_num_peaks=1)
        self.cx = cx[0]*self._DOWNSAMPLING + x1
        self.cy = cy[0]*self._DOWNSAMPLING + y1
        self.radius = radii[0]*self._DOWNSAMPLING*self.scaling_factor

        # Draw detected circles
        circy, circx = circle_perimeter(int(self.cy), int(self.cx), int(self.radius))
        self.ax.scatter(circx, circy, color='r')#, linewidth=2)

        if self.process is not None:
            self.process(self.cx, self.cy, self.radius)

if __name__ == "__main__":
    import tkinter as tk
    from tkinter import filedialog
    import imageio

    ## Choose a background image
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    image_filename = filedialog.askopenfilename(title='Choose a background image')
    root.destroy()

    image = imageio.imread(image_filename)

    clicker = DropCircleClicker(image)
    print(clicker.cx, clicker.cy, clicker.radius)
