'''
Movie class
Basic processing of movies and image folders
'''
from __future__ import division
import imageio
from glob import glob
import os
from numpy import linspace, abs
import multiprocessing as mp
import numpy as np

from tkinter import *
from tkinter.filedialog import askopenfilename
import zipfile
from dateutil import parser
import xml.etree.ElementTree as ET

try:
    import czifile
except ImportError:
    import warnings
    warnings.warn('Could not import czifile')

__all__ = ['Movie', 'MovieFolder', 'MovieFile', 'MovieFolderWithBackground', 'MovieZip', 'CZIMovie']

_INFINITE_SIZE = 1000000000 # maximum number of frames

# General movie class with no loading in memory
class Movie(object):
    '''
    Movie.

    Arguments:
        * filename: name of movie file (e.g. mp4) or folder with images (tiff or png)
        * fps: frames per second
        * pixel_size: size of a pixel in um
        * gray: if True, convert to gray scale by just selecting the red channel (faster)
        * truncate: number of frames read (if None, all)
        * step: frame increment
        * invert: True if in dark field
    '''
    def __init__(self, filename=None, fps=None, pixel_size=None, gray=False, truncate=None, step=1, invert=False):
        self.fps = fps
        self.pixel_size = pixel_size
        self.gray = gray
        self.start = 0
        if truncate is not None:
            self.end = truncate
        else:
            self.end = _INFINITE_SIZE
        self.step = step
        self.n = _INFINITE_SIZE # number of frames

        if filename is None: # selection GUI
            self.filename = self.select_file()
        else:
            self.filename = filename

        self.position = 0
        self.invert = invert

    def select_file(self):
        root = Tk()
        name = askopenfilename()#filetypes=(("TIFF files","*.tiff"),("PNG files","*.png")),
                                #title='Choose a file') # initialdir=...
        root.withdraw()
        return name

    def seek(self, n): # goes to frame n
        if n<0:
            n = len(self)-n
        if (n<0) or (n>len(self)):
            raise IndexError('No such frame')
        self.position = n

    def current_frame(self):
        frame = self._current_frame()
        if self.gray and frame.ndim == 3:
            frame = frame[:,:,0] #.mean(axis=2)
        if self.invert:
            return -frame
        else:
            return frame

    def _current_frame(self):
        pass

    def next_frame(self, gray=False):
        frame = self.current_frame()
        if gray and frame.ndim == 3:
            frame = frame.mean(axis=2)
        self.position+=self.step
        return frame

    def __len__(self):
        return self.n

    def rewind(self):
        self.seek(self.start)

    def duration(self):
        return len(self)/self.fps

    def mean(self, n=None, save=None, original_type=False):
        # Optionally save to `save` filename
        # original_type: if True, returns not a float array but the original type
        # n : number of frames over which the background is calculated (first frames)
        frame = self.current_frame()
        frame_type = frame.dtype
        background = 0.*frame
        i = 0
        for image in self.frames(verbose=False):
            background+=image*1.
            i+=1
            if i==n:
                break
        n = i
        self.rewind()
        background = background/n

        if save: # converts to original type (eg int) before saving
            writer = imageio.get_writer(save)
            writer.append_data(background.astype(frame_type), meta=dict(compress=9))
            writer.close()

        if original_type:
            background = background.astype(frame_type)

        return background

    def var(self, n=None, save=None, original_type=False):
        # Variance map
        # Optionally save to `save` filename
        # original_type: if True, returns not a float array but the original type
        # n : number of frames over which the variance is calculated (first frames)
        frame = self.current_frame()
        frame_type = frame.dtype
        squared = 0.*frame
        i = 0
        for image in self.frames(verbose=False):
            image = image*1.
            squared+=image**2
            i+=1
            if i==n:
                break
        n = i
        self.rewind()
        image_variance = squared / n - self.mean(n=n) ** 2

        if save: # converts to original type (eg int) before saving
            writer = imageio.get_writer(save)
            writer.append_data(image_variance.astype(frame_type), meta=dict(compress=9))
            writer.close()

        if original_type:
            image_variance = image_variance.astype(frame_type)

        return image_variance

    def variation(self, n=None, save=None, original_type=False):
        # Absolute variation map
        # Optionally save to `save` filename
        # original_type: if True, returns not a float array but the original type
        # n : number of frames over which the variance is calculated (first frames)
        frame = self.current_frame()
        frame_type = frame.dtype
        V = 0.*frame
        i = 0
        previous_image = None
        for image in self.frames(verbose=False):
            image = image*1.
            if previous_image is not None:
                V+=abs(image-previous_image)
            i+=1
            if i==n:
                break
            previous_image = image
        n = i
        self.rewind()
        image_variation = V / n

        if save: # converts to original type (eg int) before saving
            writer = imageio.get_writer(save)
            writer.append_data(image_variation.astype(frame_type), meta=dict(compress=9))
            writer.close()

        if original_type:
            image_variation = image_variation.astype(frame_type)

        return image_variation

    def frames(self, verbose=True, n=1):
        '''
        Generator that yields frames.
        If `verbose` is True, displays frame number every 10 frames.
        n = number of frames (if n>1, returns a list of frames)
        '''
        # If gray is True, then returns images in gray scale

        if n == 1 :
            while True:
                try:
                    if (self.position>=self.end):
                        return

                    yield self.next_frame(gray=self.gray)
                    if verbose and (self.position % 10 == 0):
                        print('Frame {}/{}'.format(self.position, len(self)))
                except: # IndexError, and for movie?
                    return
        else:
            while True:
                if (self.position >= self.end):
                    return
                frame_list = []
                try:
                    for _ in range(n):
                        frame_list.append(self.next_frame(gray=self.gray))
                        if verbose and (self.position % 10 == 0):
                            print('Frame {}/{}'.format(self.position, len(self)))
                except:
                    pass
                if len(frame_list)==0:
                    return
                else:
                    yield frame_list

    def map(self, process=None, n=1, verbose=True):
        # Runs process on all images and returns a list of results
        # If n>1, do it in parallel
        if n <=0:
            n = mp.cpu_count()+n
        if n==1:
            return [process(image) for image in self.frames(verbose=verbose)]
        else:
            pool = mp.Pool(n)
            results = []
            for images in self.frames(verbose=verbose, n=n):
                results.extend(pool.map(process, images))
            pool.close()
            return results

    def map_pairs(self, process=None, n=1, verbose=True):
        # Runs process on all successive image pairs and returns a list of results
        # If n>1, do it in parallel
        if n <=0:
            n = mp.cpu_count()+n
        if n==1:
            previous_image = None
            results = []
            for image in self.frames(verbose=verbose):
                if previous_image is not None:
                    results.append(process(previous_image,image))
                previous_image = image
            return results
        else:
            pool = mp.Pool(n)
            process_pair = lambda pair: process(*pair)
            results = []
            previous_image = self.next_frame(gray=self.gray)
            for images in self.frames(verbose=verbose, n=n):
                all_frames = [previous_image]+images
                pairs = list(zip(all_frames[:-1],all_frames[1:]))
                results.extend(pool.map(process_pair, pairs))
                previous_image = images[-1]
            pool.close()
            return results

    def write(self, filename=None, process=None, verbose=True, parallel=1, quality=5, bitrate=None):
        # Write movie to file or folder, processing frames with process
        self.rewind()
        extension = os.path.splitext(filename)[1]

        # Parallel processing (0 = all cpus)
        if parallel <=0:
            parallel = mp.cpu_count()-parallel

        if extension == '': # folder
            self.write_folder(filename=filename, process=process, verbose=verbose, parallel=parallel)
        else:
            self.write_file(filename=filename, process=process, verbose=verbose, parallel=parallel, quality=quality, bitrate=bitrate)

    def write_file(self, filename=None, process=None, verbose=True, parallel=1, quality=5, bitrate=None):
        # Write movie to file, processing frames with process
        writer = imageio.get_writer(filename, fps=self.fps, quality=quality, bitrate=bitrate)

        # Write frames
        if parallel!=1: # Run in parallel
            pool = mp.Pool(parallel)
            for images in self.frames(verbose=verbose, n=parallel):
                if process:
                    images = pool.map(process, images)
                for image in images:
                    if image is not None:
                        writer.append_data(image)
            pool.close()

        for image in self.frames(verbose=verbose):
            if process:
                image = process(image)
            if image is not None:
                writer.append_data(image)

        writer.close()

    def write_folder(self, filename=None, process=None, verbose=True, parallel=1):
        # Write movie to folder, processing frames with process

        # Create new folder
        if not os.path.exists(filename):
            if verbose:
                print('Creating directory')
            os.mkdir(filename)

        # Write frames
        if parallel!=1: # Run in parallel
            pool = mp.Pool(parallel)
            position = self.position+1
            for images in self.frames(verbose=verbose, n=parallel):
                if process is not None:
                    images = pool.map(process, images)
                for image in images:
                    if image is not None:
                        name = f'{position:09}.tiff'
                        writer = imageio.get_writer(filename + '/' + name)
                        writer.append_data(image, meta=dict(compress=9))
                        writer.close()
                        position+=1
            pool.close()

        for image in self.frames(verbose=verbose):
            if process:
                image = process(image)
            if image is not None:
                name = f'{self.position:09}.tiff'
                writer = imageio.get_writer(filename + '/' + name)
                writer.append_data(image, meta=dict(compress=9))
                writer.close()

    def is_darkfield(self, image):
        # returns True if the current frame is mostly black
        frame = image.flatten()*1.
        half_intensity = (frame.min()+frame.max())*.5
        return len((frame>half_intensity).nonzero()[0])<len(frame)*.5

    def calculate_length(self):
        # calculates the number of frames
        if len(self) ==_INFINITE_SIZE:
            self.n = 0
            for frame in self.frames(verbose=False):
                self.n += 1
            self.rewind()

    def close(self):
        pass

