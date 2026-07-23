'''
Dialogs for file openings.

TODO:
- ask_open_movie: could simply be Movie()
'''
import os
import tkinter as tk
from tkinter import filedialog
from optparse import OptionParser
from movie import *
import glob
from interface.command_line import guess_fps_and_pixelsize
from tkinter import simpledialog
import imageio

__all__ = ['ask_open_movie', 'ask_open_tracking_file', 'ask_open_movie_and_tracking', 'ask_open_image',
           'ask_open_movie_and_tracking_and_fps_and_pixelsize', 'guess_tracking_file', 'guess_or_ask_fps_and_pixelsize']

def ask_open_movie(initialdir=None, guess=True):
    '''
    Dialog to choose a movie. Can be image files or movie.
    Returns Movie object.
    '''
    parser = OptionParser()
    parser.add_option('--dir', dest='dir', help='initial directory', default=os.path.expanduser('~/Downloads'))
    (options, args) = parser.parse_args()
    initialdir = initialdir or options.dir

    root = tk.Tk()
    root.withdraw()  # Hide the main window
    filename = filedialog.askopenfilename(initialdir=initialdir, title='Choose a movie',
                                          filetypes=[
                                              ("Movies", "*.mp4 *.avi *.czi"),
                                              ("Images", "*.tif *.tiff *.png *.jpg")
                                          ])
    root.destroy()

    # Check if it's an image or a movie
    ext = os.path.splitext(filename)[1]
    if (ext=='.mp4') or (ext=='.avi'):
        movie = MovieFile(filename)
    elif (ext=='.czi'):
        movie = CZIMovie(filename)
    else:
        movie = MovieFolder(os.path.dirname(filename))

    # Get FPS and pixel size
    if guess:
        fps, pixelsize = guess_fps_and_pixelsize(movie.filename)
    else:
        fps, pixelsize = None, None
    movie.fps = movie.fps or fps
    movie.pixel_size = movie.pixel_size or pixelsize

    return movie

def ask_open_image(initialdir=None):
    '''
    Dialog to choose a movie. Can be image files or movie.
    Returns Movie object.
    '''
    parser = OptionParser()
    parser.add_option('--dir', dest='dir', help='initial directory', default=os.path.expanduser('~/Downloads'))
    (options, args) = parser.parse_args()
    initialdir = initialdir or options.dir

    root = tk.Tk()
    root.withdraw()  # Hide the main window
    filename = filedialog.askopenfilename(initialdir=initialdir, title='Choose an image',
                                          filetypes=[
                                              ("Images", "*.tif *.tiff *.png *.jpg")
                                          ])
    root.destroy()

    # Get FPS and pixel size
    #fps, pixelsize = guess_fps_and_pixelsize(filename)
    image = imageio.imread(filename)

    return image

def ask_open_tracking_file(initialdir=None, title='Choose a tracking file'):
    '''
    Dialog to choose a tracking file.
    '''
    parser = OptionParser()
    parser.add_option('--dir', dest='dir', help='initial directory', default=os.path.expanduser('~/Downloads'))
    (options, args) = parser.parse_args()
    initialdir = initialdir or options.dir


    root = tk.Tk()
    root.withdraw()  # Hide the main window
    filename = filedialog.askopenfilename(initialdir=initialdir, title=title,
                                          filetypes=[
                                              ("Fasttrack", "*.txt"),
                                              ("Other", "*.csv *.tsv *.zip *.h5")
                                          ])
    root.destroy()

    return filename

def ask_open_movie_and_tracking():
    '''
    Dialogs to choose a movie and then a tracking file.
    Returns Movie object and tracking file.
    '''
    movie = ask_open_movie()
    path = movie.filename
    if not os.path.isdir(path):
        path = os.path.dirname(path)  # in the directory of the path
    tracking = ask_open_tracking_file(initialdir=path)
    return movie, tracking

class PixelsizeFPSDialog(simpledialog.Dialog):
    def __init__(self, parent, title=None, default_fps=20.0, default_pixelsize=5.):
        self.default_fps = default_fps
        self.default_pixelsize = default_pixelsize
        super().__init__(parent, title)  # Call the parent class initializer

    def body(self, master):
        # Create labels and entry fields for fps and pixelsize
        tk.Label(master, text="Frame rate (Hz):").grid(row=0, column=0)
        tk.Label(master, text="Pixel size (um):").grid(row=1, column=0)

        self.fps_entry = tk.Entry(master)
        self.pixelsize_entry = tk.Entry(master)

        # Set default values
        self.fps_entry.insert(0, str(self.default_fps))  # Default value for fps
        self.pixelsize_entry.insert(0, str(self.default_pixelsize))  # Default value for pixelsize

        self.fps_entry.grid(row=0, column=1)
        self.pixelsize_entry.grid(row=1, column=1)

        return self.fps_entry  # Initial focus

    def apply(self):
        # Retrieve the entered values when OK is clicked
        self.fps, self.pixelsize = float(self.fps_entry.get()), float(self.pixelsize_entry.get())

def ask_open_movie_and_tracking_and_fps_and_pixelsize():
    '''
    Dialogs to choose a movie and then a tracking file, and then FPS and pixel size.
    Returns Movie object, tracking file, fps and pixel size.
    '''
    movie, tracking = ask_open_movie_and_tracking()
    if (movie.fps is None) or (movie.pixel_size is None):
        # Dialog
        root = tk.Tk()
        root.withdraw()  # Hide the main window

        # Create and show the custom dialog
        dialog = PixelsizeFPSDialog(root, "Enter FPS and pixel size")
        movie.fps = dialog.fps
        movie.pixel_size = dialog.pixelsize

    return movie, tracking

def guess_or_ask_fps_and_pixelsize(filename):
    fps, pixel_size = guess_fps_and_pixelsize(filename)
    if (fps is None) or (pixel_size is None):
        # Dialog
        root = tk.Tk()
        root.withdraw()  # Hide the main window

        # Create and show the custom dialog
        dialog = PixelsizeFPSDialog(root, "Enter FPS and pixel size")
        fps = dialog.fps
        pixel_size = dialog.pixelsize
    return fps, pixel_size

def guess_tracking_file(path):
    '''
    Finds the tracking file corresponding to the movie path.

    TODO: tracking file produced by Marcel's script
    '''
    if not os.path.isdir(path):
        path = os.path.dirname(path)  # in the directory of the path
    # Look for Fasttrack file
    possible_folders = [folder for folder in glob.glob(os.path.join(path, 'Tracking_Result*')) if 'Archive' not in folder]
    if len(possible_folders)>0:
        filename= os.path.join(possible_folders[0], 'tracking.txt')
        if os.path.exists(filename):
            return filename
        else:
            return None

if __name__ == '__main__':
    ask_open_movie_and_tracking_and_fps_and_pixelsize()