# Movie file
class MovieFile(Movie):
    '''
    Movie file.

    Arguments:
        * filename: name of file
        * fps: frames per second
        * pixel_size: size of a pixel in um
    '''
    def __init__(self, filename, **kwds):
        Movie.__init__(self, filename, **kwds)

        self.reader = imageio.get_reader(filename)
        if self.fps is None:
            self.fps = self.reader.get_meta_data()['fps']

    def __len__(self): # number of frames
        if Movie.__len__(self) == _INFINITE_SIZE:
            length = self.reader.get_length()
            if type(length) != type(0):
                self.n = _INFINITE_SIZE
            else:
                self.n = length
        return self.n

    # Generator giving frames one by one
    def _current_frame(self):
        return self.reader.get_data(self.position)

    def close(self):
        self.reader.close()

class CZIMovie(Movie):
    '''
    Movie file with czi format (Zeiss).

    Arguments:
        * filename: name of folder withimages (tiff or png)
        * fps: frames per second
        * pixel_size: size of a pixel in um
    '''
    def __init__(self, filename, **kwds):
        Movie.__init__(self, filename, **kwds)

        with czifile.CziFile(filename) as czi:
            if self.fps is None:
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
                self.fps = 1 / np.mean(deltas)

            if self.pixel_size is None:
                metadata = czi.metadata()
                root = ET.fromstring(metadata)
                # Find pixel size (in meters)
                scaling = root.find(".//Scaling/Items")
                self.pixel_size = float(scaling.find(".//Distance[@Id='X']/Value").text)*1e6 # assuming um

            self.stack = czi.asarray().squeeze()

    def __len__(self): # number of frames
        return self.stack.shape[0]

    # Generator giving frames one by one
    def _current_frame(self):
        return self.stack[self.position]

    def close(self):
        pass

# Movie folder
class MovieFolder(Movie):
    '''
    Movie folder.

    Arguments:
        * filename: name of folder withimages (tiff or png)
        * fps: frames per second
        * pixel_size: size of a pixel in um
    '''
    def __init__(self, filename, **kwds):
        Movie.__init__(self, filename, **kwds)

        # Get all file names
        filename+='/'
        self.files = glob(filename+'*.tif')+glob(filename+'*.tiff')+glob(filename+'*.png') # we could add other extensions

        if len(self.files)==0:
            raise FileNotFoundError('The folder {} is empty'.format(filename))

        self.files.sort()

    def __len__(self): # number of frames
        return len(self.files)

    # Generator giving frames one by one
    def _current_frame(self):
        return imageio.imread(self.files[self.position])

# Movie folder with backgrounds
class MovieFolderWithBackground(Movie):
    '''
    Movie folder with separated backgrounds.
    Backgrounds are in a "backgrounds" folder.
    Background filenames must strictly follow the following format:
        background_uint8_0000000-0000049

    Arguments:
        * filename: name of folder withimages (tiff or png)
        * fps: frames per second
        * pixel_size: size of a pixel in um
    '''
    def __init__(self, filename, **kwds):
        MovieFolder.__init__(self, filename, **kwds)

        background_folder = os.path.join(filename, 'backgrounds')
        self.background_files = glob(os.path.join(background_folder,'*.tif'))+ \
                                glob(os.path.join(background_folder, '*.tiff'))+ \
                                glob(os.path.join(background_folder, '*.png')) # we could add other extensions
        self.background_files.sort()
        n1 = int(os.path.splitext(self.background_files[0])[0][-15:-8])
        n2 = int(os.path.splitext(self.background_files[1])[0][-15:-8])
        self.period = n2-n1
        self.current_background_n = -1
        self.current_background = None

    def __len__(self): # number of frames
        return len(self.files)

    # Generator giving frames one by one
    def _current_frame(self):
        image = imageio.imread(self.files[self.position])
        background_n = self.position // self.period
        if background_n != self.current_background_n:
            self.current_background_n = background_n
            self.current_background = imageio.imread(self.background_files[background_n]).astype(np.uint16)
        #return (self.current_background + 5*(image.astype(np.int16)-123)).astype(np.uint8)  # 123 is the background, it seems
        return ((self.current_background+2*image.astype(np.int16))-255).astype(np.uint8) # 123 is the background, it seems

# Movie folder, zipped
class MovieZip(MovieFolder):
    '''
    Movie folder.

    Arguments:
        * filename: name of zipped file withimages (tiff or png)
        * fps: frames per second
        * pixel_size: size of a pixel in um
    '''
    def __init__(self, filename, **kwds):
        Movie.__init__(self, filename, **kwds)

        self.zipname = filename
        # Get all file names
        self.zip_ref = zipfile.ZipFile(filename, 'r')
        # List all files in the zip
        self.files = self.zip_ref.namelist() # assuming these are only images

        self.files.sort()
        #self.set_auto_invert() # not the best way to do it

    def __len__(self): # number of frames
        return len(self.files)

    # Generator giving frames one by one
    def _current_frame(self):
        with self.zip_ref.open(self.files[self.position]) as file:
            image = imageio.imread(file)
        return image

    def close(self):
        self.zip_ref.close()

if __name__ == '__main__':
    filename = '/Users/romainbrette/Movies/zone_intrigante2.mp4'
    #filename = '/Users/romainbrette/Movies/Videos paramecium LJP/Test_Bino_Zoom2.0_Fps12'
    #movie = MovieFolder(filename=filename,
    #                    fps=12., pixel_size=2.)
    movie = MovieFile(filename=filename)
    for image in movie.frames():
        print(movie.position)
